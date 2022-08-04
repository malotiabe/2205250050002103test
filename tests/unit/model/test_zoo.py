from promotheus.model.zoo import initialize_model, GBMRegressor
from sklearn.pipeline import Pipeline


def test_initialize_model_type():

    model_params = {'model': {'n_estimators': 3},
                    'encoder': {'cols': ['Flow']}}
    model = initialize_model(
        model_template=GBMRegressor,
        monotone_constraints=[],
        **model_params
    )
    assert isinstance(model, Pipeline)
