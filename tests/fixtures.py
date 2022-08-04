import pytest
import pandas as pd
import mlflow

from pipeline.run_train import load_training_data

test_start_date = pd.datetime(2018, 1, 1)
test_end_date = test_start_date + pd.Timedelta(weeks=2)

_load_training_data_output = None
_local_mlflow_tests_uri = 'mlruns/tests'


def _get_load_training_data_output():
    global _load_training_data_output
    if _load_training_data_output is None:
        _load_training_data_output = load_training_data(
            start_date=test_start_date,
            end_date=test_end_date,
            blob_input_dir='promotheus/processed_features/train',
            prefix='train',
            filter_recipe=None,
            add_recipe=None,
        )
    return _load_training_data_output


@pytest.fixture
def load_training_data_output():
    return _get_load_training_data_output()


@pytest.fixture()
def sample_feature_columns():
    return ['MostRecentFullPrice', 'UnitCostPrice', 'SoldUnitsPromotion']


@pytest.fixture()
def sample_categorical_columns():
    return []


# TODO: Determine if it's better to use this when running tests in parallel
@pytest.fixture(scope='function')
def local_mlflow_experiment() -> str:
    import os
    key = 'MLFLOW_TRACKING_URI'
    restore = os.environ[key] if key in os.environ else None
    os.environ[key] = _local_mlflow_tests_uri

    with mlflow.start_run() as active_run:
        yield active_run.info.run_id

    if restore:
        os.environ[key] = restore
    else:
        os.unsetenv(key)
