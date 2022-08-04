import copy
import datetime
import unittest
import pandas as pd

import asos.ai.retsci.services.storage.blob as retsciblob

from promotheus.configuration import get_config
from pipeline.run_ithax import get_all_products, prepare_product_data_for_search, set_depths_for_changeable_inclusions
from promotheus.ithax.parse_retail_input import read_in_excel
from promotheus.ithax import utils as iutils
from promotheus.ithax.ithax import run_algorithm_v2, run_calculator_v2
from promotheus.definitions import ithax_info


_config = get_config()

BLOB_ACCOUNT = _config.blobstore
FILESHARE_ACCOUNT = _config.fileshare


# TODO IMPORTANT: Usually, the tests are set to (a) have the first test (test_run_calculator_hits_batchwise_targets)
# write materials from scratch (pulling from prod storage) (b) have all subsequent tests use these (saved) materials,
# in order to save time (pulling + preprocessing the dfs is costly).
#
# The create-from-scratch has been disabled until the merch update (spring '22) changes are complete (DS8985). After
# that, we need to re-enable create-from-scratch so that dfs are freshly written at least ONCE in test suite (DS9063)

TARGET_DATE_FOR_TESTS = pd.to_datetime('20220314')
EXCEL_INPUT_TEMPLATE = 'product_selection_input/{0:%Y%m%d}/targets_inclusions_exclusions_B_{0:%Y%m%d}.xlsx'
RAND_SEED = 42

option_ids_for_exclusion_by_fc = {
    pd.to_datetime('20220110'): pd.DataFrame(data={"ProductOptionCode": ['101245121', '101238398',
                                                                         '113464763', '109443603', '100943206'],
                                                   "ParentWarehouse":  ['FC03 Atlanta', 'FC03 Atlanta',
                                                                        'FC01 Barnsley', 'FC04 Berlin',
                                                                        'FC01 Barnsley']
                                                   }),
    pd.to_datetime('20220314'): pd.DataFrame([
                                            ('101337000', 'FC01 Barnsley'),
                                            ('101209206', 'FC03 Atlanta'),
                                            ('100788546', 'FC04 Berlin'),
    ], columns=["ProductOptionCode", "ParentWarehouse"])
}


