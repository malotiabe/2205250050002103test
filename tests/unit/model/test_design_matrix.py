import pandas as pd
from promotheus.model import design_matrix as dm


df_cat = pd.DataFrame([
    ['FC01 Barnsley', 'Not a buyrarchy product', 8993, 0.0, 58],
    ['FC01 Barnsley', 'Womens Outlet', 2345, 16.0, 47],
    ['FC03 Atlanta', 'Womenswear', 4847, 42.0, 77],
    ['FC04 Berlin', 'Menswear', 1931, 3.0, 38],
    ['FC04 Berlin', 'Menswear', 5767, 0.0, 73],
    ['FC04 Berlin', 'Menswear', 2742, 20.0, 61],
    ['FC04 Berlin', 'Outlet', 6463, 15.0, 5],
    ['FC04 Berlin', 'Not a buyrarchy product', 6107, 0.0, 88],
    ['FC03 Atlanta', 'Womenswear', 1738, 26.99, 77],
    ['FC03 Atlanta', 'Womenswear', 8055, 0.0, 27]
], columns=['Warehouse', 'Division', 'MinutesPromo', 'FullPrice', 'SoldUnits'])


def test_CategoricalAutoEncoder_as_expected_in_sample(df=df_cat):

    # Intended behaviour: Hash Division, OHE Warehouse
    _cat = ['Warehouse', 'Division', ]
    encoder_kwargs = {
        'cardinality_max_before_hash': 3,
        'hash_n_dimensions': 2,
    }
    df_expected = pd.DataFrame([
        [1.,  0.,  0.,  8., -1.],
        [1.,  0.,  0.,  3.,  0.],
        [0.,  1.,  0.,  0.,  2.],
        [0.,  0.,  1.,  1.,  1.],
        [0.,  0.,  1.,  1.,  1.],
        [0.,  0.,  1.,  1.,  1.],
        [0.,  0.,  1.,  3., -1.],
        [0.,  0.,  1.,  8., -1.],
        [0.,  1.,  0.,  0.,  2.],
        [0.,  1.,  0.,  0.,  2.]
    ], columns=['Warehouse_FC01 Barnsley', 'Warehouse_FC03 Atlanta', 'Warehouse_FC04 Berlin', 'Division_1', 'Division_2'])

    cae = dm.CategoricalAutoEncoder(**encoder_kwargs)
    x = cae.fit_transform(df[_cat], cols=_cat)

    pd.testing.assert_frame_equal(x, df_expected)


def test_CategoricalAutoEncoder_as_expected_out_of_sample(df=df_cat):

    # Intended behaviour: Hash Division, OHE Warehouse
    _cat = ['Warehouse', 'Division', ]
    encoder_kwargs = {
        'cardinality_max_before_hash': 3,
        'hash_n_dimensions': 2,
    }
    df_expected = pd.DataFrame([
        [0.,  0.,  0.,  8., -1.],
        [0.,  0.,  0.,  3.,  0.],
        [0.,  0.,  0.,  0.,  2.],
        [0.,  0.,  1.,  0., -5.],
        [0.,  0.,  1.,  0., -5.],
        [0.,  0.,  1.,  0., -5.],
        [0.,  0.,  1.,  3., -1.],
        [0.,  0.,  1.,  8., -1.],
        [0.,  1.,  0.,  0.,  2.],
        [0.,  1.,  0.,  0.,  2.]
    ], columns=['Warehouse_FC01 Barnsley', 'Warehouse_FC03 Atlanta', 'Warehouse_FC04 Berlin', 'Division_1', 'Division_2'])

    # Fit
    cae = dm.CategoricalAutoEncoder(**encoder_kwargs)
    cae.fit(df[_cat], cols=_cat)

    # New categories
    df2 = df.copy()
    df2.loc[0:2, 'Warehouse'] = 'NewWarehouse'
    df2.loc[3:5, 'Division'] = 'NewDivision'
    x = cae.transform(df2[_cat])

    pd.testing.assert_frame_equal(x, df_expected)
