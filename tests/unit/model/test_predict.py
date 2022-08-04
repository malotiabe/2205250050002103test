import pytest
import pandas as pd
import numpy as np

from promotheus.model.predict import predict_from_df
from promotheus.model.train import train_one
from promotheus.model import zoo


def test_predict_raises_error_for_invalid_arguments(
        load_training_data_output,
        sample_feature_columns,
        sample_categorical_columns
):

    model_params = {'model': {'n_estimators': 1},
                    'encoder': {'cols': sample_categorical_columns}}
    model = train_one(
        X=load_training_data_output[sample_feature_columns],
        y=load_training_data_output.SoldUnitsPromotion,
        modobj=zoo.initialize_model(
            model_template=zoo.GBMRegressor,
            monotone_constraints=[],
            **model_params
        ),
        fit_params={},
        tracked=False
    )

    with pytest.raises(ValueError):
        predict_from_df(
            model,
            df=load_training_data_output,
            feature_columns=sample_feature_columns,
            new_minutes_in_promo=8*24*60,
            new_depth=0.1
        )

    with pytest.raises(ValueError):
        predict_from_df(
            model,
            df=load_training_data_output,
            feature_columns=sample_feature_columns,
            new_minutes_in_promo=3*24*60,
            new_depth=1.1
        )


def test_predict_produces_correct_length_output(
        load_training_data_output,
        sample_feature_columns,
        sample_categorical_columns
):
    model_params = {'model': {'n_estimators': 1},
                    'encoder': {'cols': sample_categorical_columns}}
    model = train_one(
        X=load_training_data_output[sample_feature_columns],
        y=load_training_data_output.SoldUnitsPromotion,
        modobj=zoo.initialize_model(
            model_template=zoo.GBMRegressor,
            monotone_constraints=[],
            **model_params
        ),
        fit_params={},
        tracked=False
    )
    preds = predict_from_df(
        model,
        df=load_training_data_output,
        feature_columns=sample_feature_columns,
        new_minutes_in_promo=3*24*60,
        new_depth=0.1
    )

    assert len(load_training_data_output) == len(preds)


def test_predict_correct_index_output():

    index = [2, 3, 4]

    dummy_date = pd.to_datetime('2018-01-01')
    df = pd.DataFrame({
        'CalendarDateWeekly': [dummy_date, dummy_date, dummy_date],
        'MinutesInPriceStatusPromotion': [10, 10, 10],
        'DepthPromotion': [.5, .5, .5],
        'MostRecentFullPrice': [10, 10, 10],
        'Target': [1, 1, 1]
    },
        index=index
    )

    feature_columns = ['MinutesInPriceStatusPromotion',
                       'DepthPromotion', 'MostRecentFullPrice']
    model_params = {'model': {'n_estimators': 1},
                    'encoder': {'cols': []}}

    print('------------------------ FEATURE FRAME ------------------------')
    print(df[feature_columns])
    print('------------------------ TARGET ------------------------')
    print(df.Target)
     
    model = train_one(
        X=df[feature_columns],
        y=df.Target,
        modobj=zoo.initialize_model(
            model_template=zoo.GBMRegressor,
            monotone_constraints=[],
            **model_params
        ),
        fit_params={},
        tracked=False
    )
    preds = predict_from_df(
        model=model,
        df=df,
        feature_columns=feature_columns,
        new_minutes_in_promo=10,
        new_depth=.5
    )

    assert np.array_equal(preds.index, index)