class IthaxTests(unittest.TestCase):
        
    def ithax_inputs(
        self,
        recommend_for_date: datetime.datetime,
        force_write_new: bool = True,
        load_retail_input_from_prod: bool = False
):
        '''
        When constructing test case, make sure the specific input dfs + StockVals trigger all the paths within
        run_algorithm and run_calculator. This test case (=this specific week, with specific retail targets) covers the
        following key paths:

            - ithax undershoot and overshoot are both triggered
            - multiple ithax iterations
            - run_calculator hits the lowest cover group
        '''

        def _get_large_dfs(
            recommend_for_date, read_in_data, force_write_new,
            filepath_inclusions, filepath_candidates,
        ):
            if (
                force_write_new or
                (not all([
                    BLOB_ACCOUNT.check_blob_exists(x)
                    for x in [filepath_inclusions, filepath_candidates]
                ]))
            ):
                df_inclusions, df_candidates, _ = prepare_product_data_for_search(
                    get_all_products(recommend_for_date),
                    read_in_data["inclusions"], read_in_data["filters"], read_in_data["reference_tables_dict"]
                )
                df_inclusions = set_depths_for_changeable_inclusions(recommend_for_date, df_inclusions)
                retsciblob.store_data(df_inclusions, name=filepath_inclusions,
                                    container='artifacts', account=BLOB_ACCOUNT)
                retsciblob.store_data(df_candidates, name=filepath_candidates,
                                    container='artifacts', account=BLOB_ACCOUNT)
            else:
                df_inclusions = retsciblob.load_data(filepath_inclusions,
                                                    container='artifacts', account=BLOB_ACCOUNT)
                df_candidates = retsciblob.load_data(filepath_candidates,
                                                    container='artifacts', account=BLOB_ACCOUNT)

            return df_inclusions, df_candidates

        def BatchStockVal(df, batch_name): return iutils.report_financial_metrics(
            iutils.get_data_by_batch_name(df, batch_name)).StockValueGBP

        # Load retail input
        read_in_data = read_in_excel(
            EXCEL_INPUT_TEMPLATE.format(recommend_for_date),
            fileshare_account=FILESHARE_ACCOUNT)

        # Load dataframe inputs
        df_inclusions, df_candidates = _get_large_dfs(
            recommend_for_date, read_in_data, force_write_new,
            f'promotheus/test_resources/ithax/df_inclusions_{recommend_for_date:%Y%m%d}.parquet',
            f'promotheus/test_resources/ithax/df_candidates_{recommend_for_date:%Y%m%d}.parquet',
        )

        # Batchwise StockValue targets (adjusted for Inclusions)
        target_depth, target_stock_val = read_in_data['targets']['StockDepth'], read_in_data['targets']['StockValues']
        allocatable_stock_val = copy.deepcopy(target_stock_val)
        for batch_name in ithax_info['stock_value_batches']['batch_names']:
            allocatable_stock_val[batch_name] = allocatable_stock_val[batch_name] - \
                BatchStockVal(df_inclusions,  batch_name)

        reference_tables = read_in_data["reference_tables_dict"]
        highest_bands = {
            batch: iutils.get_id_of_highest_band(table)
            for batch, table in reference_tables.items()
        }

        return (df_inclusions, df_candidates, allocatable_stock_val, target_stock_val, target_depth,
                highest_bands, reference_tables)


    def test_run_calculator_hits_batchwise_targets(
        self,
        recommend_for_date=TARGET_DATE_FOR_TESTS,
        force_write_new=True
    ):
        print('Testing Ithax run calculator hits batchwise targets.')
        (df_inclusions, df_candidates,
        allocatable_stock_val, target_stock_val, target_depth, highest_bands, _) = self.ithax_inputs(
            # Changeable Inclusions are dropped for this test, as their depths are populated upstream
            recommend_for_date=recommend_for_date,  force_write_new=force_write_new,
            # drop_changeable_inclusions=True
        )
        df_inclusions2 = df_inclusions.copy()

        df_out, _ = run_calculator_v2(
            df_inclusions=df_inclusions,
            df_candidates=df_candidates,
            allocatable_stock_values2=allocatable_stock_val,
            highest_band_dict=highest_bands,
            rand_seed=RAND_SEED
        )
        stock_depth = iutils.report_financial_metrics(df_out).StockDepth

        # Evaluate results
        report = iutils.report_ithax_hits_targets(
            df_out,
            target_stock_values=target_stock_val,
            target_stock_depth=target_depth,
            cast_stockval_in_millions=False,
            cast_pct_as_pct=True,
        )

        # Assemble test battery
        grain_inclusions = [
            'productId', 'ParentWarehouse', 'IthaxDepth',
        ]
        battery = pd.concat([
            pd.Series({
                'name': 'run_calculator hits AllocatableStockValueGBP for all batches',
                'status': all((report.loc[:, 'Hit_StockValueGBP'] == True).values),
            }),
            pd.Series({
                'name': 'Fixed Inclusions are all present, marked as fixed inclusions, and have depths unchanged',
                'status': (
                    df_inclusions2
                    .query('Source == "Inclusions Fixed"')
                    [grain_inclusions]
                    .sort_values(grain_inclusions)
                    .reset_index(drop=True)
                    .equals(
                        df_out
                        .query('Source == "Inclusions Fixed"')
                        [grain_inclusions]
                        .sort_values(grain_inclusions)
                        .reset_index(drop=True)
                    )
                ),
            }),
            pd.Series({
                'name': 'Target StockValue exceeded for some batches!',
                'status':  (report.StockValueGBP <= report.Target_StockValueGBP).mean() == 1
            }),
            pd.Series({
                'name': 'StockDepth output is the correct StockDepth',
                'status': (
                    (stock_depth > 0) and (stock_depth < 1) and
                    (stock_depth == iutils.report_financial_metrics(df_out).StockDepth)
                )
            }),
        ], axis=1).T
        assert all(battery.status.values), 'Some battery tests are failing. Battery status: ' + str(battery)

        return report


    def test_run_algorithm_hits_all_targets_for_realistic_promo(
        self,
        recommend_for_date=TARGET_DATE_FOR_TESTS,
        force_write_new=False
    ):
        print('Testing Ithax run algorithm hits all targets for realistic promo.')

        df_inclusions, df_candidates, _, target_stock_val, target_depth, _, reference_tables = self.ithax_inputs(
            recommend_for_date=recommend_for_date,  force_write_new=force_write_new)
        df_inclusions2 = df_inclusions.copy()

        df_out, boundaries_dict, _, _ = run_algorithm_v2(
            df_inclusions=df_inclusions,
            df_candidates=df_candidates,
            reference_tables=reference_tables,
            target_stock_values=target_stock_val,
            target_stock_depth=target_depth,
            rand_seed=RAND_SEED
        )
        results = iutils.report_ithax_hits_targets(
            df_out,
            target_stock_values=target_stock_val,
            target_stock_depth=target_depth
        )

        # Battery of tests
        grain_inclusions = ['productId', 'ParentWarehouse', ]
        df_inclusions2, df_candidates2, _, target_stock_val2, target_depth2, _, _ = self.ithax_inputs(
            recommend_for_date=recommend_for_date,  force_write_new=force_write_new)
        df_exclusions_by_fc = option_ids_for_exclusion_by_fc[recommend_for_date]
        battery = pd.concat([
            pd.Series({
                'name': 'run_algorithm hits Target StockValueGBP for all batches, and overall',
                'status': all(results.Hit_StockValueGBP.values)
            }),
            pd.Series({
                'name': 'run_algorithm hits Target StockDepth, overall',
                'status': results.loc['Overall', 'Hit_StockDepth']
            }),
            pd.Series({
                'name': 'All rows have valid depths',
                'status': (
                    (df_out.IthaxDepth.isnull().mean() == 0) and
                    (
                        ((df_out.IthaxDepth > 0).mean() == 1) and
                        ((df_out.IthaxDepth < 1).mean() == 1)
                    )
                )}),
            pd.Series({
                'name': 'Target and inclusion data have not been accidentally changed (should be immutable dtypes)',
                'status': (
                    df_inclusions.equals(df_inclusions2) and
                    (target_stock_val == target_stock_val2) and
                    (target_depth == target_depth2)
                )
            }),
            pd.Series({
                'name': 'Fixed Inclusions are all present, marked as fixed inclusions, and have depths unchanged',
                'status': (
                    df_inclusions2
                    .query('Source == "Inclusions Fixed"')
                    [grain_inclusions]
                    .sort_values(grain_inclusions)
                    .reset_index(drop=True)
                    .equals(
                        df_out
                        .query('Source == "Inclusions Fixed"')
                        [grain_inclusions]
                        .sort_values(grain_inclusions)
                        .reset_index(drop=True)
                    )
                ),
            }),
            pd.Series({
                'name': 'Changeable Inclusions are all present, marked as inclusions',
                'status': (
                    df_inclusions2
                    .query('Source == "Inclusions Fixed"')
                    [grain_inclusions]
                    .sort_values(grain_inclusions)
                    .reset_index(drop=True)
                    .equals(
                        df_out
                        .query('Source == "Inclusions Fixed"')
                        [grain_inclusions]
                        .sort_values(grain_inclusions)
                        .reset_index(drop=True)
                    )
                ),
            }),

            pd.Series({
                'name': 'All boundaries are positive',
                'status': all([
                        all([x > 0 for x in boundaries[1:]])
                        for batch, boundaries in boundaries_dict.items()
                ])
            }),
            pd.Series({
                'name': 'Exclusions By FC are removed',
                'status':  len(pd.merge(df_candidates2, df_exclusions_by_fc,
                                        right_on=["ProductOptionCode", "ParentWarehouse"],
                                        left_on=["ProductOptionCode", "ParentWarehouse"])) == 0
            }),
            pd.Series({
                'name': 'All products that contribute to StockValue have depths >0',
                'status': (df_out.IthaxDepth > 0).mean() == 1
            }),
            pd.Series({
                'name': 'The minimum weeks on site is 2 + 1',
                'status': min(df_out.WeeksOnSite) >= 3
            }),
            pd.Series({
                'name': 'There are no products recommended which had any minutes in either normal or promotional clearance',
                'status': (
                        (sum(df_out[~df_out.Source.isin(ithax_info["INCLUSIONS_SOURCE_LABELS"])]
                            .MinutesInPriceStatusClearancePrevWeek2) +
                        sum(df_out[~df_out.Source.isin(ithax_info["INCLUSIONS_SOURCE_LABELS"])]
                        .MinutesInPriceStatusPromotionalClearancePrevWeek2))
                    == 0
                )
            }),
        ], axis=1).T
        assert all(battery.status.values), 'Some battery tests are failing. Battery status: ' + str(battery)


    def test_run_algorithm_works_with_undershoot_intermediary(
        self,
        recommend_for_date=TARGET_DATE_FOR_TESTS,
        force_write_new=False
    ):
        '''
        This is a test to check ithax triggers the undershoot in a way that it can "bounce back" after overshooting too
        far in stock depth. When significantly changing ithax filters / logic, do review the specific arbitrary values below,
        constructing targets/tolerance such that (a) the algorithm overshoots initially (b) the undershoot is triggered later
        on (c) the algorithm does finally converge
        '''
        
        print('Testing Ithax run algorithm works with undershoot intermediary.')
        df_inclusions, df_candidates, _, target_stock_val, _, _, reference_tables = self.ithax_inputs(
            recommend_for_date=recommend_for_date, force_write_new=force_write_new)

        # Contrived depth and tolerance to force Undershoot by increasing the size of the final boundaries
        df_inclusions = df_inclusions[df_inclusions.IthaxDepth.isin([0.1, 0.15, 0.2, 0.25])]
        target_depth = 0.26
        tolerance = 0.001

        df_out, boundaries_dict, _, _ = run_algorithm_v2(
            df_inclusions=df_inclusions,
            df_candidates=df_candidates,
            reference_tables=reference_tables,
            target_stock_values=target_stock_val,
            target_stock_depth=target_depth,
            rand_seed=RAND_SEED,
            tolerance=tolerance
        )
        results = iutils.report_ithax_hits_targets(
            df_out,
            target_stock_values=target_stock_val,
            target_stock_depth=target_depth
        )

        battery = pd.concat([
            pd.Series({
                'name': 'run_algorithm hits Target StockValueGBP for all batches, and overall',
                'status': all(results.Hit_StockValueGBP.values)
            }),
            pd.Series({
                # This test is different because in the results calculation we use a
                # percentage discrepancy instead of an absolute discrepency
                'name': 'run_algorithm Hits the stock depth within the tolerance required',
                'status': abs(results[results.index == "Overall"]["StockDepth"][0] - target_depth) <= tolerance
            }),
            pd.Series({
                'name': 'run_algorithm hits Target StockDepth, overall',
                'status': results.loc['Overall', 'Hit_StockDepth']
            }),
            pd.Series({
                'name': 'All boundaries are positive',
                'status': all([
                        all([x > 0 for x in boundaries[1:]])
                        for batch, boundaries in boundaries_dict.items()
                ])
            }),
            pd.Series({
                'name': 'All products that contribute to StockValue have depths >0',
                'status': (df_out.IthaxDepth > 0).mean() == 1
            }),
        ], axis=1).T
        assert all(battery.status.values), 'Some battery tests are failing. Battery status: ' + str(battery)


    def test_run_algorithm_works_with_undershoot_final(
        self,
        recommend_for_date=TARGET_DATE_FOR_TESTS,
        force_write_new=False
    ):
        '''
        This is a test to check ithax triggers the undershoot in a way that it can "bounce back" after overshooting too
        far in stock depth. When significantly changing ithax filters / logic, do review the specific arbitrary values below,
        constructing targets/tolerance such that: (a) the algorithm undershoots just before convergence (b) the algorithm does converge
        '''

        print('Testing Ithax run algorithm works with undershoot final.')
        df_inclusions, df_candidates, _, target_stock_val, _, _, reference_tables = self.ithax_inputs(
            recommend_for_date=recommend_for_date, force_write_new=force_write_new)

        # Contrived depth and tolerance to force Undershoot by increasing the size of the final boundaries
        df_inclusions = df_inclusions[df_inclusions.IthaxDepth.isin([0.1, 0.15, 0.2, 0.25])]
        target_depth = 0.28
        tolerance = 0.0075

        df_out, boundaries_dict, _, _ = run_algorithm_v2(
            df_inclusions=df_inclusions,
            df_candidates=df_candidates,
            reference_tables=reference_tables,
            target_stock_values=target_stock_val,
            target_stock_depth=target_depth,
            rand_seed=RAND_SEED,
            tolerance=tolerance
        )
        results = iutils.report_ithax_hits_targets(
            df_out,
            target_stock_values=target_stock_val,
            target_stock_depth=target_depth
        )

        battery = pd.concat([
            pd.Series({
                'name': 'run_algorithm hits Target StockValueGBP for all batches, and overall',
                'status': all(results.Hit_StockValueGBP.values)
            }),
            pd.Series({
                'name': 'run_algorithm hits Target StockDepth, overall',
                'status': results.loc['Overall', 'Hit_StockDepth']
            }),
            pd.Series({
                # This test is different because in the results calculation we use a
                # percentage discrepancy instead of an absolute discrepency
                'name': 'run_algorithm Hits the stock depth within the tolerance required',
                'status': abs(results[results.index == "Overall"]["StockDepth"][0] - target_depth) <= tolerance
            }),
            pd.Series({
                'name': 'All boundaries are positive',
                'status': all([
                        all([x > 0 for x in boundaries[1:]])
                        for batch, boundaries in boundaries_dict.items()
                ])
            }),
            pd.Series({
                'name': 'All products that contribute to StockValue have depths >0',
                'status': (df_out.IthaxDepth > 0).mean() == 1
            }),
        ], axis=1).T
        assert all(battery.status.values), 'Some battery tests are failing. Battery status: ' + str(battery)
