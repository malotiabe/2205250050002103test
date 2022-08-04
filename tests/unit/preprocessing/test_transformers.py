import pandas as pd
import numpy as np
import pytest

from promotheus.preprocessing.transformers import (
    Filters, GetFeatureFrame, populate_single_dataslice_with_forecasts, row_merge_closest_depth)


# Filters ------------------------------------------------------------------

def test_apply_filters_removes_expected_rows():

    df = pd.DataFrame({
        'a': [1, 2, 3],
        'b': [1, 2, 3]
    })

    out_df = Filters.apply_filters(
        df, filters=[lambda x: x[x['a'] <= 2]], kwarg_dicts=[None])
    expected_output = df[0:2]

    pd.testing.assert_frame_equal(out_df, expected_output)


def test_apply_filters_handles_empty_dataframe():

    df = pd.DataFrame({
        'a': [1, 2, 3],
        'b': [1, 2, 3]
    })

    out_df = Filters.apply_filters(
        df, filters=[lambda x: x[x['a'] < 1]], kwarg_dicts=[None])
    expected_output = pd.DataFrame({
        'a': [],
        'b': []
    }, dtype=int)

    pd.testing.assert_frame_equal(out_df, expected_output)


# Calculates ------------------------------------------------------------------

def test_calculate_pos_spend_is_the_calculation_correct():
    df_input = pd.DataFrame(data={
        'Warehouse': ['Barnsley', 'Barnsley', 'Germany',
                      'Germany', 'Atlanta', 'Atlanta'],
        'productId': [1, 2, 1, 2, 1, 3],
        'SoldUnitsPromotion': [3, 5, 0, 5, 1, 0],
        'MostRecentFullPrice': [10.00, 15.00, 8.00, 10.00, 15.00, 20.00],
        'DepthPromotion': [0.1, 0.2, 0.0, 0.3, 0.1, 0.0]
    })

    df_result = GetFeatureFrame.calculate_aggregate_pos_spend(
        df_in=df_input, groupby_key='Warehouse'
    )

    df_expected_result = pd.DataFrame(
        data={'Warehouse': ['Atlanta', 'Barnsley', 'Germany'],
              'POSSpend': [1.5, 18, 15]})

    df_result = df_result.sort_values('Warehouse')

    pd.testing.assert_frame_equal(df_result, df_expected_result)


def test_GetFeatureFrame_get_shifted_lag_columns_correct():

    df_in = pd.concat([
        pd.Series(['A', 'B', 'C', ]).rename('productId'),

        # Columns whose lag number should be adjusted
        pd.Series([1, 2, 3, ]).rename('VarA'),
        pd.Series([10, 20, 30, ]).rename('VarAPrevWeek1'),
        pd.Series([100, 200, 300, ]).rename('VarAPrevWeek2'),
        pd.Series([1000, 2000, 3000, ]).rename('VarAPrevWeek3'),
        pd.Series([10000, 20000, 30000, ]).rename('VarAPrevWeek4'),

        pd.Series([70, 80, 90, ]).rename('VarB'),
        pd.Series([70, 80, 90, ]).rename('VarBPrevWeek1'),
        pd.Series([700, 800, 900, ]).rename('VarBPrevWeek2'),
        pd.Series([7000, 8000, 9000, ]).rename('VarBPrevWeek3'),
        pd.Series([70000, 80000, 90000, ]).rename('VarAPrevWeek4'),

        # Columns that should disappear
        pd.Series([5, 5, 5, ]).rename('VarC'),
    ], axis=1)
    df_expected = pd.DataFrame({
        'productId': {0: 'A', 1: 'B', 2: 'C'},
        'VarAPrevWeek3': {0: 1, 1: 2, 2: 3},
        'VarAPrevWeek4': {0: 10, 1: 20, 2: 30},
        'VarBPrevWeek3': {0: 70, 1: 80, 2: 90},
        'VarBPrevWeek4': {0: 70, 1: 80, 2: 90}
    })

    df_out = GetFeatureFrame.get_shifted_lag_columns(
        df_lagged=df_in,
        n_weeks_shift=3,
        key_index=['productId']
    )
    pd.testing.assert_frame_equal(df_out, df_expected)


def test_GetFeatureFrame_calculate_retail_financials_correct_calculation():

    # Inputs
    sold_units = pd.Series([1, 2, 3, 4, 5])
    unit_full_price = pd.Series([5, 8, 12, 13, 15])
    depth = pd.Series([0.1, 0.2, 0.3, 0.25, 0.1])
    unit_cost_price = pd.Series([2, 1, 5, 8, 4])
    opening_stock_units = pd.Series([10]*5)
    warehouse = pd.Series(['Barnsley', 'Barnsley', 'Germany',
                           'Atlanta', 'Germany'])
    tax_rates = {'Barnsley': 1.2, 'Germany': 1.19, 'Atlanta': 1}
    conversion_rates = {'Barnsley': 1, 'Germany': 1.2, 'Atlanta': 1.4}

    met = [
        'CashMarginAbsoluteLocal', 'CashMarginAbsoluteGBP',
        'CashMarginLocalPctNumerator', 'CashMarginLocalPctDenominator',
        'SalesDepthComplementGBPNumerator', 'SalesDepthComplementGBPDenominator',
        'StockDepthComplementGBPNumerator', 'StockDepthComplementGBPDenominator',
    ]

    result = GetFeatureFrame.calculate_retail_financials(
        unit_full_price_local=unit_full_price,
        unit_cost_price_gbp=unit_cost_price,
        depth=depth,
        parent_warehouse=warehouse,
        sold_units=sold_units,
        opening_stock_units=opening_stock_units,
        metrics=met,
        tax_rates=tax_rates,
        conversion_rates=conversion_rates
    )
    expected_output = pd.DataFrame([
        [1.75,   1.75,   1.75,   3.75,   4.5,   5.,  45.,  50.],
        [8.67,   8.67,   8.67,  10.67,  12.8,  16.,  64.,  80.],
        [3.18,   2.65,   3.18,  21.18,  21.,  30.,  70., 100.],
        [-5.8,  -4.14,  -5.8,  39.,  27.86,  37.14,  69.64,  92.86],
        [32.72,  27.27,  32.72,  56.72,  56.25,  62.5, 112.5, 125.]
    ], columns=met)
    pd.testing.assert_frame_equal(result.round(2), expected_output)


