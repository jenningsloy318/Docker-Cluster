## kubelet.kubeconfg
- node cnpvgl56588417
```
kubectl config set-cluster kubernetes --certificate-authority=/srv/kubernetes/ca.pem --embed-certs=true --server=https://10.58.137.243:6443 --kubeconfig=/srv/kubernetes/kubelet.kubeconfig
kubectl config set-credentials kubelet --client-certificate=/srv/kubernetes/kubelet-cnpvgl56588417.pem --client-key=/srv/kubernetes/kubelet-key.pem --embed-certs=true      --kubeconfig=/srv/kubernetes/kubelet.kubeconfig
kubectl config set-context kubelet@kubernetes --cluster=kubernetes --user=kubelet  --kubeconfig=/srv/kubernetes/kubelet.kubeconfig 
kubectl config  use-context kubelet@kubernetes  --kubeconfig=/srv/kubernetes/kubelet.kubeconfig
```
- node cnpvgl56588418
```
kubectl config set-cluster kubernetes --certificate-authority=/srv/kubernetes/ca.pem --embed-certs=true --server=https://10.58.137.243:6443 --kubeconfig=/srv/kubernetes/kubelet.kubeconfig
kubectl config set-credentials kubelet --client-certificate=/srv/kubernetes/kubelet-cnpvgl56588418.pem --client-key=/srv/kubernetes/kubelet-key.pem --embed-certs=true      --kubeconfig=/srv/kubernetes/kubelet.kubeconfig
kubectl config set-context kubelet@kubernetes --cluster=kubernetes --user=kubelet  --kubeconfig=/srv/kubernetes/kubelet.kubeconfig 
kubectl config  use-context kubelet@kubernetes  --kubeconfig=/srv/kubernetes/kubelet.kubeconfig
```

## kube-controller-manager.kubeconfig
```
kubectl config set-cluster kubernetes --certificate-authority=/srv/kubernetes/ca.pem --embed-certs=true --server=https://10.58.137.243:6443 --kubeconfig=/srv/kubernetes/kube-controller-manager.kubeconfig
kubectl config set-credentials kube-controller-manager --client-certificate=/srv/kubernetes/kube-controller-manager.pem --client-key=/srv/kubernetes/kube-controller-manager-key.pem --embed-certs=true       --kubeconfig=/srv/kubernetes/kube-controller-manager.kubeconfig
kubectl config set-context kube-controller-manager@kubernetes --cluster=kubernetes --user=kube-controller-manager  --kubeconfig=/srv/kubernetes/kube-controller-manager.kubeconfig
kubectl config  use-context kube-controller-manager@kubernetes  --kubeconfig=/srv/kubernetes/kube-controller-manager.kubeconfig
```
## kube-scheduler.kubeconfig
```
kubectl config set-cluster kubernetes --certificate-authority=/srv/kubernetes/ca.pem --embed-certs=true --server=https://10.58.137.243:6443 --kubeconfig=/srv/kubernetes/kube-scheduler.kubeconfig
kubectl config set-credentials kube-scheduler --client-certificate=/srv/kubernetes/kube-scheduler.pem --client-key=/srv/kubernetes/kube-scheduler-key.pem --embed-certs=true       --kubeconfig=/srv/kubernetes/kube-scheduler.kubeconfig
kubectl config set-context kube-scheduler@kubernetes --cluster=kubernetes --user=kube-scheduler  --kubeconfig=/srv/kubernetes/kube-scheduler.kubeconfig
kubectl config  use-context kube-scheduler@kubernetes  --kubeconfig=/srv/kubernetes/kube-scheduler.kubeconfig
```

## kube-proxy.kubeconfig
```
kubectl config set-cluster kubernetes --certificate-authority=/srv/kubernetes/ca.pem --embed-certs=true --server=https://10.58.137.243:6443 --kubeconfig=/srv/kubernetes/kube-proxy.kubeconfig
kubectl config set-credentials kube-proxy --client-certificate=/srv/kubernetes/kube-proxy.pem --client-key=/srv/kubernetes/kube-proxy-key.pem --embed-certs=true       --kubeconfig=/srv/kubernetes/kube-proxy.kubeconfig
kubectl config set-context kube-proxy@kubernetes --cluster=kubernetes --user=kube-proxy  --kubeconfig=/srv/kubernetes/kube-proxy.kubeconfig
kubectl config  use-context kube-proxy@kubernetes  --kubeconfig=/srv/kubernetes/kube-proxy.kubeconfig
```


## cluster-admin.kubeconfig
```
kubectl config set-cluster kubernetes --certificate-authority=/srv/kubernetes/ca.pem --embed-certs=true --server=https://10.58.137.243:6443  --kubeconfig=/srv/kubernetes/cluster-admin.kubeconfig 
kubectl config set-credentials cluster-admin --client-certificate=/srv/kubernetes/cluster-admin.pem --client-key=/srv/kubernetes/cluster-admin-key.pem --embed-certs=true       --kubeconfig=/srv/kubernetes/cluster-admin.kubeconfig
kubectl config set-context cluster-admin@kubernetes --cluster=kubernetes --user=cluster-admin  --kubeconfig=/srv/kubernetes/cluster-admin.kubeconfig
kubectl config  use-context cluster-admin@kubernetes  --kubeconfig=/srv/kubernetes/cluster-admin.kubeconfig
```