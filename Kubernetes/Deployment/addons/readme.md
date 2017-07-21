## create configmap for kube-proxy
```
 kubectl create configmap kube-proxy.kubeconfig --from-file=kube-proxy.kubeconfig=/srv/kubernetes/kube-proxy.kubeconfig
 ```