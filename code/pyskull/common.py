import socket
import time


class Ctx:
    def __init__(self):
        self.tracer = None
        self.tracer_current_span = None


ctx = Ctx()

from aioprometheus import Counter, Gauge, Histogram, Service, formats

PROFILE_GRPC = 'grpc'
PROFILE_HTTP = 'http'
const_labels = {
    'pod': socket.gethostname()  # corresponds to pod name
}
profiles = {
    'grpc': (
        Gauge('grpc_requests_in_flight', 'Number of gRPC requests being served.', const_labels=const_labels),
        Histogram(
            'grpc_requests',
            'Histogram of gRPC request latencies in milliseconds',
            const_labels=const_labels,
            buckets=[30, 50, 100, 200],
        ),
        Counter('grpc_requests_failed', 'Number of failed gRPC requests', const_labels=const_labels)
    ),
    'http': (
        Gauge('http_requests_in_flight', 'Number of HTTP requests being served.', const_labels=const_labels),
        Histogram(
            'http_requests',
            'Histogram of HTTP request latencies in milliseconds',
            const_labels=const_labels,
            buckets=[50, 100, 200, 1000],
        ),
        Counter('http_requests_failed', 'Number of failed HTTP requests', const_labels=const_labels)
    )
}


def api(name, profile):
    flight, reqs, failed = profiles[profile]

    def decorator(func):
        def wrapper(*args, **kwargs):
            meta = {'api': name}
            flight.inc(meta)
            start = time.perf_counter()

            # work
            if not ctx.tracer:
                try:
                    result = func(*args, **kwargs)
                except:
                    flight.dec(meta)
                    failed.inc(meta)
                    raise
            else:
                # handle with trace
                try:
                    with ctx.tracer.start_span('{}'.format(name)) as span:
                        span.set_tag('protocol', profile)
                        span.log_kv({'event': 'in'})
                        ctx.tracer_current_span = span
                        result = func(*args, **kwargs)
                        span.log_kv({'event': 'out'})
                except:
                    flight.dec(meta)
                    failed.inc(meta)
                    raise

            o = time.perf_counter() - start
            o *= 1000
            o = int(o)
            flight.dec(meta)
            reqs.observe(meta, o)
            return result

        return wrapper

    return decorator


class MetricsServer(object):

    def __init__(self):
        self.msvr = Service()

    async def start(self, host: str, port: int):
        metrics = []
        metrics += list(profiles[PROFILE_HTTP])
        metrics += list(profiles[PROFILE_GRPC])
        # attach metrics
        for m in metrics:
            self.msvr.register(m)
        await self.msvr.start(addr=host, port=port)

    async def stop(self):
        await self.msvr.stop()