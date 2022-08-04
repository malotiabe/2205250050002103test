import datetime as dt 
import mlflow
from mlflow.exceptions import RestException
import pandas as pd
import unittest
from unittest.mock import patch

from promotheus.configuration import get_config
from promotheus.utils.utils import measure_memory_time
from pipeline.run_train import main as train_main
from tests.integration.fixtures import test_experiments, train_model_config

_config = get_config()

BLOB_ACCOUNT = _config.blobstore
BLOB_CONTAINER = BLOB_ACCOUNT.get_container_client('artifacts')
END_DATE = pd.to_datetime('20210215')
BASE_INPUT_DIR = 'promotheus/test_resources/models'


class ModelTrainingTest(unittest.TestCase):

    TEST_DIR = None

    def setUp(self) -> None:
        super().setUp()
        print('Running general test setUp.')
        self.train_model_test_config = train_model_config()
        time_of_test = dt.datetime.now()
        self.TEST_DIR = f'{BASE_INPUT_DIR}/{time_of_test.strftime("%Y%m%d%H%M%S")}'
        print('Test directory is: ', self.TEST_DIR)
    

    def tearDown(self) -> None:
        super().tearDown()
        print('Tearing down test.')
        mlflow.end_run()  # Stop any hanging mlflow runs as a result of training pipeline
        test_blobs = BLOB_CONTAINER.list_blobs(name_starts_with=self.TEST_DIR)
        for blob in test_blobs:
            print('Deleting blob: ', blob.name)
            BLOB_CONTAINER.delete_blob(blob.name) 


    @measure_memory_time
    def train_main2(self, **kwargs):
        return train_main(**kwargs)


    @patch('pipeline.run_train.get_experiment_config')
    def test_train_main_score(self, mock_experiment):
        print('Testing model training - score.')
        model_usage = 'score'
        mock_experiment.return_value = test_experiments[model_usage]

        mod, met, run_id = self.train_main2(
            model_usage=model_usage,
            end_date=END_DATE,
            model_config=self.train_model_test_config['model'],
            training_data_config=self.train_model_test_config['data'],
            validation_config=self.train_model_test_config['validation'],
            n_weeks_padding=0,
            blob_output_dir=self.TEST_DIR
        )

        try:
            model = mlflow.sklearn.load_model(model_uri=f"runs:/{run_id}/model")
        except RestException as e:
            assert False, f"Model not properly registered to mlflow: {e}"

        assert BLOB_ACCOUNT.check_blob_exists(f'{self.TEST_DIR}/{run_id}/artifacts/feature_columns.pkl')
        assert BLOB_ACCOUNT.check_blob_exists(f'{self.TEST_DIR}/{run_id}/artifacts/metrics.pkl')
        assert BLOB_ACCOUNT.check_blob_exists(f'{self.TEST_DIR}/{run_id}/artifacts/usage.pkl')
        assert BLOB_ACCOUNT.check_blob_exists(f'{self.TEST_DIR}/{run_id}/model/conda.yaml')
        assert BLOB_ACCOUNT.check_blob_exists(f'{self.TEST_DIR}/{run_id}/model/model.pkl')
        assert BLOB_ACCOUNT.check_blob_exists(f'{self.TEST_DIR}/{run_id}/model/MLmodel')


    @patch('pipeline.run_train.get_experiment_config')
    def test_train_main_serve(self, mock_experiment):
        print('Testing model training - serve.')
        model_usage = 'serve'
        mock_experiment.return_value = test_experiments[model_usage]

        mod, met, run_id = self.train_main2(
            model_usage=model_usage,
            end_date=END_DATE,
            model_config=self.train_model_test_config['model'],
            training_data_config=self.train_model_test_config['data'],
            validation_config=self.train_model_test_config['validation'],
            n_weeks_padding=0,
            blob_output_dir=self.TEST_DIR
        )

        try:
            model = mlflow.sklearn.load_model(model_uri=f"runs:/{run_id}/model")
        except RestException as e:
            assert False, f"Model not properly registered to mlflow: {e}"

        assert BLOB_ACCOUNT.check_blob_exists(f'{self.TEST_DIR}/{run_id}/artifacts/feature_columns.pkl')
        assert BLOB_ACCOUNT.check_blob_exists(f'{self.TEST_DIR}/{run_id}/artifacts/usage.pkl')
        assert BLOB_ACCOUNT.check_blob_exists(f'{self.TEST_DIR}/{run_id}/model/conda.yaml')
        assert BLOB_ACCOUNT.check_blob_exists(f'{self.TEST_DIR}/{run_id}/model/model.pkl')
        assert BLOB_ACCOUNT.check_blob_exists(f'{self.TEST_DIR}/{run_id}/model/MLmodel')
