
import logging
import asyncio
import socket
import uuid

from app.ctx import ctx
from aioprometheus import Gauge, Histogram, Service, formatsgit status

class metrics(object):
    def __init__(self, host:str, port:int, logger:logging.Manager, ctx:ctx):
        self.msvr = Service()
        self.host = host
        self.port = port
        self.logger = logger
        self.ctx = ctx

        # Define some constant labels that need to be added to all metrics
        const_labels = {
            "host": socket.gethostname(),
            "app": f"{self.__class__.__name__}-{uuid.uuid4().hex}",
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