import psutil, time, logging, pprint

from app.ctx import ctx
from random import randint
from aiohttp import web

routes = web.RouteTableDef()
class api:
    def __init__(self,logger:logging.Manager, ctx:ctx):
        self.app = web.Application(middlewares=[self.middleware_time])
        self.app.add_routes(routes)
        self.ctx = ctx
        self.app['ctx'] = ctx
        self.logger = logger

    @web.middleware
    async def middleware_time(self, app:web.Application, handler):
        start = time.time_ns()
        self.ctx.metric_reqs_in_flight.inc({})

        # ram gauge
        self.ctx.metric_ram.set({"type": "virtual"}, psutil.virtual_memory().used)
        self.ctx.metric_ram.set({"type": "swap"}, psutil.swap_memory().used)
        # cpu gauge
        for c, p in enumerate(psutil.cpu_percent(interval=1, percpu=True)):
            self.ctx.metric_cpu.set({"core": c}, p)

        # work
        resp = await handler(app)

        # counters
        self.ctx.metric_reqs.inc({"path": self.ctx.cur_url})
        self.ctx.metric_reqs.inc({})
        self.ctx.cur_url = ''

        # summary
        ms = time.time_ns() - start
        ms /= 1000000
        self.ctx.metric_reqs_duration.add({}, ms)

        # request finished
        self.ctx.metric_reqs_in_flight.sub({}, 1)

        return resp

    # catch all urls
    @routes.get('/{url:.*}')
    async def handle(req:web.Request):
        # simulate work
        req.app['ctx'].cur_url = req.rel_url.path
        time.sleep(0.05 + randint(0,50) * 0.01)
        return web.Response(text=req.rel_url.path)

    async def start(self):
        self.logger.info("API server started")

    async def stop(self):
        self.logger.info("API server stopped")