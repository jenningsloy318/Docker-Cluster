## kubelet.kubeconfg
- node 192.168.59.201
```
kubectl config set-cluster kubernetes --certificate-authority=/var/lib/kubernetes/certs/RootCA.pem --embed-certs=true --server=https://127.0.0.1:8443 --kubeconfig=/var/lib/kubernetes/kubeconfig/kubelet.kubeconfig
kubectl config set-credentials kubelet --client-certificate=/var/lib/kubernetes/certs/kubelet-192.168.59.201.pem --client-key=/var/lib/kubernetes/certs/kubelet-192.168.59.201-key.pem --embed-certs=true      --kubeconfig=/var/lib/kubernetes/kubeconfig/kubelet.kubeconfig
kubectl config set-context kubelet@kubernetes --cluster=kubernetes --user=kubelet  --kubeconfig=/var/lib/kubernetes/kubeconfig/kubelet.kubeconfig
kubectl config  use-context kubelet@kubernetes  --kubeconfig=/var/lib/kubernetes/kubeconfig/kubelet.kubeconfig

```
- node 192.168.59.202
```
kubectl config set-cluster kubernetes --certificate-authority=/var/lib/kubernetes/certs/RootCA.pem --embed-certs=true --server=https://127.0.0.1:8443 --kubeconfig=/var/lib/kubernetes/kubeconfig/kubelet.kubeconfig
kubectl config set-credentials kubelet --client-certificate=/var/lib/kubernetes/certs/kubelet-192.168.59.202.pem --client-key=/var/lib/kubernetes/certs/kubelet-192.168.59.202-key.pem --embed-certs=true      --kubeconfig=/var/lib/kubernetes/kubeconfig/kubelet.kubeconfig
kubectl config set-context kubelet@kubernetes --cluster=kubernetes --user=kubelet  --kubeconfig=/var/lib/kubernetes/kubeconfig/kubelet.kubeconfig
kubectl config  use-context kubelet@kubernetes  --kubeconfig=/var/lib/kubernetes/kubeconfig/kubelet.kubeconfig
```


- node 192.168.59.203
```
kubectl config set-cluster kubernetes --certificate-authority=/var/lib/kubernetes/certs/RootCA.pem --embed-certs=true --server=https://127.0.0.1:8443 --kubeconfig=/var/lib/kubernetes/kubeconfig/kubelet.kubeconfig
kubectl config set-credentials kubelet --client-certificate=/var/lib/kubernetes/certs/kubelet-192.168.59.203.pem --client-key=/var/lib/kubernetes/certs/kubelet-192.168.59.203-key.pem --embed-certs=true      --kubeconfig=/var/lib/kubernetes/kubeconfig/kubelet.kubeconfig
kubectl config set-context kubelet@kubernetes --cluster=kubernetes --user=kubelet  --kubeconfig=/var/lib/kubernetes/kubeconfig/kubelet.kubeconfig
kubectl config  use-context kubelet@kubernetes  --kubeconfig=/var/lib/kubernetes/kubeconfig/kubelet.kubeconfig
```


- node 192.168.59.204
```
kubectl config set-cluster kubernetes --certificate-authority=/var/lib/kubernetes/certs/RootCA.pem --embed-certs=true --server=https://127.0.0.1:8443 --kubeconfig=/var/lib/kubernetes/kubeconfig/kubelet.kubeconfig
kubectl config set-credentials kubelet --client-certificate=/var/lib/kubernetes/certs/kubelet-192.168.59.204.pem --client-key=/var/lib/kubernetes/certs/kubelet-192.168.59.204-key.pem --embed-certs=true      --kubeconfig=/var/lib/kubernetes/kubeconfig/kubelet.kubeconfig
kubectl config set-context kubelet@kubernetes --cluster=kubernetes --user=kubelet  --kubeconfig=/var/lib/kubernetes/kubeconfig/kubelet.kubeconfig
kubectl config  use-context kubelet@kubernetes  --kubeconfig=/var/lib/kubernetes/kubeconfig/kubelet.kubeconfig
```

