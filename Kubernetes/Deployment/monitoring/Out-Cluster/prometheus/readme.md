1. get prometheus config from [prometheus.yaml](https://raw.githubusercontent.com/prometheus/prometheus/master/documentation/examples/prometheus-kubernetes.yml)

2. this prometheus use influxdb as the storages, configure the influxdb in its conf `prometheus.yml`.  and using  `remote-storage-adapter` is used to read/write data from/to influxdb.

3. set proper RBAC for  prometheus, since prometheus need to access api resources and objects, export the token from kubernetes cluster and configure it here.

4. since we use prometheus 2.0, we configure the alertmanager in its conf `prometheus.yml`

5. transform the `alert.rules` to `alert.rules.yml` using `promtool  update rules alert.rules`.

6. remember to copy directory of `console_libraries` and `consoles` to `/etc/prometheus/`.

7. we can reference the prometheus documents at  https://github.com/1046102779/prometheus