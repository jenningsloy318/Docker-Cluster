
1. create nfs-provision service account and binding roles 
```
kubectl apply -f nfs-provisioner-rbac.yaml
```
2. create the nfs-provisioner-daemoset

```
kubectl apply -f nfs-provisioner-daemonset.yaml
```

