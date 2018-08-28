# py-aio-prom-jaeger

Python server that:
- exposes a REST API using **aiohttp** that accepts requests for any routes
- increments and tracks metrics (while waiting a random interval to  create some vibration)
- exposes metrics using **prometheus_client**
- uses multistage docker build so as not to bloat with g++ and others
- integrated with **jaeger** for distributed tracing (WIP)
- loads in a json config and uses **jsonschema** to validate it (WIP)
- scaffolding for unit/integration tests (WIP)

## Usage

```bash
docker/build.sh # build
docker-compose -f docker/local-compose.yml up # start
```