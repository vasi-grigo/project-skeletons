#!/usr/bin/env python3

import mock
import unittest
import aiohttp
import aioprometheus

from tests.base import BaseTest

from pyskull.common import ctx
from pyskull.http import middleware


class HttpClientTest(BaseTest):

    @mock.patch('aioprometheus.collectors.Counter')
    @mock.patch('aioprometheus.collectors.Histogram')
    @mock.patch('aioprometheus.collectors.Gauge')
    @mock.patch('aiohttp.web.Request', rel_url='foo', method='bar')
    async def test_middleware(self, req, flight, req_hist, failed):
        # inject mocks
        aa, bb, cc = ctx.profile_http
        ctx.profile_http = (flight, req_hist, failed)

        async def success(r):
            self.assertEqual(req, r)

        await middleware(req, success)
        meta = {'api': req.rel_url, 'method': req.method}
        self.assertDictEqual(meta, flight.inc.call_args[0][0])
        self.assertDictEqual(meta, flight.dec.call_args[0][0])
        self.assertDictEqual(meta, req_hist.observe.call_args[0][0])
        failed.inc.assert_not_called()
        flight.reset_mock()
        req_hist.reset_mock()

        async def fail(r):
            self.assertEqual(req, r)
            raise aiohttp.web.HTTPBadRequest(text='blowup')

        try:
            await middleware(req, fail)
        except:
            pass
        self.assertDictEqual(meta, flight.inc.call_args[0][0])
        self.assertDictEqual(meta, flight.dec.call_args[0][0])
        req_hist.observe.assert_not_called()
        self.assertDictEqual(meta, failed.inc.call_args[0][0])

        ctx.profile_http = (aa, bb, cc)  # revert mocks

    async def test_http(self):
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:80/hail/horus') as resp:
                self.assertEqual(400, resp.status)
            async with session.get('http://localhost:80/hail/emperor') as resp:
                self.assertEqual(200, resp.status)
                self.assertEqual('Hail, emperor!', await resp.text())


if __name__ == '__main__':
    unittest.main(exit=False)
    BaseTest.cleanup()