import asyncio

from pyskull.common import api, PROFILE_HTTP
from random import randint
from aiohttp import web
from pyskull.common import ctx

routes = web.RouteTableDef()


@routes.get('/hello/{name}')
@api('/hello', PROFILE_HTTP)
async def hello(req: web.Request):
    if ctx.tracer_current_span:
        with ctx.tracer.start_span('blah', child_of=ctx.tracer_current_span) as child_span:
            ctx.tracer_current_span.log_kv({'from_blah': 'fooblah'})
            child_span.log_kv({'blah': 'blah blah'})
    await asyncio.sleep(0.05 + randint(0, 50) * 0.01)
    return web.Response(text="Hello, {}".format(req.match_info['name']))