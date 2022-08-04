import pandas as pd

from promotheus.ithax.utils import report_ithax_hits_targets, report_financial_metrics


# Generic dataframe with product info that is used to compute financial metrics
test_df = pd.DataFrame(
    # Test case should cover all batches, with some batches passing and others failng.

    [['FC04 Berlin', 'Menswear', 'ASOS Design', 763.0, 20.825, 0.25, 6.88, 746.0],
     ['FC01 Barnsley', 'Menswear', 'High Street', 209.0, 90.0, 0.3, 36.36, 200.0],
     ['FC03 Atlanta', 'Menswear', 'High Street', 56.0, 38.57, 0.2, 11.087, 56.0],
     ['FC04 Berlin', 'Menswear', 'High Street', 1007.0, 19.15, 0.25, 6.13, 1006.0],
     ['FC04 Berlin', 'Menswear', 'Other Brands', 140.0, 17.0, 0.15, 14.3, 134.0],
     ['FC03 Atlanta', 'Menswear', 'Sports Brands', 4.0, 79.28, 0.15, 25.91, 4.0],
     ['FC03 Atlanta', 'Menswear', 'Sports Brands', 20.0, 39.28, 0.15, 23.65, 20.0],
     ['FC01 Barnsley', 'Menswear', 'Venture', 61.0, 15.0, 0.0, 8.2, 25.0],
     ['FC01 Barnsley', 'Menswear', 'Outlet', 108.0, 34.0, 0.0, 12.8975, 70.0],
     ['FC03 Atlanta', 'Menswear', 'Outlet', 14.0, 34.28, 0.15, 11.0, 14.0],
     ['FC01 Barnsley', 'Womenswear', 'Outlet', 123.0, 7.0, 0.0, 2.15, 109.0],
     ['FC03 Atlanta', 'Womenswear', 'Outlet', 121.0, 6.78, 0.0, 2.35, 111.0],
     ['FC04 Berlin', 'Womenswear', 'Outlet', 78.0, 50.82, 0.0, 17.66, 76.0],
     ['FC01 Barnsley', 'Womenswear', 'ASOS Design', 194.0, 32.0, 0.2, 16.55, 169.0],
     ['FC01 Barnsley', 'Womenswear', 'ASOS Design', 2166.0, 8.0, 0.0, 2.12, 2042.0],
     ['FC04 Berlin', 'Womenswear', 'Other Brands', 36.0, 27.49, 0.0, 8.59, 34.0],
     ['FC03 Atlanta', 'Womenswear', 'Sports Brands', 69.0, 57.14, 0.2, 32.5, 68.0],
     ['FC04 Berlin', 'Womenswear', 'Sports Brands', 66.0, 75.0, 0.35, 27.761, 64.0],
     ['FC04 Berlin', 'Womenswear', 'Venture', 76.0, 12.07, 0.0, 1.78, 71.0],
     ['FC04 Berlin', 'Womenswear', 'Venture', 25.0, 34.15, 0.0, 11.8, 23.0]],
    columns=[
        'ParentWarehouse', 'DivisionDescription', 'BuyingSummaryGroupDescription', 'SaleableStockPrevWeek2',
        'MostRecentFullPriceGBP', 'IthaxDepth', 'UnitCostPrice', 'TradeableStockPrevWeek2'
    ]
)


def test_report_financial_metrics(test_df=test_df):

    expected = pd.Series({'StockValueGBP': 99960.410, 'StockDepth': 0.1866})
    out = report_financial_metrics(test_df)

    pd.testing.assert_series_equal(expected, out, check_less_precise=3)


def test_report_ithax_hits_targets():
    expected = pd.DataFrame(
        [
            [99960.40999999999,  0.18657257908405933,  97800.0,  0.23,  '2.2%',  '-18.9%',  True,  False],
            [1102.72, 0.15000000000000002, 1100.0, 0.23, '0.2%', '-34.8%', True, False],
            [60473.189999999995,  0.2471468678930282,  60000.0,  0.23,  '0.8%',  '7.5%',  True,  False],
            [8685.52, 0.28289659110795906, 8700.0, 0.23, '-0.2%', '23.0%', True, False],
            [29698.980000000003,  0.03641875916277271,  28000.0,  0.23,  '6.1%',  '-84.2%',  False,  False]
        ],
        columns=['StockValueGBP', 'StockDepth', 'Target_StockValueGBP', 'Target_StockDepth',
                 'PctDiscrep_StockValueGBP', 'PctDiscrep_StockDepth', 'Hit_StockValueGBP', 'Hit_StockDepth'],
        index=['Overall', 'Menswear_SportsBrands', 'Menswear_NotSportsBrands',
               'Womenswear_SportsBrands', 'Womenswear_NotSportsBrands'],
    )

    out = report_ithax_hits_targets(
        test_df,
        target_stock_values={
            'Menswear_SportsBrands': 1100,
            'Menswear_NotSportsBrands': 60000,
            'Womenswear_SportsBrands': 8700,
            'Womenswear_NotSportsBrands': 28000
        },
        target_stock_depth=0.23,
        cast_stockval_in_millions=False
    )

    pd.testing.assert_frame_equal(expected, out)
