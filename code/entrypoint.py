#!/usr/bin/env python3

import uvloop
import os
import asyncio
import logging
import ujson
import jsonschema
import jaeger_client
import time
import signal

from pyskull.configschema import schema
from pyskull.common import ctx, MetricsServer


def main():
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()
    logging.basicConfig(level=os.getenv('LOG_LEVEL', logging.INFO))
    logging.getLogger("asyncio").setLevel(logging.ERROR)
    logging.getLogger("aiohttp").setLevel(logging.ERROR)
    logging.getLogger("jaeger_tracing").setLevel(logging.ERROR)
    logger = logging.getLogger(__name__)
    h = '0.0.0.0'

    # configuration
    config = os.getenv("CONFIG")
    if not config:
        raise EnvironmentError("no config file specified")
    if not os.path.exists(config):
        raise EnvironmentError("config file does not exist")
    logger.info("Reading configuration from {config}".format(**locals()))
    try:
        with open(config, "r") as cfg:
            config = ujson.load(cfg)
    except ValueError:
        raise EnvironmentError("could not parse config file")
    jsonschema.validate(config, schema)

    # tracer
    jport = os.getenv('JAEGER_AGENT_PORT')
    if jport:
        config = jaeger_client.Config(
            config={
                'sampler': {'type': 'const', 'param': 1},
                'logging': True,
            },
            service_name='pyskull',
            validate=True
        )
        ctx.tracer = config.initialize_tracer()
        logger.info("jaeger started against {}:{}".format(os.getenv('JAEGER_AGENT_HOST'), jport))

    # http api server
    runner = None
    api_port = os.environ['HTTP_PORT']
    if api_port:
        from pyskull.http import routes
        from aiohttp import web
        app = web.Application()
        app.add_routes(routes)
        runner = web.AppRunner(app)
        loop.run_until_complete(runner.setup())
        site = web.TCPSite(runner, h, int(api_port))
        loop.run_until_complete(site.start())
        logger.info("HTTP API started on {h}:{api_port}".format(**locals()))

    # grpc server
    gapi = None
    gport = os.getenv('GRPC_PORT')
    if gport:
        from pyskull import grpc as g
        from grpclib.server import Server
        gapi = Server([g.Greeter(ctx)], loop=loop)
        loop.run_until_complete(gapi.start('0.0.0.0', 50051))
        logger.info("gRPC started on {h}:{gport}".format(**locals()))

    # metrics server
    mserver = None
    metrics_port = os.environ['METRICS_PORT']
    if metrics_port:
        mserver = MetricsServer()
        loop.run_until_complete(mserver.start(h, metrics_port))
        logger.info("metrics started on {h}:{metrics_port}".format(**locals()))

    def killer(**kwargs):
        raise KeyboardInterrupt

    loop.add_signal_handler(signal.SIGINT, lambda: asyncio.ensure_future(killer()))
    loop.add_signal_handler(signal.SIGTERM, lambda: asyncio.ensure_future(killer()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info('shutting down')
        cleanup = []
        if runner:
            cleanup += [asyncio.ensure_future(runner.cleanup())]

        if gapi:
            gapi.close()
            cleanup += [asyncio.ensure_future(gapi.wait_closed())]

        if mserver:
            cleanup += [asyncio.ensure_future(mserver.stop())]

        loop.run_until_complete(asyncio.gather(*cleanup))
        loop.close()

        # allow for tracer to flush if enabled
        if ctx.tracer:
            time.sleep(2)
            ctx.tracer.close()


if __name__ == "__main__":
    main()