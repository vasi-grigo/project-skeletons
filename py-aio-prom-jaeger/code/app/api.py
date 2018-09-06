import time, logging, pprint, asyncio

from app.ctx import ctx
from random import randint
from aiohttp import web

routes = web.RouteTableDef()
class api:
    def __init__(self, logger:logging.Manager, ctx:ctx):
        self.app = web.Application(middlewares=[self.middleware_time])
        self.app.add_routes(routes)
        self.logger = logger
        self.ctx = ctx

    @web.middleware
    async def middleware_time(self, app:web.Application, handler):
        start = time.time_ns()
        self.ctx.m_reqs_in_flight += 1

        # work
        resp, url = await handler(app)

        # gauge
        self.ctx.m_reqs_in_flight -= 1

        # counters
        self.ctx.m_reqs_count[url] = self.ctx.m_reqs_count[url] + 1 if url in self.ctx.m_reqs_count else 1

        # histogram
        ms = time.time_ns() - start
        ms /= 1000000
        self.ctx.m_reqs_duration.append(ms)
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