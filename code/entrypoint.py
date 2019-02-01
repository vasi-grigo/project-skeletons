#!/usr/bin/env python3

import uvloop
import os
import asyncio
import logging
import ujson
import jsonschema
import jaeger_client
import time

from aiohttp import web
from app import pyskel
from app.configschema import schema

if __name__ == "__main__":
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()
    loglevel = os.getenv('LOG_LEVEL', logging.INFO)
    logging.basicConfig(level=loglevel)
    logging.getLogger("asyncio").setLevel(logging.ERROR)
    logging.getLogger("aiohttp").setLevel(logging.ERROR)
    logging.getLogger("jaeger_tracing").setLevel(logging.ERROR)
    logger = logging.getLogger(__name__)
    h = '0.0.0.0'

    # configuration
    api_port = os.environ['REST_PORT']
    metrics_port = os.environ['METRICS_PORT']
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

    # context
    ctx = pyskel.Ctx()

    # tracer
    jaeger = os.getenv("JAEGER")
    if jaeger:
        config = jaeger_client.Config(
            config={
                'sampler': {'type': 'const', 'param': 1},
                'logging': True,
            },
            service_name='pyskel',
            validate=True
        )
        ctx.tracer = config.initialize_tracer()

    # api server
    api = pyskel.Api(ctx, logger)
    logger.info("starting HTTP API on {h}:{api_port}".format(**locals()))
    runner = web.AppRunner(api.app)
    loop.run_until_complete(runner.setup())
    site = web.TCPSite(runner, h, api_port)
    loop.run_until_complete(site.start())

    # metrics server
    logger.info("starting metrics server on {h}:{metrics_port}".format(**locals()))
    m = pyskel.MetricsServer(host=h, port=metrics_port, logger=logger, ctx=ctx)
    loop.run_until_complete(m.start())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    logger.info('Shutting down')
    tasks = [
        asyncio.ensure_future(runner.cleanup),
        asyncio.ensure_future(api.stop),
        asyncio.ensure_future(m.stop)
    ]
    loop.run_until_complete(asyncio.gather(*tasks))
    loop.close()

    # allow for tracer to flush if enabled
    if ctx.tracer:
        time.sleep(2)
        ctx.tracer.close()