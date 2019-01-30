#!/usr/bin/env python3

import uvloop
import os
import asyncio
import logging

from aiohttp import web
from app import pyskel

if __name__ == "__main__":
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()
    loglevel = os.getenv('LOG_LEVEL', logging.INFO)
    logging.basicConfig(level=loglevel)
    logging.getLogger("asyncio").setLevel(logging.ERROR)
    logging.getLogger("aiohttp").setLevel(logging.ERROR)
    logger = logging.getLogger(__name__)
    h = '0.0.0.0'

    # configuration
    api_port = os.environ['REST_PORT']
    metrics_port = os.environ['METRICS_PORT']

    # context
    ctx = pyskel.Ctx()

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