Description:
--
My demo environment has two hosts, one is used for master and the other one is node. and I will use traditional systemd to run these services.

hostname|IP address|
--------|-----------
kube-master| 192.168.49.141
kube-node1:|192.168.49.135


*Configure on master node*
> **1. Get kubernetes binary and etcd binary**

  a. get kubernetes binary 

```shell

# wget https://github.com/kubernetes/kubernetes/releases/download/v1.5.0/kubernetes.tar.gz
# untar kubernetes.tar.gz 
# cd kubernetes
# cluster/get-kube-binaries.sh
Kubernetes release: v1.5.0
Server: linux/amd64
Client: linux/amd64

Will download kubernetes-server-linux-amd64.tar.gz from https://storage.googleapis.com/kubernetes-release/release/v1.5.0
Will download and extract kubernetes-client-linux-amd64.tar.gz from https://storage.googleapis.com/kubernetes-release/release/v1.5.0

Will download and extract kubernetes-client-linux-amd64.tar.gz from https://storage.googleapis.com/kubernetes-release/release/v1.5.0
Is this ok? [Y]/n y


kubernetes/server/kubernetes-server-linux-amd64.tar.gz 
kubernetes/client/kubernetes-client-linux-amd64.tar.gz 

#tar xf kubernetes/server/kubernetes-server-linux-amd64.tar.gz 
# tar xf kubernetes/client/kubernetes-client-linux-amd64.tar.gz 

```

then copy all binaries to /usr/bin on master and node 

  b. get etcd binary

```shell
# wget https://github.com/coreos/etcd/releases/download/v3.0.15/etcd-v3.0.15-linux-amd64.tar.gz
#tar xf etcd-v3.0.15-linux-amd64.tar.gz
then copy all binary to /usr/bin
```
> **2. Start etcd on master **

copy [etcd.service](./init/etcd.service) to /etc/systemd/system/multi-user.target.wants/;

copy [etcd.conf](./conf/etcd.conf) to /etc/etcd/

```shell
#systemctl daemon-reload
#systemctl start etcd
# ss -lptn | column -n |grep etcd
LISTEN     0      128         :::2379                    :::*                   users:(("etcd",pid=2108,fd=6))
LISTEN     0      128         :::2380                    :::*                   users:(("etcd",pid=2108,fd=5))

```
