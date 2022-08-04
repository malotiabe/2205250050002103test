import json
import pytest
import pandas as pd

from promotheus.preprocessing.utils import get_column_total_over_price_status, inject_transformer_kwargs


def _jsonify_mixed_object(x):
    return json.dumps(x, sort_keys=True)


def test_inject_transformer_kwargs_empty_initial_kwargdict():

    instructions = ('TransformerName', {})
    new_kwargs = {'you': 'should', 'do': 'this'}
    expected = (instructions[0], new_kwargs)

    out = inject_transformer_kwargs(
        instructions,
        new_kwargs
    )

    assert _jsonify_mixed_object(out) == _jsonify_mixed_object(expected)


def test_inject_transformer_kwargs_empty_add_to_kwargdict():

    instructions = ('TransformerName', {'do': 'i', 'have': 'to'})
    new_kwargs = {'you': 'should', 'get': 'it'}
    out = inject_transformer_kwargs(
        instructions,
        new_kwargs
    )

    expected_new_kwargs = new_kwargs.copy()
    expected_new_kwargs.update(instructions[1])
    expected = (instructions[0], expected_new_kwargs)

    assert _jsonify_mixed_object(out) == _jsonify_mixed_object(expected)


def test_inject_transformer_kwargs_empty_detect_key_clash():

    instructions = ('TransformerName', {'do': 'i', 'have': 'to'})
    new_kwargs = {'you': 'should', 'do': 'this'}

    with pytest.raises(ValueError):
        inject_transformer_kwargs(
            instructions,
            new_kwargs
        )


def test_get_column_total_over_price_status_expected_output():

    df = pd.DataFrame({
        'TestFullPricePrevWeek1': [1, 2],
        'TestClearancePrevWeek1': [3, 4],
        'TestPromotionPrevWeek1': [5, 6]
    })
    expected_output = pd.Series([9, 12])
    output = get_column_total_over_price_status(
        df=df, column='Test', prev_week=1)

    pd.testing.assert_series_equal(output, expected_output)


def test_get_column_total_over_price_status_raises_error_for_missing_column():

    df = pd.DataFrame({
        'TestFullPricePrevWeek1': [1, 2],
        'TestClearancePrevWeek1': [3, 4]
    })

    with pytest.raises(ValueError):
        get_column_total_over_price_status(
            df=df, column='Test', prev_week=1)
