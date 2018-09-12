# py-aio-prom-jaeger

Python server that:
- exposes a REST API using **aiohttp** that accepts requests for any routes
- exposes metrics using **prometheus_client**; metrics are updated each second
(it takes some ~ 18 ms to update counters, hence updating is moved to a periodic task as prometheus 
scrapes every 5secs at best)
- uses multistage docker build so as not to bloat with g++ and others
- uses **siege** to simulate load on http
- integrated with **jaeger** for distributed tracing (WIP)
- loads in a json config and uses **jsonschema** to validate it (WIP)
- scaffolding for unit/integration tests (WIP)
- **helm** chart to install into k8s (and make prometheus scrape the service)

## Usage

```bash
# local
docker/build.sh # build
docker-compose -f docker/local-compose.yml up # start

# k8s
helm install chart/py-aio-prom-jaeger --name my-app
```