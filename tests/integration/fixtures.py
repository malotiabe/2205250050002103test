from typing import Dict
import copy
from promotheus.definitions import model_config, training_data_config, validation_config
from promotheus.environment import Environment

true_environment = Environment()
# TODO: Instead of having an explicit mapping here, and telling the code which experiment to run.
# a cleaner approach would be to have the main code being tested just refer to the mapping in promotheus.tracking.py
# and then mock / inject the values forthe test experiments into promotheus.tracking.py from here
environment_to_test_experiment_mapping = {
    'lab': {
        'serve': {
            'tracking_uri': 'databricks',
            'id': '3958069098699372',
            'artifact_location': '/Shared/RetailScience/Promotheus/Pipelines/train-to-serve-test',
            'model_path': 'model',
            'host': 'https://adb-2793304196320822.2.azuredatabricks.net',
            'register': {
                'model_uri': 'runs:/{run_id}/model',
                'name': 'Promotheus-serve-test'
            }
        },
        'score': {
            'tracking_uri': 'databricks',
            'id': '3958069098699371',
            'artifact_location': '/Shared/RetailScience/Promotheus/Pipelines/train-to-score-test',
            'model_path': 'models',
            'host': 'https://adb-2793304196320822.2.azuredatabricks.net',
            'register': None
        }
    },
    'dev': {
        'serve': {
            'tracking_uri': 'databricks',
            'id': '2470103304518012',
            'artifact_location': '/Shared/RetailScience/Promotheus/Pipelines/train-to-serve-test',
            'model_path': 'model',
            'host': 'https://adb-7627893052593350.10.azuredatabricks.net/',
            'register': {
                'model_uri': 'runs:/{run_id}/model',
                'name': 'Promotheus-serve-test'
            }
        },
        'score': {
            'tracking_uri': 'databricks',
            'id': '2470103304518011',
            'artifact_location': '/Shared/RetailScience/Promotheus/Pipelines/train-to-score-test',
            'model_path': 'models',
            'host': 'https://adb-7627893052593350.10.azuredatabricks.net/',
            'register': None
        }
    },
    'np': {
        'serve': {
            'tracking_uri': 'databricks',
            'id': '2736616829650876',
            'artifact_location': '/Shared/RetailScience/Promotheus/Pipelines/train-to-serve-test',
            'model_path': 'model',
            'host': 'https://adb-199148056525493.13.azuredatabricks.net/',
            'register': {
                'model_uri': 'runs:/{run_id}/model',
                'name': 'Promotheus-serve-test'
            }
        },
        'score': {
            'tracking_uri': 'databricks',
            'id': '2736616829650875',
            'artifact_location': '/Shared/RetailScience/Promotheus/Pipelines/train-to-score-test',
            'model_path': 'models',
            'host': 'https://adb-199148056525493.13.azuredatabricks.net/',
            'register': None
        }
    },
    'pd': {
        'serve': {
            'tracking_uri': 'databricks',
            'id': '4423108000890227',
            'artifact_location': '/Shared/RetailScience/Promotheus/Pipelines/train-to-serve-test',
            'model_path': 'model',
            'host': 'https://adb-7616617238323226.6.azuredatabricks.net/',
            'register': {
                'model_uri': 'runs:/{run_id}/model',
                'name': 'Promotheus-serve-test'
            }
        },
        'score': {
            'tracking_uri': 'databricks',
            'id': '4423108000890228',
            'artifact_location': '/Shared/RetailScience/Promotheus/Pipelines/train-to-score-test',
            'model_path': 'models',
            'host': 'https://adb-7616617238323226.6.azuredatabricks.net/',
            'register': None
        }
    }
}

test_experiments = environment_to_test_experiment_mapping[true_environment.short_name]


