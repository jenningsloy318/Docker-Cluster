1. get prometheus config from [prometheus.yaml](https://raw.githubusercontent.com/prometheus/prometheus/master/documentation/examples/prometheus-kubernetes.yml)
2. create configmap to accommodate prometheus config
  ```
  kubectl create configmap prometheus.yml --from--file=prometheus.yml
  ```
3. get node-exporter from https://github.com/prometheus/node_exporter/releases/download/v0.14.0/node_exporter-0.14.0.linux-amd64.tar.gz