def test_GetFeatureFrame_calculate_retail_financials_correct_output_index():
    common_index = [4, 5, 6, 7, 8]
    net_sales = pd.Series([1, 2, 3, 4, 5], index=common_index)
    full_price = pd.Series([2, 2, 2, 2, 2], index=common_index)
    depth = pd.Series([0, 0, 0, 0, 0], index=common_index)
    cost_price = pd.Series([1, 1, 1, 1, 1], index=common_index)
    warehouse = pd.Series(['A', 'A', 'A', 'A', 'A'], index=common_index)
    conversion_rates = {'A': 1}
    tax_rates = {'A': 1}

    output = GetFeatureFrame.calculate_retail_financials(
        sold_units=net_sales,
        unit_full_price_local=full_price,
        depth=depth,
        unit_cost_price_gbp=cost_price,
        parent_warehouse=warehouse,
        conversion_rates=conversion_rates,
        tax_rates=tax_rates,
        metrics=['CashMarginAbsoluteLocal']
    )
    expected_output = (
        pd.Series([1, 2, 3, 4, 5], dtype=float, index=common_index)
        .rename('CashMarginAbsoluteLocal')
    )
    pd.testing.assert_series_equal(
        output, expected_output, check_index_type='equiv')


def test_GetFeatureFrame_calculate_retail_financials_correct_output_for_unmatched_index():

    common_index = [2, 3, 4]
    net_sales = pd.Series([1, 2, 3], index=[1, 2, 3])
    full_price = pd.Series([2, 2, 2], index=common_index)
    depth = pd.Series([0, 0, 0], index=common_index)
    cost_price = pd.Series([1, 1, 1], index=common_index)
    warehouse = pd.Series(['A', 'A', 'A'], index=common_index)
    conversion_rates = {'A': 1}
    tax_rates = {'A': 1}

    output = GetFeatureFrame.calculate_retail_financials(
        sold_units=net_sales,
        unit_full_price_local=full_price,
        depth=depth,
        unit_cost_price_gbp=cost_price,
        parent_warehouse=warehouse,
        conversion_rates=conversion_rates,
        tax_rates=tax_rates,
        metrics=['CashMarginAbsoluteLocal']
    )

    expected_output = (
        pd.Series([np.nan, 2, 3, np.nan], dtype=float, index=[1, 2, 3, 4])
        .rename('CashMarginAbsoluteLocal')
    )
    pd.testing.assert_series_equal(
        output, expected_output, check_index_type='equiv')


def test_populate_single_dataslice_with_forecasts():

    def fallback_populator_constructor(allow_non_matches):
        return lambda df_slice, df_forecast: df_slice.apply(
            row_merge_closest_depth,
            df_forecast=df_forecast,
            col_row_depth='observed_price',
            col_forecast_depth='proposed_price',
            join_key=['key'],
            allow_non_matches=allow_non_matches, axis=1
        )

    df_slice, df_forecast = pd.DataFrame([
        ['A', 1, 'what'],
        ['B', 4, 'is'],   # Key present, no price match
        ['C', 3, 'up'],   # Key absent
    ], columns=['key', 'observed_price', 'info1']), \
        pd.DataFrame([
            ['A', 1, 'traffic'],
            ['A', 2, 'modern'],
            ['B', 1, 'getting'],
            ['B', 2, 'in'],
        ], columns=['key', 'proposed_price', 'info2'])

    # #1: Using fallback populator
    out = populate_single_dataslice_with_forecasts(
        df_slice, df_forecast,
        slice_join_on=['key', 'observed_price'],
        forecast_join_on=['key', 'proposed_price'],
        fallback_populator=fallback_populator_constructor(allow_non_matches=True),
        max_prop_missing_forecasts=0.7
    )
    expected = pd.DataFrame([
        ['A', 1, 'what', 1.0, 'traffic'],
        ['B', 4, 'is', 2.0, 'in'],
        ['C', 3, 'up', np.nan, np.nan]], columns=['key', 'observed_price', 'info1', 'proposed_price', 'info2'])
    pd.testing.assert_frame_equal(out, expected)

    # #2: No fallback populators
    out = populate_single_dataslice_with_forecasts(
        df_slice, df_forecast,
        slice_join_on=['key', 'observed_price'],
        forecast_join_on=['key', 'proposed_price'],
        fallback_populator=None,
        max_prop_missing_forecasts=0.7
    )
    expected = pd.DataFrame([
        ['A', 1, 'what', 1.0, 'traffic'],
        ['B', 4, 'is', np.nan, np.nan],
        ['C', 3, 'up', np.nan, np.nan]], columns=['key', 'observed_price', 'info1', 'proposed_price', 'info2'])
    pd.testing.assert_frame_equal(out, expected)

    # #3: Illegal key-mismatches
    with pytest.raises(ValueError):
        populate_single_dataslice_with_forecasts(
            df_slice, df_forecast,
            slice_join_on=['key', 'observed_price'],
            forecast_join_on=['key', 'proposed_price'],
            fallback_populator=fallback_populator_constructor(allow_non_matches=False),
            max_prop_missing_forecasts=0.7
        )
