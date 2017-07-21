## create configmap for config.toml
```
kubectl create configmap influxdb-conf --from-file=config.toml -n monitoring
```