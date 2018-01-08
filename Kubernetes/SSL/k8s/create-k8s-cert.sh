#!/bin/bash

MASTER_IP="192.168.59.129"
MASTER_DNS="k8s-master"
NODES="192.168.59.130"
SVC_CLUSTER=192.168.10.0/24
SVC_KUBERNETES=192.168.10.1
POD_CLUSTER=192.168.20.0/24


echo "Create apiserver certificates"

echo "#####"
echo "creating apiserver-key"
openssl genrsa -out apiserver-key.pem 4096

echo "creating openssl-k8s.conf"

cat <<EOF >openssl-k8s.conf

[req]
req_extensions = v3_req
distinguished_name = req_distinguished_name
[req_distinguished_name]
[ v3_req ]
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
subjectAltName = @alt_names
[ v3_ca ]
subjectAltName = @alternate_names
[alt_names]
DNS.1 = kubernetes
DNS.2 = kubernetes.default
DNS.3 = kubernetes.default.svc
DNS.4 = kubernetes.default.svc.cluster.local
IP.1 = $SVC_KUBERNETES
IP.2=127.0.0.1
EOF


master_dnsconter=0
for master_dns in $MASTER_DNS
 do 
	master_dnsconter=`expr $master_dnsconter + 5`
    echo DNS.$master_dnsconter=$master_dns >>openssl-k8s.conf
done


master_ipconter=0
for master_ip in $MASTER_IP
 do 
	master_ipconter=`expr $master_ipconter + 3`
	echo $master_ipconter
    echo IP.$master_ipconter=$master_ip >>openssl-k8s.conf
done


echo "create sing request"

openssl req -new -key apiserver-key.pem -out apiserver.csr -subj "/CN=apiserver" -config openssl-k8s.conf 


echo "signing apiserver.pem"

openssl x509 -req -in apiserver.csr -CA ca.pem -CAkey ca-key.pem -CAcreateserial -out apiserver.pem -days 3650   -extensions v3_req  -extfile   openssl-k8s.conf



## Create cluster admin certificates


echo "create cluster-admin-key"
openssl genrsa -out cluster-admin-key.pem 4096

echo "create sign request"


openssl req -new -key cluster-admin-key.pem -out cluster-admin.csr -subj "/O=system:masters" 

echo "signing cluster-admin.pem"


openssl x509 -req -in cluster-admin.csr -CA ca.pem -CAkey ca-key.pem -CAcreateserial -out cluster-admin.pem -days 3650 


## create system:kube-scheduler  certificates 
echo "create system:kube-scheduler key"


openssl genrsa -out kube-scheduler-key.pem 4096 

echo "create kube-scheduler  sign request"

openssl req -new -key kube-scheduler-key.pem -out kube-scheduler.csr -subj "/CN=system:kube-scheduler" 

echo "sign kube-scheduler.pem"

openssl x509 -req -in kube-scheduler.csr -CA ca.pem -CAkey ca-key.pem -CAcreateserial -out kube-scheduler.pem -days 3650 




## create system:kube-controller-manager  certificates 
echo "create system:kube-controller-manager key "


openssl genrsa -out kube-controller-manager-key.pem 4096 

echo "create kube-controller-manager sign request" 

openssl req -new -key kube-controller-manager-key.pem -out kube-controller-manager.csr -subj "/CN=system:kube-controller-manager" 

echo " sign  kube-controller-manager.pem"

openssl x509 -req -in kube-controller-manager.csr -CA ca.pem -CAkey ca-key.pem -CAcreateserial -out kube-controller-manager.pem -days 3650 


## create system:kube-proxy  certificates 
echo " create system:kube-proxy key "


openssl genrsa -out kube-proxy-key.pem 4096 

echo " create  kube-proxy sing request" 

openssl req -new -key kube-proxy-key.pem -out kube-proxy.csr -subj "/CN=system:kube-proxy" 

echo  "sign kube-proxy.pem"

openssl x509 -req -in kube-proxy.csr -CA ca.pem -CAkey ca-key.pem -CAcreateserial -out kube-proxy.pem -days 3650 


## create kubelet  certificates 

echo " create kubelet key "


openssl genrsa -out kubelet-key.pem 4096 




echo " create kubelet sign request"

for master in $MASTER_IP
do
openssl req -new -key kubelet-key.pem -out kubelet-$master.csr -subj "/O=system:nodes/CN=system:node:$master" 
done


if [ "x$NODES" != "x" ];
then
	for node in $NODES
		do 
			openssl req -new -key kubelet-key.pem -out kubelet-$node.csr -subj "/O=system:nodes/CN=system:node:$node" 
		done
	
fi




echo "sign kubelet csr"

for master in $MASTER_IP
do
openssl x509 -req -in kubelet-$master.csr -CA ca.pem -CAkey ca-key.pem -CAcreateserial -out kubelet-$master.pem -days 3650
done


if [ "x$NODES" != "x" ];
then
	for node in $NODES
		do 
			openssl x509 -req -in kubelet-$node.csr -CA ca.pem -CAkey ca-key.pem -CAcreateserial -out kubelet-$node.pem -days 3650
		done
	
fi
