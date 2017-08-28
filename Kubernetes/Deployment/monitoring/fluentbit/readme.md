## create configmap to accomodate the conf
```
kubectl create configmap fluentbit-conf --from-file=fluent-bit.conf  --from-file=fluentbit-parser.conf  -n monitoring
```

##other Tips 

1. we use fluentbit to read logs from journald, and after parsering/filtering, finally save them into influxdb

2. in the fluentbit daemonset, we share /var/log/journal with pod, in addtion to two  journald sockets. but currently only /var/log/journal is working for fluentbit

3. conf for fluentbit
  
   3.1 enable trace/debug in the [service] section, which helps me a lot to investigate the problems.

   3.2 for the input plugin, choose systemd as the plugin, and  add two Systemd_Filters, addtional Path is mandatory. 

   3.3 we don't need parser, because journal logs are already structured.  
   
   3.5 in the filter, we add `Match       *` and `use_journal  On` plus the default kubernetes setting. 

4. set corect RBAC for service account fluentbit

5. create database in influxdb 

   ```
   create database k8slog
   ```
6. create RETENTION POLICY
   
   ```
   CREATE RETENTION POLICY "docker" ON "k8slog" DURATION 30d REPLICATION 1 DEFAULT
   ```
