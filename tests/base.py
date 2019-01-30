import unittest
import os

check = os.getenv('TEST_SAFE')
if check != 'TheEmperorProtects':
    print('You are not worthy.')
    exit()


class BaseTest(unittest.TestCase):

    def helper(self):
        a = 1