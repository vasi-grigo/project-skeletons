import socket
import uuid
from aioprometheus import Counter, Gauge, Histogram, Service, Summary, formats

class ctx:
    def __init__(self):
        # Define some constant labels that need to be added to all metrics
        const_labels = {
            "host": socket.gethostname(),
            "app": f"{self.__class__.__name__}-{uuid.uuid4().hex}",
        }

        metrics = []

        self.metric_reqs = Counter("requests", "Requests served by route", const_labels=const_labels)
        metrics.append(self.metric_reqs)
        self.metric_reqs_in_flight = Gauge("requests_in_flight", "Number of requests being served.", const_labels=const_labels)
        metrics.append(self.metric_reqs_in_flight)
        self.metric_ram = Gauge("memory_usage_bytes", "Memory usage in bytes.", const_labels=const_labels)
        metrics.append(self.metric_ram)
        self.metric_cpu = Gauge("cpu_usage_percent", "CPU usage percent.", const_labels=const_labels)
        metrics.append(self.metric_cpu)

        self.metric_reqs_duration = Summary(
            "request_duration_ms",
            "Sum of all requests ms.",
            const_labels=const_labels,
            invariants=[(0.50, 0.05), (0.99, 0.001)],
        )
        metrics.append(self.metric_reqs_duration)

        self.metric_reqs_latency = Histogram(
            "request_latency_ms",
            "Request latency ms",
            const_labels=const_labels,
            buckets=[0.1, 0.5, 1.0, 5.0],
        )
        metrics.append(self.metric_reqs_latency)
        self.metrics = metrics

        self.cur_url = ''