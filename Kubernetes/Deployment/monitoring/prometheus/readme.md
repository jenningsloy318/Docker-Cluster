1. get prometheus config from [prometheus.yaml](https://raw.githubusercontent.com/prometheus/prometheus/master/documentation/examples/prometheus-kubernetes.yml)
2. create configmap to accommodate   config and altermanager templates
  ```
  kubectl create configmap prometheus --from--file=prometheus.yml
  kubectl create configmap alertmanager --from--file=alertmanager.yml
  kubectl create configmap alertmanager-templates --from--file=default.tmpl
  ```
3. get node-exporter from https://github.com/prometheus/node_exporter/releases/download/v0.14.0/node_exporter-0.14.0.linux-amd64.tar.gz