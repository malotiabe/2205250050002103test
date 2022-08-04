import datetime as dt
import pandas as pd
import unittest
from unittest.mock import patch

from promotheus.utils.utils import measure_memory_time
from promotheus.configuration import get_config
from promotheus.model.monitor.registry_utils import _get_run_id
from pipeline.run_forecast_optimize import main as forecast_optimize
from tests.integration.fixtures import test_experiments


_config = get_config()
BLOB_ACCOUNT = _config.blobstore
BLOB_CONTAINER = BLOB_ACCOUNT.get_container_client('artifacts')
BASE_OUTPUT_DIR = 'promotheus/test_resources/forecasts'


class ForecastOptimizeTest(unittest.TestCase):

    TEST_DIR = None

    def setUp(self) -> None:
        super().setUp()
        print('Running general test setUp.')
        time_of_test = dt.datetime.now()
        self.TEST_DIR = f'{BASE_OUTPUT_DIR}/{time_of_test.strftime("%Y%m%d%H%M%S")}'
        print('Test directory is: ', self.TEST_DIR)
    

    def tearDown(self) -> None:
        super().tearDown()
        print('Tearing down test.')
        test_blobs = BLOB_CONTAINER.list_blobs(name_starts_with=self.TEST_DIR)
        for blob in test_blobs:
            print('Deleting blob: ', blob.name)
            BLOB_CONTAINER.delete_blob(blob.name) 


    @measure_memory_time
    def forecast_optimize2(self, **kwargs):
        return forecast_optimize(**kwargs)


    # Requires a model in Promotheus-serve-test to be in the Production stage (this is a manual transition by design)
    @patch('pipeline.run_forecast_optimize.get_experiment_config')
    def test_forecast_optimize(self, mock_experiment):
        print('Testing forecast optimize.')
        mock_experiment.return_value = test_experiments['serve']

        self.forecast_optimize2(
            recommend_for_date=pd.to_datetime('20210809'),
            minutes_in_promo=10080,
            overwrite_predictions=True,
            depths_range_predict=[0.1, 0.2],
            blob_directory_features='promotheus/processed_features/serve',
            blob_directory_output=self.TEST_DIR,
            blob_input_features_account=BLOB_ACCOUNT,
            blob_input_model_account=BLOB_ACCOUNT,
            blob_output_account=BLOB_ACCOUNT,
        )
