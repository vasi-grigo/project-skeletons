import os
from tests.base import BaseTest

# required to do a server shutdown after test completion
def load_tests(loader, standard_tests, pattern):
    this_dir = os.path.dirname(__file__)
    package_tests = loader.discover(start_dir=this_dir, pattern=pattern)
    standard_tests.addTests(package_tests)
    BaseTest.integration_test_count = package_tests.countTestCases()
    return standard_tests