## create configmap to accomodate the conf
```
kubectl create configmap fluentbit-conf --from-file=fluentbit.conf=fluentbit.conf --from-file=fluentbit-parer.conf=fluentbit-parer.conf  -n monitoring
```
