import datetime as dt
import pandas as pd
import pytest

from promotheus.model.monitor.utils import aggregate_cv_results


def test_aggregate_cv_results_expected_result():

    date_times = [
        dt.datetime(2020, 1, 1), dt.datetime(2020, 1, 1),
        dt.datetime(2020, 1, 8), dt.datetime(2020, 1, 8)
    ]

    df_cv1 = pd.DataFrame({
        'CalendarDateWeekly': date_times,
        'y_true': [1]*4,
        'y_baseline': [2]*4,
        'y_pred': [3]*4,
    })

    df_cv2 = pd.DataFrame({
        'CalendarDateWeekly': date_times,
        'y_true': [1]*4,
        'y_baseline': [2] * 4,
        'y_pred': [4]*4
    })

    expected_df_agg_cv_results = pd.DataFrame({
        'cv':  ['cv_0', 'cv_0', 'cv_1', 'cv_1'],
        'CalendarDateWeekly': [
            dt.datetime(2020, 1, 1), dt.datetime(2020, 1, 8),
            dt.datetime(2020, 1, 1), dt.datetime(2020, 1, 8)
        ],
        'y_true': [2]*4,
        'y_baseline': [4]*4,
        'y_pred': [6, 6, 8, 8]
    })

    expected_df_agg_gt = pd.DataFrame({
        'CalendarDateWeekly': [dt.datetime(2020, 1, 1),
                               dt.datetime(2020, 1, 8)],
        'y_true': [2, 2],
        'y_baseline': [4, 4]
    })

    cv_results = aggregate_cv_results(cv_results=[df_cv1, df_cv2], agg='sum')

    pd.testing.assert_frame_equal(cv_results[0], expected_df_agg_cv_results)
    pd.testing.assert_frame_equal(cv_results[1], expected_df_agg_gt)


def test_aggregate_cv_results_throws_error_for_inconsistent_ground_truth():

    date_times = [dt.datetime(2020, 1, 1)]*2

    df_cv1 = pd.DataFrame({
        'CalendarDateWeekly': date_times,
        'y_true': [1]*2,
        'y_baseline': [2]*2,
        'y_pred': [3]*2,
    })

    df_cv2 = pd.DataFrame({
        'CalendarDateWeekly': date_times,
        'y_true': [2]*2,
        'y_baseline': [2]*2,
        'y_pred': [4]*2
    })

    with pytest.raises(ValueError):
        aggregate_cv_results(cv_results=[df_cv1, df_cv2], agg='sum')
