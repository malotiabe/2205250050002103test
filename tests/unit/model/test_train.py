import pytest
from typing import Union
import pandas as pd
from sklearn.exceptions import NotFittedError

from promotheus.model.train import (
    train_one, CVInputCompiler
)
from promotheus.evaluation.evaluate import model_comparator
from promotheus.model import zoo
from tests.fixtures import test_start_date, test_end_date


def test_load_training_data_has_correct_date_range(load_training_data_output):
    assert (
        load_training_data_output.CalendarDateWeekly.max() -
        load_training_data_output.CalendarDateWeekly.min() +
        pd.Timedelta(weeks=1)
    ).days == (test_end_date - test_start_date).days


def test_load_training_data_has_correct_number_of_weeks(
    load_training_data_output
):
    assert load_training_data_output.CalendarDateWeekly.nunique() == 2


def test_train_one_output_is_fitted(load_training_data_output,
                                    sample_feature_columns,
                                    sample_categorical_columns
                                    ):

    model_params = {'model': {},
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
    try:
        model.predict(load_training_data_output[sample_feature_columns])
        trained = True
    except NotFittedError:
        trained = False

    assert trained


def test_evaluate_model_metrics_expected():

    def _get_column_total_over_price_status(
            df: pd.DataFrame,
            column: str,
            prev_week: int
    ) -> pd.Series:

        price_statuses = ['Full Price', 'Markdown', 'Promotion']
        for ps in price_statuses:
            if f'{column}{ps}PrevWeek{prev_week}' not in df.columns:
                raise ValueError(
                    f"Column '{column}{ps}PrevWeek{prev_week}' " +
                    f"not in columns {df.columns}"
                )

        columns = [f'{column}{ps}PrevWeek{prev_week}' for ps in price_statuses]
        return df[columns].sum(axis=1)

    def _previous_week_total_target_baseline(
            df: pd.DataFrame,
            target_variable: str,
            minutes_for_prediction: Union[pd.Series, float],
            prev_week: int
    ) -> pd.Series:

        if prev_week < 1:
            raise ValueError(
                'Previous Week must be greater than or equal to 1.')

        x = len(minutes_for_prediction)
        if x != 1 and x != len(df):
            raise ValueError(
                f'MinutesInPrediction len={x} but df len = {len(df)}' +
                'Minutes must have the same length or be a scalar.')

        prev_week_target_total = _get_column_total_over_price_status(
            df=df, column=target_variable, prev_week=prev_week)
        prev_week_minutes_total = _get_column_total_over_price_status(
            df=df, column='MinutesInPriceStatus', prev_week=prev_week)

        baseline_preds = prev_week_target_total * \
            minutes_for_prediction/prev_week_minutes_total

        return baseline_preds

    def _remove_price_status_from_col_name(col_name: str) -> str:
        for ps in ['Full Price', 'Markdown', 'Promotion']:
            col_name = col_name.replace(ps, '')

        return col_name

    dummy_date = pd.to_datetime('2012-11-13')
    df_train = pd.DataFrame({
        'CalendarDateWeekly': [dummy_date, dummy_date, dummy_date],
        'TargetFull Price': [0, 0, 0],
        'TargetMarkdown': [0, 0, 0],
        'TargetPromotion': [1, 1, 1]
    })
    df_test = pd.DataFrame({
        'CalendarDateWeekly': [dummy_date, dummy_date, dummy_date],
        'TargetFull Price': [0, 0, 0],
        'TargetMarkdown': [0, 0, 0],
        'TargetPromotion': [2, 2, 2],
        'TargetFull PricePrevWeek1': [0, 0, 0],
        'TargetMarkdownPrevWeek1': [0, 0, 0],
        'TargetPromotionPrevWeek1': [3, 2, 2],
        'MinutesInPriceStatusFull Price': [0, 0, 0],
        'MinutesInPriceStatusMarkdown': [0, 0, 0],
        'MinutesInPriceStatusPromotion': [1, 1, 1],
        'MinutesInPriceStatusFull PricePrevWeek1': [0, 0, 0],
        'MinutesInPriceStatusMarkdownPrevWeek1': [0, 0, 0],
        'MinutesInPriceStatusPromotionPrevWeek1': [1, 1, 1]
    })

    target_column = 'TargetPromotion'
    feature_columns = ['TargetPromotion']
    categorical_columns = []

    model_params = {'model': {},
                    'encoder': {'cols': categorical_columns}}
    model = train_one(
        X=df_train[feature_columns],
        y=df_train[target_column],
        modobj=zoo.initialize_model(
            model_template=zoo.GBMRegressor,
            monotone_constraints=[],
            **model_params
        ),
        fit_params={},
        tracked=False
    )
    x = df_test[feature_columns]
    df_test['pred'] = pd.Series(model.predict(x), index=df_test.index)

    df_test['baseline'] = _previous_week_total_target_baseline(
        df_test,
        target_variable=_remove_price_status_from_col_name(target_column),
        minutes_for_prediction=df_test['MinutesInPriceStatusPromotion'],
        prev_week=1
    )

    scores = model_comparator.score_dataset(
        df_test,
        metrics=['rel_mae', 'wape', 'prop_bias'],
        cols={
            'true': target_column,
            'predict': 'pred',
            'baseline': 'baseline',
        }

    )

    assert scores == [3.0, 0.5, -0.5], 'Scores (rel_mae, wape, prop_bias) not as expected!'


def test_kfold_sequential_with_recentmost_as_test():

    total_n_slices = 10
    n_folds, n_slices_for_train, n_slices_per_test = 3, 4, 2
    slice_dfs = [pd.DataFrame({'slice_key': [i]})
                 for i in range(1, total_n_slices+1)]

    # Run function
    cv_out = CVInputCompiler.kfold_sequential_with_recentmost_as_test(
        dataslices=slice_dfs,
        n_folds=n_folds,
        n_dataslices_for_training=n_slices_for_train,
        n_dataslices_per_test=n_slices_per_test
    )

    # Expected slice keys (e.g. "WeekNum") for each fold's train/test
    expected_train_slicekeys = [
        [8, 7, 6, 5],
        [7, 6, 5, 4],
        [6, 5, 4, 3]
    ]
    expected_test_slicekeys = [
        [10, 9],
        [9, 8],
        [8, 7]
    ]

    for k in range(n_folds):

        # Check train df
        pd.testing.assert_series_equal(
            cv_out[k]['train'].slice_key.reset_index(drop=True),
            pd.Series(expected_train_slicekeys[k]),
            check_names=False, check_index_type=False
        )

        # Check test df
        pd.testing.assert_series_equal(
            cv_out[k]['test'].slice_key.reset_index(drop=True),
            pd.Series(expected_test_slicekeys[k]),
            check_names=False, check_index_type=False
        )


def test_get_folds_raises_error_for_k_too_large():

    total_n_slices = 10
    n_folds = 10
    slice_dfs = [pd.DataFrame({'slice_key': [i]})
                 for i in range(1, total_n_slices+1)]

    with pytest.raises(ValueError):
        CVInputCompiler.kfold_sequential_with_recentmost_as_test(
            dataslices=slice_dfs,
            n_folds=n_folds,
            n_dataslices_for_training=1,
            n_dataslices_per_test=1
        )
