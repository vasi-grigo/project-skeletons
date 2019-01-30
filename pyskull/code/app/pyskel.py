import time
import logging
import asyncio
import socket

from random import randint
from aiohttp import web
from aioprometheus import Gauge, Histogram, Service, formats

routes = web.RouteTableDef()


class Ctx:
    def __init__(self):
        self.m_reqs_in_flight = 0
        self.m_reqs = []


class Api:
    def __init__(self, ctx: Ctx, logger=None):
        self.app = web.Application(middlewares=[self.middleware_time])
        self.app.add_routes(routes)

        self.logger = logger or logging.getLogger(__name__)
        self.ctx = ctx

    @web.middleware
    async def middleware_time(self, app:web.Application, handler):
        start = time.perf_counter()
        self.ctx.m_reqs_in_flight += 1

        # work
        resp, url = await handler(app)

        # gauge
        self.ctx.m_reqs_in_flight -= 1

        # histogram
        o = time.perf_counter() - start
        o *= 1000
        o = int(o)
        self.ctx.m_reqs.append((o, url))
        return resp

    # catch all urls
    @routes.get('/{url:.*}')
    async def handle(req:web.Request):
        await asyncio.sleep(0.05 + randint(0,50) * 0.01)
        return web.Response(text=req.rel_url.path), req.rel_url.path

    async def start(self):
        self.logger.info("API server started")

    async def stop(self):
        self.logger.info("API server stopped")


class MetricsServer(object):

    def __init__(self, host: str, port: int, ctx: Ctx, logger=None):
        self.msvr = Service()
        self.host = host
        self.port = port
        self.logger = logger or logging.getLogger(__name__)
        self.ctx = ctx

        # Define some constant labels that need to be added to all metrics
        const_labels = {
            "pod": socket.gethostname() # corresponds to pod name
        }

        metrics = []
        self.metric_reqs_in_flight = Gauge("app_requests_in_flight", "Number of requests being served.", const_labels=const_labels)
        metrics.append(self.metric_reqs_in_flight)

        self.metric_reqs = Histogram(
            "app_requests",
            "Histogram of request latencies in milliseconds",
            const_labels=const_labels,
            buckets=[50, 100, 150, 300, 500, 1000],
        )
        metrics.append(self.metric_reqs)

        # attach metrics
        for m in metrics:
            self.msvr.register(m)

    async def tick(self):
        """ Updates the cpu and mem percent on the counters """
        # counters
        self.metric_reqs_in_flight.set({}, self.ctx.m_reqs_in_flight)

        # histograms
        while len(self.ctx.m_reqs):
            p = self.ctx.m_reqs.pop()
            self.metric_reqs.add({'api':p[1]}, p[0])

        await asyncio.sleep(0.5)
        asyncio.get_event_loop().create_task(self.tick())

    async def start(self):
        """ Start the application """
        await self.msvr.start(addr=self.host, port=self.port)
        loop = asyncio.get_event_loop()
        loop.create_task(self.tick())
        self.logger.info('metrics server started')

    async def stop(self):
        """ Stop the application """
        await self.msvr.stop()
        self.logger.info('metrics server stopped')