import pandas as pd

from promotheus.optimiser.optimiser import (
    get_optimal_depths_gridsearch_argmax,
    groupby_select_on_criteria
)


def test_get_optimal_depths_gridsearch_argmax():

    # Starting df (predicted reward across entire act space, per key variable)
    df = pd.DataFrame({
        0: {'test': '1winner', 'pid': 1, 'fc': 'A', 'act': 0.00, 'reward': 30},
        1: {'test': '1winner', 'pid': 1, 'fc': 'A', 'act': 0.10, 'reward': 20},
        2: {'test': '1winner', 'pid': 1, 'fc': 'A', 'act': 0.20, 'reward': 10},
        3: {'test': 'tie',     'pid': 1, 'fc': 'B', 'act': 0.00, 'reward': 20},
        4: {'test': 'tie',     'pid': 1, 'fc': 'B', 'act': 0.10, 'reward': 20},
        5: {'test': 'tie',     'pid': 1, 'fc': 'B', 'act': 0.20, 'reward': 10},
    }).T
    df.reward = df.reward.astype(float)
    df.act = df.act.astype(float)
    df.pid = df.pid.astype(int)

    key, act, reward = ['pid', 'fc'], 'act', 'reward'
    df_out = get_optimal_depths_gridsearch_argmax(
        df,
        groupby_key=key,
        col_action=act,
        col_reward=reward,
        return_all=False
    )
    assert df_out.shape[0] == len(df.groupby(key)), \
        "requested return only optimal # rows not expected"

    df_out = get_optimal_depths_gridsearch_argmax(
        df,
        groupby_key=key,
        col_action=act,
        col_reward=reward,
        return_all=True
    )
    assert df_out.shape[0] == df.shape[0], \
        "requested return all but df shape changed"
    assert df_out.query('test == "1winner"').isRecommended.sum() == 1, \
        "test case with 1 clear winner didn't find 1 clear winner"
    assert df_out.query('test == "tie"').isRecommended.sum() == 1, \
        "test case with ties didn't pick 1 clear winner"


def test_groupby_select_on_criteria_returns_correct_rows():

    df = pd.DataFrame({
        'productId': [1] * 8 + [2] * 4,
        'ParentWarehouse': ['A'] * 4 + ['B'] * 4 + ['A'] * 4,
        'ProposedDepthPromotion': [0.1, 0.2, 0.3, 0.4] * 3,
        'ForecastedProfit':
            [1.00, 2.3203, 3.1203, 2.35434] +
        [3.3234, 2.4532, 1.231, 4.646] +
        [5.122, 4.414, 3.4356, 2.343]
    })

    df_output = groupby_select_on_criteria(
        df=df,
        groupby_key=['productId', 'ParentWarehouse'],
        criteria_col='ForecastedProfit',
        criteria='max',
        round_precision=3,
    )

    df_expected = pd.DataFrame(
        data={
            'productId': [1, 1, 2],
            'ParentWarehouse': ['A', 'B', 'A'],
            'ProposedDepthPromotion': [0.3, 0.4, 0.1],
            'ForecastedProfit': [3.120, 4.646, 5.122]
        },
        index=[2, 7, 8]
    )

    pd.testing.assert_frame_equal(df_output, df_expected)