preproc_train_columns = ['productId', 'ParentWarehouse', 'CalendarDateWeekly', 'DepthPromotion', 'DepthClearance',
                         'MinutesInPriceStatusClearance', 'MinutesInPriceStatusFullPrice',
                         'MinutesInPriceStatusPromotion', 'CurrentPrice', 'PriceFullPrice', 'PriceClearance',
                         'PricePromotion', 'MostRecentFullPrice', 'UnitCostPrice', 'SoldUnits', 'SoldUnitsFullPrice',
                         'SoldUnitsPromotion', 'SoldUnitsClearance', 'WeeksOnSite', 'Cover', 'SaleableStock',
                         'TradeableStock', 'GlobalMaxTradeableSKUs', 'GlobalSaleableStock', 'GlobalTradeableStock',
                         'ReplacementUnitsFullPrice', 'ReplacementUnitsPromotion', 'ReplacementUnitsClearance',
                         'ReturnCentresMaxTradeableSKUs', 'ReturnCentresSaleableStock',
                         'ReturnCentresTradeableStock', 'VoidUnits', 'containedFullPrice', 'containedPromotion',
                         'containedClearance', 'containedPromotionalClearance',
                         'MinutesInPriceStatusClearancePrevWeek1', 'MinutesInPriceStatusClearancePrevWeek2',
                         'MinutesInPriceStatusClearancePrevWeek3', 'MinutesInPriceStatusClearancePrevWeek4',
                         'MinutesInPriceStatusClearancePrevWeek5', 'MinutesInPriceStatusClearancePrevWeek6',
                         'MinutesInPriceStatusClearancePrevWeek7', 'MinutesInPriceStatusClearancePrevWeek8',
                         'MinutesInPriceStatusFullPricePrevWeek1', 'MinutesInPriceStatusFullPricePrevWeek2',
                         'MinutesInPriceStatusFullPricePrevWeek3', 'MinutesInPriceStatusFullPricePrevWeek4',
                         'MinutesInPriceStatusFullPricePrevWeek5', 'MinutesInPriceStatusFullPricePrevWeek6',
                         'MinutesInPriceStatusFullPricePrevWeek7', 'MinutesInPriceStatusFullPricePrevWeek8',
                         'MinutesInPriceStatusPromotionPrevWeek1', 'MinutesInPriceStatusPromotionPrevWeek2',
                         'MinutesInPriceStatusPromotionPrevWeek3', 'MinutesInPriceStatusPromotionPrevWeek4',
                         'MinutesInPriceStatusPromotionPrevWeek5', 'MinutesInPriceStatusPromotionPrevWeek6',
                         'MinutesInPriceStatusPromotionPrevWeek7', 'MinutesInPriceStatusPromotionPrevWeek8',
                         "MinutesInPriceStatusPromotionalClearance",
                         "MinutesInPriceStatusPromotionalClearancePrevWeek1",
                         'MinutesInPriceStatusPromotionalClearancePrevWeek2',
                         'MinutesInPriceStatusPromotionalClearancePrevWeek3',
                         'MinutesInPriceStatusPromotionalClearancePrevWeek4',
                         'MinutesInPriceStatusPromotionalClearancePrevWeek5',
                         'MinutesInPriceStatusPromotionalClearancePrevWeek6',
                         'MinutesInPriceStatusPromotionalClearancePrevWeek7',
                         'MinutesInPriceStatusPromotionalClearancePrevWeek8',
                         'PriceFullPricePrevWeek1', 'PriceFullPricePrevWeek2', 'PriceFullPricePrevWeek3',
                         'PriceFullPricePrevWeek4', 'PriceFullPricePrevWeek5', 'PriceFullPricePrevWeek6',
                         'PriceFullPricePrevWeek7', 'PriceFullPricePrevWeek8', 'PriceClearancePrevWeek1',
                         'PriceClearancePrevWeek2', 'PriceClearancePrevWeek3', 'PriceClearancePrevWeek4',
                         'PriceClearancePrevWeek5', 'PriceClearancePrevWeek6', 'PriceClearancePrevWeek7',
                         'PriceClearancePrevWeek8', 'PricePromotionPrevWeek1', 'PricePromotionPrevWeek2',
                         'PricePromotionPrevWeek3', 'PricePromotionPrevWeek4', 'PricePromotionPrevWeek5',
                         'PricePromotionPrevWeek6', 'PricePromotionPrevWeek7', 'PricePromotionPrevWeek8',
                         'MostRecentFullPricePrevWeek1', 'MostRecentFullPricePrevWeek2',
                         'MostRecentFullPricePrevWeek3', 'MostRecentFullPricePrevWeek4',
                         'MostRecentFullPricePrevWeek5', 'MostRecentFullPricePrevWeek6',
                         'MostRecentFullPricePrevWeek7', 'MostRecentFullPricePrevWeek8', 'SoldUnitsPrevWeek1',
                         'SoldUnitsPrevWeek2', 'SoldUnitsPrevWeek3', 'SoldUnitsPrevWeek4', 'SoldUnitsPrevWeek5',
                         'SoldUnitsPrevWeek6', 'SoldUnitsPrevWeek7', 'SoldUnitsPrevWeek8',
                         'SoldUnitsFullPricePrevWeek1', 'SoldUnitsFullPricePrevWeek2', 'SoldUnitsFullPricePrevWeek3',
                         'SoldUnitsFullPricePrevWeek4', 'SoldUnitsFullPricePrevWeek5', 'SoldUnitsFullPricePrevWeek6',
                         'SoldUnitsFullPricePrevWeek7', 'SoldUnitsFullPricePrevWeek8', 'SoldUnitsPromotionPrevWeek1',
                         'SoldUnitsPromotionPrevWeek2', 'SoldUnitsPromotionPrevWeek3', 'SoldUnitsPromotionPrevWeek4',
                         'SoldUnitsPromotionPrevWeek5', 'SoldUnitsPromotionPrevWeek6', 'SoldUnitsPromotionPrevWeek7',
                         'SoldUnitsPromotionPrevWeek8', 'SoldUnitsClearancePrevWeek1', 'SoldUnitsClearancePrevWeek2',
                         'SoldUnitsClearancePrevWeek3', 'SoldUnitsClearancePrevWeek4', 'SoldUnitsClearancePrevWeek5',
                         'SoldUnitsClearancePrevWeek6', 'SoldUnitsClearancePrevWeek7', 'SoldUnitsClearancePrevWeek8',
                         'CoverPrevWeek1', 'CoverPrevWeek2', 'CoverPrevWeek3', 'CoverPrevWeek4', 'CoverPrevWeek5',
                         'CoverPrevWeek6', 'CoverPrevWeek7', 'CoverPrevWeek8', 'SaleableStockPrevWeek1',
                         'SaleableStockPrevWeek2', 'SaleableStockPrevWeek3', 'SaleableStockPrevWeek4',
                         'SaleableStockPrevWeek5', 'SaleableStockPrevWeek6', 'SaleableStockPrevWeek7',
                         'SaleableStockPrevWeek8', 'TradeableStockPrevWeek1', 'TradeableStockPrevWeek2',
                         'TradeableStockPrevWeek3', 'TradeableStockPrevWeek4', 'TradeableStockPrevWeek5',
                         'TradeableStockPrevWeek6', 'TradeableStockPrevWeek7', 'TradeableStockPrevWeek8',
                         'GlobalMaxTradeableSKUsPrevWeek1', 'GlobalMaxTradeableSKUsPrevWeek2',
                         'GlobalMaxTradeableSKUsPrevWeek3', 'GlobalMaxTradeableSKUsPrevWeek4',
                         'GlobalMaxTradeableSKUsPrevWeek5', 'GlobalMaxTradeableSKUsPrevWeek6',
                         'GlobalMaxTradeableSKUsPrevWeek7', 'GlobalMaxTradeableSKUsPrevWeek8',
                         'GlobalSaleableStockPrevWeek1', 'GlobalSaleableStockPrevWeek2',
                         'GlobalSaleableStockPrevWeek3', 'GlobalSaleableStockPrevWeek4',
                         'GlobalSaleableStockPrevWeek5', 'GlobalSaleableStockPrevWeek6',
                         'GlobalSaleableStockPrevWeek7', 'GlobalSaleableStockPrevWeek8',
                         'GlobalTradeableStockPrevWeek1', 'GlobalTradeableStockPrevWeek2',
                         'GlobalTradeableStockPrevWeek3', 'GlobalTradeableStockPrevWeek4',
                         'GlobalTradeableStockPrevWeek5', 'GlobalTradeableStockPrevWeek6',
                         'GlobalTradeableStockPrevWeek7', 'GlobalTradeableStockPrevWeek8',
                         'ReplacementUnitsFullPricePrevWeek1', 'ReplacementUnitsFullPricePrevWeek2',
                         'ReplacementUnitsFullPricePrevWeek3', 'ReplacementUnitsFullPricePrevWeek4',
                         'ReplacementUnitsFullPricePrevWeek5', 'ReplacementUnitsFullPricePrevWeek6',
                         'ReplacementUnitsFullPricePrevWeek7', 'ReplacementUnitsFullPricePrevWeek8',
                         'ReplacementUnitsPromotionPrevWeek1', 'ReplacementUnitsPromotionPrevWeek2',
                         'ReplacementUnitsPromotionPrevWeek3', 'ReplacementUnitsPromotionPrevWeek4',
                         'ReplacementUnitsPromotionPrevWeek5', 'ReplacementUnitsPromotionPrevWeek6',
                         'ReplacementUnitsPromotionPrevWeek7', 'ReplacementUnitsPromotionPrevWeek8',
                         'ReplacementUnitsClearancePrevWeek1', 'ReplacementUnitsClearancePrevWeek2',
                         'ReplacementUnitsClearancePrevWeek3', 'ReplacementUnitsClearancePrevWeek4',
                         'ReplacementUnitsClearancePrevWeek5', 'ReplacementUnitsClearancePrevWeek6',
                         'ReplacementUnitsClearancePrevWeek7', 'ReplacementUnitsClearancePrevWeek8',
                         'ReturnCentresMaxTradeableSKUsPrevWeek1', 'ReturnCentresMaxTradeableSKUsPrevWeek2',
                         'ReturnCentresMaxTradeableSKUsPrevWeek3', 'ReturnCentresMaxTradeableSKUsPrevWeek4',
                         'ReturnCentresMaxTradeableSKUsPrevWeek5', 'ReturnCentresMaxTradeableSKUsPrevWeek6',
                         'ReturnCentresMaxTradeableSKUsPrevWeek7', 'ReturnCentresMaxTradeableSKUsPrevWeek8',
                         'ReturnCentresSaleableStockPrevWeek1', 'ReturnCentresSaleableStockPrevWeek2',
                         'ReturnCentresSaleableStockPrevWeek3', 'ReturnCentresSaleableStockPrevWeek4',
                         'ReturnCentresSaleableStockPrevWeek5', 'ReturnCentresSaleableStockPrevWeek6',
                         'ReturnCentresSaleableStockPrevWeek7', 'ReturnCentresSaleableStockPrevWeek8',
                         'ReturnCentresTradeableStockPrevWeek1', 'ReturnCentresTradeableStockPrevWeek2',
                         'ReturnCentresTradeableStockPrevWeek3', 'ReturnCentresTradeableStockPrevWeek4',
                         'ReturnCentresTradeableStockPrevWeek5', 'ReturnCentresTradeableStockPrevWeek6',
                         'ReturnCentresTradeableStockPrevWeek7', 'ReturnCentresTradeableStockPrevWeek8',
                         'VoidUnitsPrevWeek1', 'VoidUnitsPrevWeek2', 'VoidUnitsPrevWeek3', 'VoidUnitsPrevWeek4',
                         'VoidUnitsPrevWeek5', 'VoidUnitsPrevWeek6', 'VoidUnitsPrevWeek7', 'VoidUnitsPrevWeek8',
                         'containedFullPricePrevWeek1', 'containedFullPricePrevWeek2', 'containedFullPricePrevWeek3',
                         'containedFullPricePrevWeek4', 'containedFullPricePrevWeek5', 'containedFullPricePrevWeek6',
                         'containedFullPricePrevWeek7', 'containedFullPricePrevWeek8', 'containedPromotionPrevWeek1',
                         'containedPromotionPrevWeek2', 'containedPromotionPrevWeek3', 'containedPromotionPrevWeek4',
                         'containedPromotionPrevWeek5', 'containedPromotionPrevWeek6', 'containedPromotionPrevWeek7',
                         'containedPromotionPrevWeek8', 'containedClearancePrevWeek1', 'containedClearancePrevWeek2',
                         'containedClearancePrevWeek3', 'containedClearancePrevWeek4', 'containedClearancePrevWeek5',
                         'containedClearancePrevWeek6', 'containedClearancePrevWeek7', 'containedClearancePrevWeek8',
                         'ProductOptionCode', 'BusinessModelId', 'BusinessModelDescription',
                         'BuyingSummaryGroupDescription', 'BuyingSummarySubgroupDescription', 'BuyingGroupId',
                         'BuyingGroupDescription', 'BuyingSubGroupId', 'BuyingSubGroupDescription',
                         'BuyingDivisionId', 'BuyingDivisionDescription', 'GroupId', 'GroupDescription',
                         'ParentBuyingSubGroupDescription', 'DivisionDescription',
                         'ProductGroupId', 'ProductGroupDescription', 'CategoryId', 'CategoryDescription',
                         'SubcategoryId', 'SubCategoryDescription', 'StyleCode', 'StyleDescription', 'WebsiteColour',
                         'AsosColourId', 'AsosColourDescription', 'AsosColourGroupId', 'AsosColourGroupDescription',
                         'SupplierReference', 'BrandId', 'BrandDescription', 'BrandGroupId', 'BrandGroupDescription',
                         'SeasonalEvent', 'Flow', 'Range', 'RangeShopByFit', 'OutletStockType',
                         'BrandedSeasonalPlanningConcat', 'TotalSKUs', 'RetailSeason', 'isFlow',
                         'Year', 'WeekOfYear', 'WeekOfYearSin', 'WeekOfYearCos', 'MonthOfYear', 'MonthOfYearSin',
                         'MonthOfYearCos', 'WeekOfMonth', 'WeekOfMonthSin', 'WeekOfMonthCos',
                         'DepthPromotionRounded', 'SoldUnitsPromotionDaily', 'SoldUnitsPrevWeek1Daily',
                         'SoldUnitsPrevWeek2Daily',

                         # new merch hierarchy columns
                         'ParentBuyingSubGroupDescription',
                         'DivisionDescription'
                         ]

