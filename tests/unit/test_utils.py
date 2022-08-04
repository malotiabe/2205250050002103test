import pytest
import numpy as np
import pandas as pd

from promotheus.utils.utils import df_loc_fillcol


def test_df_loc_fillcol_returns_filled_cols():
    df = pd.DataFrame(
        np.reshape([k for k in range(0, 30)], (6, 5)),
        columns=[f'Var{k}' for k in range(1, 6)]
    )

    df_out = df_loc_fillcol(
        df,
        cols=['Var1', 'Var2', 'VarA', 'VarB'],
    )
    df_expected = pd.DataFrame(
        [[0, 1, None, None],
         [5, 6, None, None],
         [10, 11, None, None],
         [15, 16, None, None],
         [20, 21, None, None],
         [25, 26, None, None]],
        columns=['Var1', 'Var2', 'VarA', 'VarB']
    )

    pd.testing.assert_frame_equal(df_out, df_expected)


def test_df_loc_fillcol_respects_must_have_cols():

    df = pd.DataFrame(np.reshape([k for k in range(0, 30)], (6, 5)),
                      columns=[f'Var{k}' for k in range(1, 6)]
                      )
    with pytest.raises(AssertionError):
        df_loc_fillcol(
            df,
            cols=['Var1', 'Var2', 'VarA', 'VarB'],
            cols_must_have=['VarA']
        )
