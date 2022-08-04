
import pandas as pd
import pandas.testing as pdt
import numpy as np
from promotheus.utils.experiments import (
    power_statslib, get_power_curve_independent_samples
)


def test_output_all_statslib_methods():
    '''
        Tests output format for all stats methods. This will ensure that
        any new tests comply with expected library format.
    '''

    # Fetch all (stats) methods that need testing
    all_stats_methods = [
        method_name
        for method_name in dir(power_statslib)
        if (
            callable(getattr(power_statslib, method_name))
            & (method_name[0] != "_")
        )
    ]

    # Input to stats methods
    nMonteCarloSamples = 100
    nUnits_Test = 30
    y_test, y_control = np.random.rand(nMonteCarloSamples, nUnits_Test), \
        np.random.rand(nMonteCarloSamples, nUnits_Test)

    for method in all_stats_methods:
        vec_stats, vec_p = getattr(power_statslib, method)(y_test, y_control)

        assert vec_stats.ndim == vec_p.ndim == 1, \
            f"[power statslib.{method}] all stats methods should return a " + \
            "single tuple containing two 1D vectors (statistic, pval) "
        assert len(vec_stats) == len(vec_p) == nMonteCarloSamples, \
            f"[power statslib.{method}] returned stats / pval vectors " + \
            "length should = nMonteCarloSamples"


def test_get_power_curve_independent_samples():

    # Test config
    np.random.seed(100)
    nUnitsMax = 50
    df_out = pd.DataFrame({'sample_size': {0: 50, 1: 50},
                           'change_percentage': {0: 0, 1: 99},
                           'prop_dataset_in_test': {0: 0.5, 1: 0.5},
                           'prop_significant': {0: 0.054, 1: 0.0295}
                           })

    # Execute call
    y_all = pd.Series(np.random.normal(0, 1, nUnitsMax))
    df = get_power_curve_independent_samples(data=y_all,
                                             SampleSizes=[nUnitsMax],
                                             change_percentages=[0, 99],
                                             nMonteCarloSamples=1000
                                             )

    # Assert outputs
    _cols = ['sample_size', 'change_percentage',
             'prop_dataset_in_test', 'prop_significant']
    pdt.assert_frame_equal(df[_cols], df_out)
