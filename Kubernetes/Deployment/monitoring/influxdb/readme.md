## create configmap for config.toml
```
kubectl create configmap influxdb-conf --from-file=config.toml -n monitoring
```

## create database for promethus/k8slog
since we enabled ingress tcp exposure, we can connect influxdb via ingress controller directly.
```
#  influx  -host 10.58.137.243 -port 8086
Visit https://enterprise.influxdata.com to register for updates, InfluxDB server management, and monitoring.
Connected to http://10.58.137.243:8086 version unknown
InfluxDB shell 0.10.0
> create database prometheus
>create database k8slog
> show databases
name: databases
---------------
name
_internal
k8s
k8slog
prometheus
```
