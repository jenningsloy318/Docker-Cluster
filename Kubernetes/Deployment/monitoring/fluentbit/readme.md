## create configmap to accomodate the conf
```
kubectl create configmap fluentbit-conf --from-file=fluent-bit.conf  --from-file=fluentbit-parser.conf  -n monitoring
```
