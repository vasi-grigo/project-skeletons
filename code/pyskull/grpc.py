import time
import pyskull_grpc
import pyskull_pb2
from pyskull.common import ctx


def middleware(func):
    flight, reqs, failed = ctx.profile_grpc
    api = func.__name__

    async def wrapped(self, stream):
        meta = {'api': api}
        flight.inc(meta)
        start = time.perf_counter()

        # work
        try:
            if not ctx.tracer:
                resp = await func(self, stream)
            else:
                with ctx.tracer.start_span('{}'.format(api)) as span:
                    span.set_tag('protocol', 'grpc')
                    span.log_kv({'event': 'in'})
                    ctx.tracer_current_span = span
                    resp = await func(self, stream)
                    span.log_kv({'event': 'out'})
        except Exception as e:
            failed.inc(meta)
            raise e
        finally:
            flight.dec(meta)

        o = time.perf_counter() - start
        o *= 1000
        o = int(o)
        reqs.observe(meta, o)
        return resp
    return wrapped


class Greeter(pyskull_grpc.GreeterBase):

    @middleware
    async def Hail(self, stream):
        if ctx.tracer_current_span:
            with ctx.tracer.start_span('blah', child_of=ctx.tracer_current_span) as child_span:
                ctx.tracer_current_span.log_kv({'from_blah': 'fooblah'})
                child_span.log_kv({'blah': 'blah blah'})

        request = await stream.recv_message()
        name = request.name
        message = 'Will not hail!'
        code = 1
        if name in ['emperor', 'odin', 'shiva', 'zeus', 'ra']:
            message = f'Hail, {request.name}!'
            code = 0
        await stream.send_message(pyskull_pb2.HailResponse(message=message,code=code))
