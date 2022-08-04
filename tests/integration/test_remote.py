import unittest


class RemoteIntegrationTest(unittest.TestCase):
    # Executes before tests in this class are run
    def setUp(self):
        # Test setup code...
        pass

    def test_foo_on_remote(self):

        foo = 'bar'

        self.assertEqual(foo, 'bar')

    # Executes after tests in this class are run
    def tearDown(self):
        # Test cleanup code...
        pass
