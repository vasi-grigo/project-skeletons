#!/usr/bin/env python3

import unittest
import asyncio
import aiohttp

from tests.base import BaseTest
from grpclib.client import Channel

from pyskull_pb2 import HelloRequest
from pyskull_grpc import GreeterStub

class ClientTest(BaseTest):

    async def test_grpc(self):
        channel = Channel('127.0.0.1', 50051, loop=asyncio.get_event_loop())
        stub = GreeterStub(channel)
        response = await stub.SayHello(HelloRequest(name='World'))
        channel.close()
        self.assertEqual('Hello, World!', response.message)

    async def test_http(self):
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:80/foo') as resp:
                self.assertEqual(404, resp.status)
            async with session.get('http://localhost:80/hello/world') as resp:
                self.assertEqual(200, resp.status)
                self.assertEqual('Hello, world', await resp.text())


if __name__ == '__main__':
    unittest.main(exit=False)
    BaseTest.cleanup()