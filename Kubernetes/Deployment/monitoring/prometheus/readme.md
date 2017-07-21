1. get prometheus config from [prometheus.yaml](https://raw.githubusercontent.com/prometheus/prometheus/master/documentation/examples/prometheus-kubernetes.yml)
2. create configmap to accommodate prometheus config
  ```
  kubectl create configmap prometheus.yml --from--file=prometheus.yml
  ```
