1. get prometheus config from [prometheus.yaml](https://raw.githubusercontent.com/prometheus/prometheus/master/documentation/examples/prometheus-kubernetes.yml)
2. create configmap to accommodate altermanager templates.
  ```
  kubectl create configmap alertmanager-templates --from-file=default.tmpl -n monitoring
  ```

3. get node-exporter from https://github.com/prometheus/node_exporter/releases/download/v0.14.0/node_exporter-0.14.0.linux-amd64.tar.gz

4. this prometheus use influxdb as the storages, hence set `'-storage.local.engine=none'` and configure the influxdb in its conf `prometheus.yml`.  and one more container `remote-storage-adapter` is used to read/write data from/to influxdb.

5. set proper RBAC for  prometheus, since prometheus need to access api resources and objects.