preproc_serve_columns = ['productId', 'ParentWarehouse', 'CalendarDateWeekly', 'PriceFullPrice', 'MostRecentFullPrice',
                         'UnitCostPrice', 'WeeksOnSite', 'MinutesInPriceStatusClearancePrevWeek2',
                         'MinutesInPriceStatusClearancePrevWeek3', 'MinutesInPriceStatusClearancePrevWeek4',
                         'MinutesInPriceStatusClearancePrevWeek5', 'MinutesInPriceStatusClearancePrevWeek6',
                         'MinutesInPriceStatusClearancePrevWeek7', 'MinutesInPriceStatusClearancePrevWeek8',

                         "MinutesInPriceStatusPromotionalClearance",
                         'MinutesInPriceStatusPromotionalClearancePrevWeek2',
                         'MinutesInPriceStatusPromotionalClearancePrevWeek3',
                         'MinutesInPriceStatusPromotionalClearancePrevWeek4',
                         'MinutesInPriceStatusPromotionalClearancePrevWeek5',
                         'MinutesInPriceStatusPromotionalClearancePrevWeek6',
                         'MinutesInPriceStatusPromotionalClearancePrevWeek7',
                         'MinutesInPriceStatusPromotionalClearancePrevWeek8',

                         'MinutesInPriceStatusFullPricePrevWeek2', 'MinutesInPriceStatusFullPricePrevWeek3',
                         'MinutesInPriceStatusFullPricePrevWeek4', 'MinutesInPriceStatusFullPricePrevWeek5',
                         'MinutesInPriceStatusFullPricePrevWeek6', 'MinutesInPriceStatusFullPricePrevWeek7',
                         'MinutesInPriceStatusFullPricePrevWeek8', 'MinutesInPriceStatusPromotionPrevWeek2',
                         'MinutesInPriceStatusPromotionPrevWeek3', 'MinutesInPriceStatusPromotionPrevWeek4',
                         'MinutesInPriceStatusPromotionPrevWeek5', 'MinutesInPriceStatusPromotionPrevWeek6',
                         'MinutesInPriceStatusPromotionPrevWeek7', 'MinutesInPriceStatusPromotionPrevWeek8',
                         'PriceFullPricePrevWeek2', 'PriceFullPricePrevWeek3', 'PriceFullPricePrevWeek4',
                         'PriceFullPricePrevWeek5', 'PriceFullPricePrevWeek6', 'PriceFullPricePrevWeek7',
                         'PriceFullPricePrevWeek8', 'PriceClearancePrevWeek2', 'PriceClearancePrevWeek3',
                         'PriceClearancePrevWeek4', 'PriceClearancePrevWeek5', 'PriceClearancePrevWeek6',
                         'PriceClearancePrevWeek7', 'PriceClearancePrevWeek8', 'PricePromotionPrevWeek2',
                         'PricePromotionPrevWeek3', 'PricePromotionPrevWeek4', 'PricePromotionPrevWeek5',
                         'PricePromotionPrevWeek6', 'PricePromotionPrevWeek7', 'PricePromotionPrevWeek8',
                         'MostRecentFullPricePrevWeek2', 'MostRecentFullPricePrevWeek3', 'MostRecentFullPricePrevWeek4',
                         'MostRecentFullPricePrevWeek5', 'MostRecentFullPricePrevWeek6', 'MostRecentFullPricePrevWeek7',
                         'MostRecentFullPricePrevWeek8', 'SoldUnitsPrevWeek2', 'SoldUnitsPrevWeek3',
                         'SoldUnitsPrevWeek4', 'SoldUnitsPrevWeek5', 'SoldUnitsPrevWeek6', 'SoldUnitsPrevWeek7',
                         'SoldUnitsPrevWeek8', 'SoldUnitsFullPricePrevWeek2', 'SoldUnitsFullPricePrevWeek3',
                         'SoldUnitsFullPricePrevWeek4', 'SoldUnitsFullPricePrevWeek5', 'SoldUnitsFullPricePrevWeek6',
                         'SoldUnitsFullPricePrevWeek7', 'SoldUnitsFullPricePrevWeek8', 'SoldUnitsPromotionPrevWeek2',
                         'SoldUnitsPromotionPrevWeek3', 'SoldUnitsPromotionPrevWeek4', 'SoldUnitsPromotionPrevWeek5',
                         'SoldUnitsPromotionPrevWeek6', 'SoldUnitsPromotionPrevWeek7', 'SoldUnitsPromotionPrevWeek8',
                         'SoldUnitsClearancePrevWeek2', 'SoldUnitsClearancePrevWeek3', 'SoldUnitsClearancePrevWeek4',
                         'SoldUnitsClearancePrevWeek5', 'SoldUnitsClearancePrevWeek6', 'SoldUnitsClearancePrevWeek7',
                         'SoldUnitsClearancePrevWeek8', 'CoverPrevWeek2', 'CoverPrevWeek3', 'CoverPrevWeek4',
                         'CoverPrevWeek5', 'CoverPrevWeek6', 'CoverPrevWeek7', 'CoverPrevWeek8',
                         'SaleableStockPrevWeek2', 'SaleableStockPrevWeek3', 'SaleableStockPrevWeek4',
                         'SaleableStockPrevWeek5', 'SaleableStockPrevWeek6', 'SaleableStockPrevWeek7',
                         'SaleableStockPrevWeek8', 'TradeableStockPrevWeek2', 'TradeableStockPrevWeek3',
                         'TradeableStockPrevWeek4', 'TradeableStockPrevWeek5', 'TradeableStockPrevWeek6',
                         'TradeableStockPrevWeek7', 'TradeableStockPrevWeek8', 'GlobalMaxTradeableSKUsPrevWeek2',
                         'GlobalMaxTradeableSKUsPrevWeek3', 'GlobalMaxTradeableSKUsPrevWeek4',
                         'GlobalMaxTradeableSKUsPrevWeek5', 'GlobalMaxTradeableSKUsPrevWeek6',
                         'GlobalMaxTradeableSKUsPrevWeek7', 'GlobalMaxTradeableSKUsPrevWeek8',
                         'GlobalSaleableStockPrevWeek2', 'GlobalSaleableStockPrevWeek3', 'GlobalSaleableStockPrevWeek4',
                         'GlobalSaleableStockPrevWeek5', 'GlobalSaleableStockPrevWeek6', 'GlobalSaleableStockPrevWeek7',
                         'GlobalSaleableStockPrevWeek8', 'GlobalTradeableStockPrevWeek2',
                         'GlobalTradeableStockPrevWeek3', 'GlobalTradeableStockPrevWeek4',
                         'GlobalTradeableStockPrevWeek5', 'GlobalTradeableStockPrevWeek6',
                         'GlobalTradeableStockPrevWeek7', 'GlobalTradeableStockPrevWeek8',
                         'ReplacementUnitsFullPricePrevWeek2', 'ReplacementUnitsFullPricePrevWeek3',
                         'ReplacementUnitsFullPricePrevWeek4', 'ReplacementUnitsFullPricePrevWeek5',
                         'ReplacementUnitsFullPricePrevWeek6', 'ReplacementUnitsFullPricePrevWeek7',
                         'ReplacementUnitsFullPricePrevWeek8', 'ReplacementUnitsPromotionPrevWeek2',
                         'ReplacementUnitsPromotionPrevWeek3', 'ReplacementUnitsPromotionPrevWeek4',
                         'ReplacementUnitsPromotionPrevWeek5', 'ReplacementUnitsPromotionPrevWeek6',
                         'ReplacementUnitsPromotionPrevWeek7', 'ReplacementUnitsPromotionPrevWeek8',
                         'ReplacementUnitsClearancePrevWeek2', 'ReplacementUnitsClearancePrevWeek3',
                         'ReplacementUnitsClearancePrevWeek4', 'ReplacementUnitsClearancePrevWeek5',
                         'ReplacementUnitsClearancePrevWeek6', 'ReplacementUnitsClearancePrevWeek7',
                         'ReplacementUnitsClearancePrevWeek8', 'ReturnCentresMaxTradeableSKUsPrevWeek2',
                         'ReturnCentresMaxTradeableSKUsPrevWeek3', 'ReturnCentresMaxTradeableSKUsPrevWeek4',
                         'ReturnCentresMaxTradeableSKUsPrevWeek5', 'ReturnCentresMaxTradeableSKUsPrevWeek6',
                         'ReturnCentresMaxTradeableSKUsPrevWeek7', 'ReturnCentresMaxTradeableSKUsPrevWeek8',
                         'ReturnCentresSaleableStockPrevWeek2', 'ReturnCentresSaleableStockPrevWeek3',
                         'ReturnCentresSaleableStockPrevWeek4', 'ReturnCentresSaleableStockPrevWeek5',
                         'ReturnCentresSaleableStockPrevWeek6', 'ReturnCentresSaleableStockPrevWeek7',
                         'ReturnCentresSaleableStockPrevWeek8', 'ReturnCentresTradeableStockPrevWeek2',
                         'ReturnCentresTradeableStockPrevWeek3', 'ReturnCentresTradeableStockPrevWeek4',
                         'ReturnCentresTradeableStockPrevWeek5', 'ReturnCentresTradeableStockPrevWeek6',
                         'ReturnCentresTradeableStockPrevWeek7', 'ReturnCentresTradeableStockPrevWeek8',
                         'VoidUnitsPrevWeek2', 'VoidUnitsPrevWeek3', 'VoidUnitsPrevWeek4', 'VoidUnitsPrevWeek5',
                         'VoidUnitsPrevWeek6', 'VoidUnitsPrevWeek7', 'VoidUnitsPrevWeek8',
                         'containedFullPricePrevWeek2', 'containedFullPricePrevWeek3', 'containedFullPricePrevWeek4',
                         'containedFullPricePrevWeek5', 'containedFullPricePrevWeek6', 'containedFullPricePrevWeek7',
                         'containedFullPricePrevWeek8', 'containedPromotionPrevWeek2', 'containedPromotionPrevWeek3',
                         'containedPromotionPrevWeek4', 'containedPromotionPrevWeek5', 'containedPromotionPrevWeek6',
                         'containedPromotionPrevWeek7', 'containedPromotionPrevWeek8', 'containedClearancePrevWeek2',
                         'containedClearancePrevWeek3', 'containedClearancePrevWeek4', 'containedClearancePrevWeek5',
                         'containedClearancePrevWeek6', 'containedClearancePrevWeek7', 'containedClearancePrevWeek8',
                         'ProductOptionCode', 'BusinessModelId', 'BusinessModelDescription',
                         'BuyingSummaryGroupDescription', 'BuyingSummarySubgroupDescription', 'BuyingGroupId',
                         'BuyingGroupDescription', 'BuyingSubGroupId', 'BuyingSubGroupDescription', 'BuyingDivisionId',
                         'BuyingDivisionDescription', 'GroupId', 'GroupDescription', 'ProductGroupId',
                         'ParentBuyingSubGroupDescription', 'DivisionDescription',
                         'ProductGroupDescription', 'CategoryId', 'CategoryDescription', 'SubcategoryId',
                         'SubCategoryDescription', 'StyleCode', 'StyleDescription', 'WebsiteColour', 'AsosColourId',
                         'AsosColourDescription', 'AsosColourGroupId', 'AsosColourGroupDescription',
                         'SupplierReference', 'BrandId', 'BrandDescription', 'BrandGroupId', 'BrandGroupDescription',
                         'SeasonalEvent', 'Flow', 'Range', 'RangeShopByFit', 'OutletStockType',
                         'BrandedSeasonalPlanningConcat', 'TotalSKUs', 'RetailSeason', 'isFlow',
                         'SoldUnitsPrevWeek2Daily', 'DepthPromotion', 'DepthPromotionRounded', 'PricePromotion',
                         'CurrentPrice', 'MinutesInPriceStatusClearance', 'MinutesInPriceStatusFullPrice',
                         'MinutesInPriceStatusPromotion', 'SoldUnits', 'SoldUnitsClearance', 'SoldUnitsFullPrice',
                         'SoldUnitsPromotion', 'SoldUnitsPromotionDaily', 'containedClearance', 'containedFullPrice',
                         'containedPromotion', 'containedPromotionalClearance',
                         'Year', 'WeekOfYear', 'WeekOfYearSin', 'WeekOfYearCos', 'MonthOfYear', 'MonthOfYearSin',
                         'MonthOfYearCos', 'WeekOfMonth', 'WeekOfMonthSin', 'WeekOfMonthCos'
                         ]

