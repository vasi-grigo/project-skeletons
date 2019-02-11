import aiounittest
import os
import time
import subprocess

check = os.getenv('TEST_SAFE')
if check != 'TheEmperorProtects':
    print('You are not worthy.')
    exit()


class BaseTest(aiounittest.AsyncTestCase):

    integration_test_count = None
    integration_test_current = 0

    inited = False
    p = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if BaseTest.inited:
            return
        BaseTest.p = subprocess.Popen(["/opt/app/entrypoint.py", "&"])
        time.sleep(2)
        BaseTest.inited = True

    def tearDown(self):
        super().tearDown()

        # no info on number of tests so likely manual cleanup required
        if BaseTest.integration_test_count is None:
            return

        # check it's an integration test case
        if 'integration' in self.__class__.__module__:
            BaseTest.integration_test_current += 1

        # not initialized or not all tests have been run yet
        if not BaseTest.inited or BaseTest.integration_test_current < BaseTest.integration_test_count:
            return

        self.cleanup()

    @classmethod
    def cleanup(cls):
        BaseTest.p.terminate()
        BaseTest.p.wait()
        BaseTest.p = None
        BaseTest.inited = False
