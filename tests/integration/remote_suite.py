import unittest

from tests.integration.test_forecast_optimize import ForecastOptimizeTest
from tests.integration.test_model_training import ModelTrainingTest
from tests.integration.test_monitoring import MonitoringTest
from tests.integration.test_preprocessing import PreprocessingTest
from tests.integration.test_ithax import IthaxTests

def run_remote_test_suite():
    print('Beginning remote run for integration tests.')
    # Add new test classes to run on remote here
    test_classes_to_run = [
        ForecastOptimizeTest,
        MonitoringTest,
        PreprocessingTest,
        IthaxTests,
        ModelTrainingTest
    ]

    loader = unittest.TestLoader()

    suites_list = []
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites_list.append(suite)
        
    remote_test_suite = unittest.TestSuite(suites_list)

    runner = unittest.TextTestRunner(verbosity=2)
    results = runner.run(remote_test_suite)
    if not results.wasSuccessful():
        raise RuntimeError("One or more tests failed. Please check job logs for additional information.")


if __name__ == "__main__":
    run_remote_test_suite()
