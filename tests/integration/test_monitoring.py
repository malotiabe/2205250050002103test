import datetime as dt
from itertools import tee
from sys import prefix
import unittest
import pandas as pd

from promotheus.utils.utils import measure_memory_time
from promotheus.monitoring.run_populate_predictions import main as pop_main
from promotheus.monitoring.run_compute_metrics import main as precompute_main
from promotheus.configuration import get_config
from tests.integration.fixtures import monitoring_preds, data_quality, metrics

_config = get_config()
BLOB_ACCOUNT = _config.blobstore
BLOB_CONTAINER = BLOB_ACCOUNT.get_container_client('artifacts')
BASE_INPUT_DIR = 'promotheus/test_resources/monitoring'


class MonitoringTest(unittest.TestCase):

    TEST_DIR = None

    def setUp(self) -> None:
        super().setUp()
        print('Running general test setUp.')
        time_of_test = dt.datetime.now()
        self.TEST_DIR = f'{BASE_INPUT_DIR}/{time_of_test.strftime("%Y%m%d%H%M%S")}'
        print('Test directory is: ', self.TEST_DIR)
    

    def tearDown(self) -> None:
        super().tearDown()
        print('Tearing down test.')
        test_blobs = BLOB_CONTAINER.list_blobs(name_starts_with=self.TEST_DIR)
        for blob in test_blobs:
            print('Deleting blob: ', blob.name)
            BLOB_CONTAINER.delete_blob(blob.name) 


    def populate_predictions_setup(self):
        print('Getting dates for populate_predictions test.')
        first_date, last_date = pd.to_datetime('20210221'), pd.to_datetime('20210222')
        date_range = pd.date_range(first_date, last_date)
        return first_date, last_date, date_range


    @measure_memory_time
    def pop_main2(self, **kwargs):
        return pop_main(**kwargs)


    def test_run_populate_predictions(self):
        print('Testing populate_predictions.')
        first_date, last_date, date_range = self.populate_predictions_setup()

        self.pop_main2(
            first_date=first_date,
            last_date=last_date,
            path_base_forecast='promotheus/forecasts',
            path_template_output=self.TEST_DIR + '/input_date/promo_products_{:%Y%m%d}.parquet',
        )

        for date in date_range:
            blob_path = f'{self.TEST_DIR}/input_date/promo_products_{date:%Y%m%d}.parquet'
            assert BLOB_ACCOUNT.check_blob_exists(blob_path)

        df = BLOB_ACCOUNT.load_data(
            name=f'{self.TEST_DIR}/input_date/promo_products_{last_date:%Y%m%d}.parquet',
            container=BLOB_CONTAINER
        )

        missing_cols = set(monitoring_preds) - set(df.columns.values)
        extra_cols = set(df.columns.values) - set(monitoring_preds)

        assert len(missing_cols) == 0, 'Expected cols missing. ' + str(missing_cols)
        assert len(extra_cols) == 0, 'Extra unxpected cols observed. ' + str(extra_cols)


    def compute_metrics_setup(self):
        print('Getting dates and columns for compute_metrics test.')
        first_date, last_date = pd.to_datetime('20210215'), pd.to_datetime('20210216')  # first date must be Monday
        all_date_str = [f'{x:%Y%m%d}' for x in pd.date_range(first_date, last_date)]

        daily_filepaths_columns = [
            [
                (f'{self.TEST_DIR}/data_quality/daily/data_quality_{x}.parquet', data_quality),
                (f'{self.TEST_DIR}/online_model_metrics/daily/online_model_metrics_{x}.parquet', metrics),
                (f'{self.TEST_DIR}/product_metrics/daily/product_metrics_{x}.parquet', metrics),
            ] for x in all_date_str]
        daily_filepaths_columns = [item for sublist in daily_filepaths_columns for item in sublist]
        weekly_filepaths_columns = [
            [
                (
                    f'{self.TEST_DIR}/data_quality/week_to_date/' +
                    f'{all_date_str[0]}/data_quality_{all_date_str[0]}_{x}.parquet',
                    data_quality
                ),
                (
                    f'{self.TEST_DIR}/online_model_metrics/week_to_date/' +
                    f'{all_date_str[0]}/online_model_metrics_{all_date_str[0]}_{x}.parquet',
                    metrics
                ),
                (
                    f'{self.TEST_DIR}/product_metrics/week_to_date/' +
                    f'{all_date_str[0]}/product_metrics_{all_date_str[0]}_{x}.parquet',
                    metrics
                ),
            ] for x in all_date_str]
        weekly_filepaths_columns = [item for sublist in weekly_filepaths_columns for item in sublist]

        for path, cols in daily_filepaths_columns + weekly_filepaths_columns:
            if BLOB_ACCOUNT.check_blob_exists(path):
                BLOB_CONTAINER.delete_blob(path)

        return first_date, last_date, daily_filepaths_columns + weekly_filepaths_columns


    @measure_memory_time
    def precompute_main2(self, **kwargs):
        return precompute_main(**kwargs)


    def test_run_compute_metrics(self):
        print('Testing compute metrics.')
        first_date, last_date, filepaths_and_columns = self.compute_metrics_setup()

        self.precompute_main2(
            first_date=first_date,
            last_date=last_date,
            path_date_input=f'{BASE_INPUT_DIR}/input_date',
            path_monitoring_output=self.TEST_DIR,
            groupby_vars_to_report=[
                ['ParentWarehouse', 'BuyingDivisionDescription'],
            ]
        )

        for path, expected_cols in filepaths_and_columns:

            obs_cols = BLOB_ACCOUNT.load_data(path).columns.values
            missing_cols = set(expected_cols) - set(obs_cols)
            extra_cols = set(obs_cols) - set(expected_cols)

            assert len(missing_cols) == 0, f'[{path}] Missing cols: ' + str(missing_cols)
            assert len(extra_cols) == 0, f'[{path}] Extra cols: ' + str(extra_cols)
