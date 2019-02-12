#!/usr/bin/env python3

import mock
import unittest
import asyncio
import aioprometheus

from pyskull.common import ctx
from pyskull.grpc import middleware

from tests.base import BaseTest
from grpclib.client import Channel

import pyskull_pb2
import pyskull_grpc


class GrpcClientTest(BaseTest):

    @mock.patch('aioprometheus.collectors.Counter')
    @mock.patch('aioprometheus.collectors.Histogram')
    @mock.patch('aioprometheus.collectors.Gauge')
    async def test_middleware(self, flight, req_hist, failed):
        # inject mocks
        aa, bb, cc = ctx.profile_grpc
        ctx.profile_grpc = (flight, req_hist, failed)

        @middleware
        async def foobarbaz(a, b):
            return 1

        actual = await foobarbaz(1, 2)
        self.assertEqual(1, actual)
        meta = {'api': 'foobarbaz'}
        self.assertDictEqual(meta, flight.inc.call_args[0][0])
        self.assertDictEqual(meta, flight.dec.call_args[0][0])
        self.assertDictEqual(meta, req_hist.observe.call_args[0][0])
        failed.inc.assert_not_called()
        flight.reset_mock()
        req_hist.reset_mock()

        @middleware
        async def fail(a, b):
            raise Exception('boom')

        try:
            await fail(1, 2)
        except:
            pass
        meta = {'api': 'fail'}
        self.assertDictEqual(meta, flight.inc.call_args[0][0])
        self.assertDictEqual(meta, flight.dec.call_args[0][0])
        req_hist.observe.assert_not_called()
        self.assertDictEqual(meta, failed.inc.call_args[0][0])
        ctx.profile_grpc = (aa, bb, cc)  # revert mocks

    async def test_grpc(self):
        channel = Channel('127.0.0.1', 50051, loop=asyncio.get_event_loop())
        stub = pyskull_grpc.GreeterStub(channel)
        response = await stub.Hail(pyskull_pb2.HailRequest(name='horus'))
        self.assertEqual('Will not hail!', response.message)
        self.assertEqual(1, response.code)
        response = await stub.Hail(pyskull_pb2.HailRequest(name='emperor'))
        self.assertEqual('Hail, emperor!', response.message)
        self.assertEqual(0, response.code)
        channel.close()


if __name__ == '__main__':
    unittest.main(exit=False)
    BaseTest.cleanup()