## kube-controller-manager.kubeconfig
```
kubectl config set-cluster kubernetes --certificate-authority=/var/lib/kubernetes/certs/RootCA.pem --embed-certs=true --server=https://127.0.0.1:8443  --kubeconfig=/var/lib/kubernetes/kubeconfig/kube-controller-manager.kubeconfig
kubectl config set-credentials kube-controller-manager --client-certificate=/var/lib/kubernetes/certs/kube-controller-manager.pem --client-key=/var/lib/kubernetes/certs/kube-controller-manager-key.pem --embed-certs=true       --kubeconfig=/var/lib/kubernetes/kubeconfig/kube-controller-manager.kubeconfig
kubectl config set-context kube-controller-manager@kubernetes --cluster=kubernetes --user=kube-controller-manager  --kubeconfig=/var/lib/kubernetes/kubeconfig/kube-controller-manager.kubeconfig
kubectl config  use-context kube-controller-manager@kubernetes  --kubeconfig=/var/lib/kubernetes/kubeconfig/kube-controller-manager.kubeconfig
```
## kube-scheduler.kubeconfig
```
kubectl config set-cluster kubernetes --certificate-authority=/var/lib/kubernetes/certs/RootCA.pem --embed-certs=true --server=https://127.0.0.1:8443  --kubeconfig=/var/lib/kubernetes/kubeconfig/kube-scheduler.kubeconfig
kubectl config set-credentials kube-scheduler --client-certificate=/var/lib/kubernetes/certs/kube-scheduler.pem --client-key=/var/lib/kubernetes/certs/kube-scheduler-key.pem --embed-certs=true       --kubeconfig=/var/lib/kubernetes/kubeconfig/kube-scheduler.kubeconfig
kubectl config set-context kube-scheduler@kubernetes --cluster=kubernetes --user=kube-scheduler  --kubeconfig=/var/lib/kubernetes/kubeconfig/kube-scheduler.kubeconfig
kubectl config  use-context kube-scheduler@kubernetes  --kubeconfig=/var/lib/kubernetes/kubeconfig/kube-scheduler.kubeconfig
```

## kube-proxy.kubeconfig
```
kubectl config set-cluster kubernetes --certificate-authority=/var/lib/kubernetes/certs/RootCA.pem --embed-certs=true --server=https://127.0.0.1:8443  --kubeconfig=/var/lib/kubernetes/kubeconfig/kube-proxy.kubeconfig
kubectl config set-credentials kube-proxy --client-certificate=/var/lib/kubernetes/certs/kube-proxy.pem --client-key=/var/lib/kubernetes/certs/kube-proxy-key.pem --embed-certs=true       --kubeconfig=/var/lib/kubernetes/kubeconfig/kube-proxy.kubeconfig
kubectl config set-context kube-proxy@kubernetes --cluster=kubernetes --user=kube-proxy  --kubeconfig=/var/lib/kubernetes/kubeconfig/kube-proxy.kubeconfig
kubectl config  use-context kube-proxy@kubernetes  --kubeconfig=/var/lib/kubernetes/kubeconfig/kube-proxy.kubeconfig
```


## cluster-admin.kubeconfig
```
kubectl config set-cluster kubernetes --certificate-authority=/var/lib/kubernetes/certs/RootCA.pem --embed-certs=true --server=https://127.0.0.1:8443   --kubeconfig=/var/lib/kubernetes/certs/cluster-admin.kubeconfig 
kubectl config set-credentials cluster-admin --client-certificate=/var/lib/kubernetes/certs/cluster-admin.pem --client-key=/var/lib/kubernetes/certs/cluster-admin-key.pem --embed-certs=true       --kubeconfig=/var/lib/kubernetes/certs/cluster-admin.kubeconfig
kubectl config set-context cluster-admin@kubernetes --cluster=kubernetes --user=cluster-admin  --kubeconfig=/var/lib/kubernetes/certs/cluster-admin.kubeconfig
kubectl config  use-context cluster-admin@kubernetes  --kubeconfig=/var/lib/kubernetes/certs/cluster-admin.kubeconfig
```


## create basic and token auth 
```
TOKEN=$(dd if=/dev/urandom bs=128 count=1 2>/dev/null | base64 | tr -d "=+/" | dd bs=32 count=1 2>/dev/null)

echo "$TOKEN,clusteradm,clusteradm,\"system:masters\"" > /var/lib/kubernetes/certs/c

echo "Q9wgrHJQscILd4,clusteradm,clusteradm,\"system:masters\"" > /var/lib/kubernetes/certs/basic.csv
```