monitoring_preds = [
    'productId', 'ParentWarehouse', 'CalendarDateWeekly', 'CalendarDate',
    'MinutesInPriceStatusPromotion', 'ObservedDepth', 'MostRecentFullPrice', 'PricePromotion',
    'SoldUnits', 'CashMarginAbsoluteGBP', 'CashMarginAbsoluteGBPUnits', 'ForecastedLinkedDepth',
    'ForecastedSoldUnits', 'ForecastedCashMarginAbsoluteGBP', 'ForecastedCashMarginAbsoluteGBPUnits',
]

data_quality = ['period', 'first_date', 'last_date', 'n_rows', 'n_products',
                'promo_minutes_mean', 'promo_minutes_median',
                'promo_minutes_10pctile', 'promo_minutes_90pctile',
                'prop_date_level_row_has_forecast']

metrics = ['period', 'first_date', 'last_date', 'GroupType', 'GroupingVariables',
           'VariableLevels', 'SubsetQuery', 'n', 'metric', 'statistic', 'value']


def train_model_config() -> Dict:
    # Faster model
    test_model_config = copy.deepcopy(model_config)
    test_model_config['model_params']['model']['n_estimators'] = 3
    test_model_config['model_params']['model']['num_leaves'] = 3
    test_model_config['model_params']['model']['max_depth'] = 2

    # Less training data
    test_training_data_config = copy.deepcopy(training_data_config)
    test_training_data_config['n_weeks_data_training'] = 1

    # Shorter cross-validation
    test_validation_config = copy.deepcopy(validation_config)
    test_validation_config['cv_kwargs']['n_folds'] = 2
    test_validation_config['cv_kwargs']['n_dataslices_increment_per_step'] = 1
    test_validation_config['n_weeks_per_test'] = 1

    return {
        'model': test_model_config,
        'data': test_training_data_config,
        'validation': test_validation_config
    }
