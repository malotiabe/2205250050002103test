import datetime
import pandas as pd

from promotheus.preprocessing.dataframe_constructors import assemble_data_mix, get_forecasts_for_promo_via_serving_log


def test_assemble_data_mix_correct_output():

    df = pd.DataFrame({
        'MinutesInPriceStatusPromotion': [10, 0],
        'MinutesInPriceStatusFullPrice': [0, 10],
        'SoldUnitsPromotion': [10, 0],
        'SoldUnitsFullPrice': [0, 10],
        'PricePromotion': [9, 0],
        'MostRecentFullPrice': [10, 10],
        'DepthPromotion': [0.9, 1]
    })

    output = assemble_data_mix(
        df,
        prop_full_price=0.5,
        random_state=0
    )

    expected_output = pd.DataFrame({
        'MinutesInPriceStatusPromotion': [10, 10],
        'MinutesInPriceStatusFullPrice': [0, 10],
        'SoldUnitsPromotion': [10, 10],
        'SoldUnitsFullPrice': [0, 10],
        'PricePromotion': [9, 10],
        'MostRecentFullPrice': [10, 10],
        'DepthPromotion': [0.9, 0]
    })

    pd.testing.assert_frame_equal(output, expected_output)


def test_assemble_data_mix_correct_output_length_for_oversized_sample():

    df = pd.DataFrame({
        'MinutesInPriceStatusPromotion': [10, 0],
        'MinutesInPriceStatusFullPrice': [0, 10],
        'SoldUnitsPromotion': [10, 0],
        'SoldUnitsFullPrice': [0, 10],
        'PricePromotion': [9, 0],
        'MostRecentFullPrice': [10, 10],
        'DepthPromotion': [0.9, 1]
    })

    output = assemble_data_mix(
        df,
        prop_full_price=0.9,
        random_state=0
    )

    assert len(output) == 2


def _fake_forecast_loader(*args, **kwargs): return pd.DataFrame([
    [100, 'FC01 Barnsley', 4],
    [200, 'FC03 Atlanta', 5],
    [300, 'FC04 Berlin', 6],
], columns=['productId', 'ParentWarehouse', 'Forecast'])


def test_get_forecasts_for_promo_via_serving_log():

    # Function inputs
    serving_log = {
        "2021-10-18": {
            'model_run_id': None,
            "warehouse_forecast_mapping": [
                {
                    "warehouse": ["FC01 Barnsley", "FC04 Berlin"],
                    "forecast_filename": "predictions_all_depths_10080_minutes",
                    "forecast_n_days": 7
                },
                {
                    "warehouse": ["FC03 Atlanta"],
                    "forecast_filename": "predictions_all_depths_7200_minutes",
                    "forecast_n_days": 5
                }
            ]
        },
    }

    # Expected
    expected_batch_keys = ['target_rows_id_query', 'df_forecast', 'serving_log_batch']
    expected_queries = [
        "ParentWarehouse in ['FC01 Barnsley', 'FC04 Berlin']",
        "ParentWarehouse in ['FC03 Atlanta']",
    ]
    expected_df_forecasts = [
        pd.DataFrame([[100, 'FC01 Barnsley', 4], [300, 'FC04 Berlin', 6]],
                     columns=['productId', 'ParentWarehouse', 'Forecast']),
        pd.DataFrame([[200, 'FC03 Atlanta', 5]], columns=['productId', 'ParentWarehouse', 'Forecast'])
    ]

    # Execute
    out = get_forecasts_for_promo_via_serving_log(
        week_start_date=datetime.datetime(2021, 10, 18),
        serving_log=serving_log,
        forecast_loader=_fake_forecast_loader,
        forecast_file_template='promotheus/forecasts/{date:%Y%m%d}/{model_id}/' +
        'predictions_all_depths_{promo_minutes}_minutes.parquet',
    )

    # Checks
    assert not any([
        set(x.keys()) != set(expected_batch_keys)
        for x in out
    ]), 'Batch keys not as expected'
    assert not any([
        x['target_rows_id_query'] != expected_query
        for x, expected_query in zip(out, expected_queries)
    ]), "Batch queries not as expected"
    assert not any([
        (
            out['df_forecast']
            .reset_index(drop=False)
            .equals(
                expected.reset_index(drop=False)
            )
        )
        for out, expected in
        zip(out, expected_df_forecasts)
    ]), 'Forecasts are not divided up as expected'
