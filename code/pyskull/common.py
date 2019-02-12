import socket
from aioprometheus import Counter, Gauge, Histogram, Service, formats

class Ctx:
    def __init__(self):
        self.tracer = None
        self.tracer_current_span = None
        self.profile_grpc = None
        self.profile_http = None

ctx = Ctx()
const_labels = {
    'pod': socket.gethostname()  # corresponds to pod name
}
ctx.profile_grpc = (
    Gauge('grpc_requests_in_flight', 'Number of gRPC requests being served.', const_labels=const_labels),
    Histogram(
        'grpc_requests',
        'Histogram of gRPC request latencies in milliseconds',
        const_labels=const_labels,
        buckets=[30, 50, 100, 200],
    ),
    Counter('grpc_requests_failed', 'Number of failed gRPC requests', const_labels=const_labels)
)
ctx.profile_http = (
    Gauge('http_requests_in_flight', 'Number of HTTP requests being served.', const_labels=const_labels),
    Histogram(
        'http_requests',
        'Histogram of HTTP request latencies in milliseconds',
        const_labels=const_labels,
        buckets=[50, 100, 200, 1000],
    ),
    Counter('http_requests_failed', 'Number of failed HTTP requests', const_labels=const_labels)
)

class MetricsServer(object):

    def __init__(self):
        self.msvr = Service()

    async def start(self, host: str, port: int):
        metrics = []
        metrics += list(ctx.profile_http)
        metrics += list(ctx.profile_grpc)
        # attach metrics
        for m in metrics:
            self.msvr.register(m)
        await self.msvr.start(addr=host, port=port)

    async def stop(self):
        await self.msvr.stop()