import pandas as pd
import numpy as np
from sklearn.linear_model import ElasticNetCV
from promotheus.model import design_matrix as dm
from promotheus.model import custom_estimators as ce


def test_RegressionAutoCategorical_fits_and_predicts_correct(load_training_data_output):

    df = load_training_data_output.reset_index(drop=True)

    encoder_kwargs = {
        'cardinality_max_before_hash': 5,
        'hash_n_dimensions': 3,
    }
    _cat = ['ParentWarehouse', 'BuyingDivisionDescription', 'GroupDescription', 'SeasonalEvent', 'Range', ]
    _cont = ['MinutesInPriceStatusPromotion', 'MostRecentFullPrice', 'SoldUnitsPrevWeek1', 'SoldUnitsPrevWeek2', ]

    # Generate predictions via the custom estimator
    model_params = {
        'encoder': {
            'continuous_features': _cont,
            'categorical_features': _cat,
            'categorical_encoder_kwargs': encoder_kwargs
        },
    }
    reg = ce.RegressionAutoCategorical(estimator=ElasticNetCV, **model_params)
    reg.fit(
        X=df[_cont + _cat],
        y=df.SoldUnitsPromotion
    )
    yhat = reg.predict(df[_cont + _cat])

    # Generate predictions separately from scratch
    x_cat = dm.CategoricalAutoEncoder(
        feature_frame_column_names=_cat,
        **model_params['encoder']['categorical_encoder_kwargs']
    ).fit_transform(df)
    x_cont = dm.FeatureSelector(columns=_cont).fit_transform(df)
    x = pd.concat([x_cat, x_cont], axis=1)

    # Fit model
    mod = ElasticNetCV().fit(X=x, y=df.SoldUnitsPromotion)
    yhat2 = mod.predict(x)

    np.testing.assert_array_almost_equal(yhat, yhat2, decimal=4)
