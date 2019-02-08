import aiounittest
import os
import asyncio

check = os.getenv('TEST_SAFE')
if check != 'TheEmperorProtects':
    print('You are not worthy.')
    exit()


class BaseTest(aiounittest.AsyncTestCase):

    def helper(self):
        a = 1