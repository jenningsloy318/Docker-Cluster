#!/bin/bash

MASTER="192.168.59.129"
NODES="192.168.59.130"
SVC_CLUSTER=192.168.10.0/24
SVC_KUBERNETES=192.168.10.1
POD_CLUSTER=192.168.20.0/24

for master in  $MASTER
		do 
echo "create kubeconfig for kubelet master "
kubectl config set-cluster kubernetes --certificate-authority=/var/lib/kubernetes/ca.pem --embed-certs=true --server=https://$MASTER:6443 --kubeconfig=/var/lib/kubernetes/kubelet.kubeconfig
kubectl config set-credentials kubelet --client-certificate=/var/lib/kubernetes/kubelet-$master.pem --client-key=/var/lib/kubernetes/kubelet-key.pem --embed-certs=true      --kubeconfig=/var/lib/kubernetes/kubelet.kubeconfig
kubectl config set-context kubelet@kubernetes --cluster=kubernetes --user=kubelet  --kubeconfig=/var/lib/kubernetes/kubelet.kubeconfig 
kubectl config  use-context kubelet@kubernetes  --kubeconfig=/var/lib/kubernetes/kubelet.kubeconfig

done





if [ "x$NODES" != "x" ];

echo "create kubeconfig for kubelet nodes "

then
	for node in $NODES $MASTER
		do 
		
		kubectl config set-cluster kubernetes --certificate-authority=/var/lib/kubernetes/ca.pem --embed-certs=true --server=https://$MASTER:6443 --kubeconfig=/var/lib/kubernetes/kubelet.kubeconfig
		kubectl config set-credentials kubelet --client-certificate=/var/lib/kubernetes/kubelet-$node.pem --client-key=/var/lib/kubernetes/kubelet-key.pem --embed-certs=true      --kubeconfig=/var/lib/kubernetes/kubelet.kubeconfig
		kubectl config set-context kubelet@kubernetes --cluster=kubernetes --user=kubelet  --kubeconfig=/var/lib/kubernetes/kubelet.kubeconfig 
		kubectl config  use-context kubelet@kubernetes  --kubeconfig=/var/lib/kubernetes/kubelet.kubeconfig
		done
	
fi


## kube-controller-manager.kubeconfig

kubectl config set-cluster kubernetes --certificate-authority=/var/lib/kubernetes/ca.pem --embed-certs=true --server=https://$MASTER:6443 --kubeconfig=/var/lib/kubernetes/kube-controller-manager.kubeconfig
kubectl config set-credentials kube-controller-manager --client-certificate=/var/lib/kubernetes/kube-controller-manager.pem --client-key=/var/lib/kubernetes/kube-controller-manager-key.pem --embed-certs=true       --kubeconfig=/var/lib/kubernetes/kube-controller-manager.kubeconfig
kubectl config set-context kube-controller-manager@kubernetes --cluster=kubernetes --user=kube-controller-manager  --kubeconfig=/var/lib/kubernetes/kube-controller-manager.kubeconfig
kubectl config  use-context kube-controller-manager@kubernetes  --kubeconfig=/var/lib/kubernetes/kube-controller-manager.kubeconfig

## kube-scheduler.kubeconfig

kubectl config set-cluster kubernetes --certificate-authority=/var/lib/kubernetes/ca.pem --embed-certs=true --server=https://$MASTER:6443 --kubeconfig=/var/lib/kubernetes/kube-scheduler.kubeconfig
kubectl config set-credentials kube-scheduler --client-certificate=/var/lib/kubernetes/kube-scheduler.pem --client-key=/var/lib/kubernetes/kube-scheduler-key.pem --embed-certs=true       --kubeconfig=/var/lib/kubernetes/kube-scheduler.kubeconfig
kubectl config set-context kube-scheduler@kubernetes --cluster=kubernetes --user=kube-scheduler  --kubeconfig=/var/lib/kubernetes/kube-scheduler.kubeconfig
kubectl config  use-context kube-scheduler@kubernetes  --kubeconfig=/var/lib/kubernetes/kube-scheduler.kubeconfig


## kube-proxy.kubeconfig

kubectl config set-cluster kubernetes --certificate-authority=/var/lib/kubernetes/ca.pem --embed-certs=true --server=https://$MASTER:6443 --kubeconfig=/var/lib/kubernetes/kube-proxy.kubeconfig
kubectl config set-credentials kube-proxy --client-certificate=/var/lib/kubernetes/kube-proxy.pem --client-key=/var/lib/kubernetes/kube-proxy-key.pem --embed-certs=true       --kubeconfig=/var/lib/kubernetes/kube-proxy.kubeconfig
kubectl config set-context kube-proxy@kubernetes --cluster=kubernetes --user=kube-proxy  --kubeconfig=/var/lib/kubernetes/kube-proxy.kubeconfig
kubectl config  use-context kube-proxy@kubernetes  --kubeconfig=/var/lib/kubernetes/kube-proxy.kubeconfig



## cluster-admin.kubeconfig

kubectl config set-cluster kubernetes --certificate-authority=/var/lib/kubernetes/ca.pem --embed-certs=true --server=https://$MASTER:6443  --kubeconfig=/var/lib/kubernetes/cluster-admin.kubeconfig 
kubectl config set-credentials cluster-admin --client-certificate=/var/lib/kubernetes/cluster-admin.pem --client-key=/var/lib/kubernetes/cluster-admin-key.pem --embed-certs=true       --kubeconfig=/var/lib/kubernetes/cluster-admin.kubeconfig
kubectl config set-context cluster-admin@kubernetes --cluster=kubernetes --user=cluster-admin  --kubeconfig=/var/lib/kubernetes/cluster-admin.kubeconfig
kubectl config  use-context cluster-admin@kubernetes  --kubeconfig=/var/lib/kubernetes/cluster-admin.kubeconfig



## create basic and token auth 

TOKEN=$(dd if=/dev/urandom bs=128 count=1 2>/dev/null | base64 | tr -d "=+/" | dd bs=32 count=1 2>/dev/null)

echo "$TOKEN,clusteradm,clusteradm,\"system:masters\"" > /var/lib/kubernetes/token.csv

echo "Q9wgrHJQscILd4,clusteradm,clusteradm,\"system:masters\"" > /var/lib/kubernetes/basic.csv
