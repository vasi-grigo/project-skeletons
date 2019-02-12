import time

from aiohttp import web
from pyskull.common import ctx

routes = web.RouteTableDef()


@web.middleware
async def middleware(request, handler):
    flight, reqs, failed = ctx.profile_http
    api = str(request.rel_url)
    meta = {'api': api, 'method': str(request.method)}
    flight.inc(meta)
    start = time.perf_counter()

    # work
    try:
        if not ctx.tracer:
            resp = await handler(request)
        else:
            with ctx.tracer.start_span('{}'.format(api)) as span:
                span.set_tag('protocol', 'http')
                span.log_kv({'event': 'in'})
                ctx.tracer_current_span = span
                resp = await handler(request)
                span.log_kv({'event': 'out'})
    except Exception as e:
        # logging handled by aiohttp
        failed.inc(meta)
        raise e
    finally:
        flight.dec(meta)

    o = time.perf_counter() - start
    o *= 1000
    o = int(o)
    reqs.observe(meta, o)
    return resp


@routes.get('/hail/{name}')
async def hail(req: web.Request):
    name = req.match_info.get('name')
    if not name or name not in ['emperor', 'odin', 'shiva', 'zeus', 'ra']:
        raise web.HTTPBadRequest(text='Will not hail!')
    return web.Response(text="Hail, {}!".format(name))

middlewares = [middleware]
