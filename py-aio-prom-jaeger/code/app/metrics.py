
import logging

from aioprometheus import Service
from aiohttp import web
from app.ctx import ctx

routes = web.RouteTableDef()

class metrics(object):
    def __init__(self, ctx:ctx, host:str, port:int,logger:logging.Manager):
        self.msvr = Service()
        self.host = host
        self.port = port
        self.logger = logger
        self.ctx = ctx
        # attach metrics
        for m in ctx.metrics:
            self.msvr.register(m)

    async def start(self):
        """ Start the application """
        await self.msvr.start(addr=self.host, port=self.port)
        self.logger.info('metrics server started')

    async def stop(self):
        """ Stop the application """
        await self.msvr.stop()
        self.logger.info('metrics server stopped')