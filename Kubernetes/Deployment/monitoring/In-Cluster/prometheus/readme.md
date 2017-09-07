1. get prometheus config from [prometheus.yaml](https://raw.githubusercontent.com/prometheus/prometheus/master/documentation/examples/prometheus-kubernetes.yml)

2. this prometheus use influxdb as the storages, configure the influxdb in its conf `prometheus.yml`.  and one more container `remote-storage-adapter` is used to read/write data from/to influxdb.

3. set proper RBAC for  prometheus, since prometheus need to access api resources and objects.

4. since we use prometheus 2.0, we configure the alertmanager in its conf `prometheus.yml`

5. transform the `alert.rules` to `alert.rules.yml` using `promtool  update rules alert.rules`.