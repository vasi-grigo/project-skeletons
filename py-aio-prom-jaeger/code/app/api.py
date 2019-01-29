import time
import logging
import asyncio

from app.ctx import ctx
from random import randint
from aiohttp import web

routes = web.RouteTableDef()
class api:
    def __init__(self, ctx: ctx, logger=None):
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