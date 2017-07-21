1. create secrete for calico as etcd has tls
```
kubectl create secret  generic calico-etcd-secrets --from-file=etcd-key=etcdclient-key.pem --from-file=etcd-cert=etcdclient.pem --from-file=etcd-ca=ca.pem -n kube-system
```