# pyskull

Basic python application skeleton with the common bells and whistles:
- HTTP, gRPC support
- prometheus metrics
- opentracing via jaeger
- dockerized
- helm charts
- reduced bullshit

### Usage

```bash
# local
docker/build.sh # build the image, rebuild protos and copy over
docker-compose -f docker/local-compose.yml up # start stuff locally

# run tests
docker exec pyskull python3 -m unittest discover /opt/tests/
```

### K8S
```
# install prometheus (use the offical helm repo to get the manifests)
helm install stable/prometheus --name prometheus --namespace monitoring

# if running a local cluster, make sure your metric server has certain flags
stable/metrics-server/values.yaml:
...
args:
   - --logtostderr
   - --kubelet-insecure-tls # <- this
...

# start the metrics server
helm install stable/metrics-server --name metrics-server --namespace monitoring

# tweak prometheus-adapter configuration:
...
rules:
  default: false
  custom:
  - seriesQuery: '{__name__=~"http_requests_count",pod!="",kubernetes_namespace!=""}'
    resources:
      overrides:
        kubernetes_namespace: {resource: "namespace"}
        pod: {resource: "pod"}
    name:
      matches: ".*"
      as: "avg_requests"
    metricsQuery: 'sum(irate(<<.Series>>{<<.LabelMatchers>>}[2m])) by (<<.GroupBy>>)'
...

# start the adapter
helm install stable/prometheus-adapter --name prometheus-adapter --namespace monitoring

# finally, start the application
helm install chart/pyskull --name my-app

# add load and see it scale ...
```

### Debugging tips
1. Check the logs of the metrics-server
2. Check the logs of the prometheus-adapter and toggle the logging level to 6
3. Make sure that the adapter is able to list the data from prometheus, i.e.:
    ```bash
    I0917 14:50:59.304159       1 round_trippers.go:405] GET https://10.96.0.1:443/api/v1/namespaces/default/pods?labelSelector=app%3Dpyskull%2Crelease%3Dmy-app 200 OK in 3 milliseconds
    # GET is succesful
    ```
4. Make sure that the custom metric is available:
    ```bash
    kubectl get --raw /apis/custom.metrics.k8s.io/v1beta1/namespaces/default/pods/*/avg_requests
    ```
    Yields:
    ```json
    {
      "kind": "MetricValueList",
      "apiVersion": "custom.metrics.k8s.io/v1beta1",
      "metadata": {
        "selfLink": "/apis/custom.metrics.k8s.io/v1beta1/namespaces/default/pods/%2A/avg_requests"
      },
      "items": [
        {
          "describedObject": {
            "kind": "Pod",
            "namespace": "default",
            "name": pyskull,
            "apiVersion": "/__internal"
          },
          "metricName": "avg_requests",
          "timestamp": "2018-09-17T14:51:21Z",
          "value": "3604m"
        },
        {
          "describedObject": {
            "kind": "Pod",
            "namespace": "default",
            "name": pyskull,
            "apiVersion": "/__internal"
          },
          "metricName": "avg_requests",
          "timestamp": "2018-09-17T14:51:21Z",
          "value": "3287m"
        },
        {
          "describedObject": {
            "kind": "Pod",
            "namespace": "default",
            "name": pyskull,
            "apiVersion": "/__internal"
          },
          "metricName": "avg_requests",
          "timestamp": "2018-09-17T14:51:21Z",
          "value": "3353m"
        },
        {
          "describedObject": {
            "kind": "Pod",
            "namespace": "default",
            "name": pyskull,
            "apiVersion": "/__internal"
          },
          "metricName": "avg_requests",
          "timestamp": "2018-09-17T14:51:21Z",
          "value": "3070m"
        }
      ]
    }
    ```
5. Finally, troubleshoot HPA:
    ```bash
    kubectl describe hpa
    kubectl get hpa
    ```