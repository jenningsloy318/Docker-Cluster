1. create secrete for calico as etcd has tls
```
kubectl create secret  generic calico-etcd-secrets --from-file=etcd-key=etcdclient-key.pem --from-file=etcd-cert=etcdclient.pem --from-file=etcd-ca=ca.pem -n kube-system
```

2. More details explanation about calico [Calico网络的原理、组网方式与使用](http://www.lijiaocn.com/%E9%A1%B9%E7%9B%AE/2017/04/11/calico-usage.html)