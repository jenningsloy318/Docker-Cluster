Description:
--
My demo environment has two hosts, one is used for master and the other one is node. and I will use traditional systemd to run these services.

hostname|IP address|
--------|-----------
kube-master| 192.168.49.141
kube-node1:|192.168.49.135

Authentication in Kubernetes:

1. there are two kinds of users in kubenetes, normal user and service account. 
    * normal users are managed by priviate key, key store(keystone/google account) or a file which contains the user list. 
    * service accounts are users managed by the Kubernetes API. They are bound to specific namespaces, and created automatically by the API server or manually through API calls.
    * API requests are tied to either a normal user or a service account, or are treated as anonymous requests. 
    * every process inside or outside the cluster must authenticate when making requests to the API server, or be treated as an anonymous user.

2. authentication strategies.
    * client certificates
    * bearer tokens
    * authenticating proxy
    * HTTP basic auth

3. users authenticate torwards kubernetes API have following attributes
    * Username: a string which identifies the end user. Common values might be kube-admin or jane@example.com.
    * UID: a string which identifies the end user and attempts to be more consistent and unique than username.
    * Groups: a set of strings which associate users with as set of commonly grouped users.
    * Extra fields: a map of strings to list of strings which holds additional information authorizers may find useful.

4. authentication method
    * Client certificate authentication, enabled by passing --client-ca-file= to apiserver, which need to generate client certificate. 
    * Static Token authentication, enabled by passing --token-auth-file= to apiserver, we should create a token file which contains columns "token,user,uid [,group1,group2,group3]" (groups are optional).
    * Basic authentication, enabled by passing --basic-auth-file= to apiserver, a stack user,password,uid file will be created.
    * Service Account authentication, Service accounts are usually created automatically by the API server and associated with pods running in the cluster through the ServiceAccount Admission Controller.

*Configure on master node*


**1. Get kubernetes binary and etcd binary.**

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

**2. Start etcd on master.**

copy [etcd.service](./init/etcd.service) to /etc/systemd/system/multi-user.target.wants/;

copy [etcd.conf](./conf/etcd.conf) to /etc/etcd/

```shell
#systemctl daemon-reload
#systemctl start etcd
# ss -lptn | column -n |grep etcd
LISTEN     0      128         :::2379                    :::*                   users:(("etcd",pid=2108,fd=6))
LISTEN     0      128         :::2380                    :::*                   users:(("etcd",pid=2108,fd=5))

```

**3 prepare the authentications for communication between master and node.**

 *create certification for  authentication, using [EasyRSA](https://github.com/OpenVPN/easy-rsa).* 


* create CA cert for overall certificaion.

```shell
# wget https://github.com/OpenVPN/easy-rsa/releases/download/3.0.1/EasyRSA-3.0.1.tgz
#tar xfEasyRSA-3.0.1.tgz
#cd EasyRSA
#./easyrsa init-pki
# MASTER=192.168.49.141
#./easyrsa --batch "--req-cn=$MASTER@`date +%s`" build-ca nopass
```

* create server cert/key for HTTPS using on master.

```shell
#./easyrsa --subject-alt-name="IP:$MASTER" build-server-full server nopass
# cp pki/ca.crt  pki/issued/server.crt pki/private/server.key  /var/run/kubernetes
```
