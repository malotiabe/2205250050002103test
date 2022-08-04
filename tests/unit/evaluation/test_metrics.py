import pandas as pd
import numpy as np
import pytest
from sklearn.metrics import mean_absolute_error

from promotheus.evaluation.metrics import relative_score, prop_bias


def test_relative_score_throws_zero_basline_error_error():
    y_true = pd.Series([1, 2, 3])
    y_pred = pd.Series([1.1, 2.1, 2.9])
    y_baseline = pd.Series([1, 2, 3])

    with pytest.raises(RuntimeError):
        relative_score(y_true=y_true, y_pred=y_pred,
                       y_baseline=y_baseline,
                       metric=mean_absolute_error)


def test_relative_score_expected_value():

    y_true = pd.Series([1, 2, 3])
    y_pred = pd.Series([1.1, 2.1, 2.9])
    y_baseline = pd.Series([1.2, 1.8, 3.2])

    score = relative_score(y_true=y_true, y_pred=y_pred,
                           y_baseline=y_baseline, metric=mean_absolute_error)

    assert pytest.approx(score, 1e-10) == 0.5


def test_prop_bias_expected_value():

    y_true = pd.Series([2, 2, 4])
    y_pred = pd.Series([2, 2, 3])

    score = prop_bias(y_true=y_true, y_pred=y_pred)
    assert pytest.approx(score, 1e-10) == -0.125


def test_prop_bias_inifity_at_zero_true():

    y_true = pd.Series([0, 0, 0])
    y_pred = pd.Series([2, 3, 3])

    score = prop_bias(y_true=y_true, y_pred=y_pred)
    assert score == np.inf
