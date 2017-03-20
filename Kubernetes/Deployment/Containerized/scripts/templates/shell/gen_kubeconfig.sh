#!/bin/bash
apiserver=$1
outdir=$2
kubeconfig=$3
if ! which kubectl;then
    echo "install kubectl"
     curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl -o /usr/bin/kubectl
fi

kubectl config set-cluster devosp-k8s --certificate-authority=/data/kubernetes/certs/ca.pem  --server=https://${apiserver}:6443 --kubeconfig=${outdir}/${kubeconfig}
kubectl config set-credentials admin  --client-certificate=/data/kubernetes/certs/apiserver.pem --client-key=/data/kubernetes/certs/apiserver-key.pem  --kubeconfig=${outdir}/${kubeconfig}
kubectl config set-context admin@devosp-k8s --cluster=devosp-k8s --user=admin  --kubeconfig=${outdir}/kubeconfig
kubectl config  use-context admin@devosp-k8s  --kubeconfig=${outdir}/${kubeconfig}
