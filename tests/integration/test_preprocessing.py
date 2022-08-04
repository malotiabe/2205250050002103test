import datetime as dt 
import unittest
import pandas as pd

from promotheus.configuration import get_config
from promotheus.utils.utils import measure_memory_time
from pipeline.run_preprocessing import main as preproc_main
from tests.integration.fixtures import preproc_train_columns, preproc_serve_columns

_config = get_config()

BLOB_ACCOUNT = _config.blobstore
BLOB_CONTAINER = BLOB_ACCOUNT.get_container_client('artifacts')
BASE_DIR = 'promotheus/test_resources/processed_features'
TARGET_DATE = pd.to_datetime('20210802')

class PreprocessingTest(unittest.TestCase):

    TEST_DIR = None

    def setUp(self) -> None:
        super().setUp()
        print('Running general test setUp.')
        time_of_test = dt.datetime.now()
        self.TEST_DIR = f'{BASE_DIR}/{time_of_test.strftime("%Y%m%d%H%M%S")}'
        print('Test directory is: ', self.TEST_DIR)
    

    def tearDown(self) -> None:
        super().tearDown()
        print('Tearing down test.')
        test_blobs = BLOB_CONTAINER.list_blobs(name_starts_with=self.TEST_DIR)
        for blob in test_blobs:
            print('Deleting blob: ', blob.name)
            BLOB_CONTAINER.delete_blob(blob.name) 


    @measure_memory_time
    def preproc_main2(self, **kwargs):
        return preproc_main(**kwargs)


    def _get_diff_in_cols(self, expected, observed):
        return list(set(expected) - set(observed)), list(set(observed) - set(expected))

    
    def get_target_path(self, is_prep_for_serving: bool) -> str:
        prefix = 'serve' if is_prep_for_serving else 'train'
        return f'{self.TEST_DIR}/{prefix}/{prefix}_{TARGET_DATE:%Y%m%d}.parquet'


    def test_run_preprocessing_train(self):
        print('Testing run preprocessing train.')
        target_blob_path = self.get_target_path(is_prep_for_serving=False)
        self.preproc_main2(
            last_week_start_date=TARGET_DATE,
            first_week_start_date=TARGET_DATE,
            is_prep_for_serving=False,
            blob_output_directory=self.TEST_DIR,
            overwrite=True
        )
        output = BLOB_ACCOUNT.load_data(target_blob_path)

        exp_m_ob, ob_m_exp = self._get_diff_in_cols(preproc_train_columns, output.columns.values)

        for cols, message in [
            (exp_m_ob, 'Some expected cols are missing. '),
            (ob_m_exp, 'Some observed cols are unexpected. '),
        ]:
            assert len(cols) == 0, message + str(cols)


    def test_run_preprocessing_serve(self):
        print('Testing run preprocessing serve.')
        target_blob_path = self.get_target_path(is_prep_for_serving=True)
        self.preproc_main2(
            last_week_start_date=TARGET_DATE,
            first_week_start_date=TARGET_DATE,
            is_prep_for_serving=True,
            blob_output_directory=self.TEST_DIR,
            overwrite=True
        )
        output = BLOB_ACCOUNT.load_data(target_blob_path)
        exp_m_ob, ob_m_exp = self._get_diff_in_cols(preproc_serve_columns, output.columns.values)

        for cols, message in [
            (exp_m_ob, 'Some expected cols are missing. '),
            (ob_m_exp, 'Some observed cols are unexpected. '),
        ]:
            assert len(cols) == 0, message + str(cols)
