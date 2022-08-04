import mlflow
from numpy.testing import assert_allclose
from promotheus.model.monitor import serialization
from promotheus.model.train import train_one
from promotheus.model import zoo

# TODO: Revisit this test case, this is testing 3rd party code


def test_save_model_preserves_predict_behaviour_and_artifacts(
    load_training_data_output,
    sample_feature_columns,
    sample_categorical_columns,
    local_mlflow_experiment
):

    model_params = {'model': {},
                    'encoder': {'cols': sample_categorical_columns}}
    model = train_one(
        X=load_training_data_output[sample_feature_columns].tail(1000),
        y=load_training_data_output.SoldUnitsPromotion.tail(1000),
        modobj=zoo.initialize_model(
            model_template=zoo.GBMRegressor,
            monotone_constraints=[],
            **model_params
        ),
        fit_params={}
    )
    test_model_path = 'promotheus/test_resources/models/'
    artifacts = {
        'feature_columns': sample_feature_columns
    }
    test_run_id = local_mlflow_experiment
    serialization.save_model(
        model,
        run_id=test_run_id,
        artifacts=artifacts,
        blob_storage_model_path=test_model_path
    )
    reloaded_model, reloaded_artifacts = serialization.load_model(
        run_id=test_run_id,
        blob_storage_model_path=test_model_path
    )

    prediction_data = load_training_data_output[sample_feature_columns].head(
        1000)

    mlflow.end_run()  # Stops any hanging mlflow runs as a result of the active run started via local_mlflow_experiment

    assert artifacts == reloaded_artifacts
    assert_allclose(reloaded_model.predict(prediction_data),
                    model.predict(prediction_data))
