1. create btrfs on /dev/sdb
```
#mkfs.btrfs /dev/sdb

btrfs-progs v4.4
See http://btrfs.wiki.kernel.org for more information.

Label:              (null)
UUID:               729840e5-d577-4003-aee7-501218b52602
Node size:          16384
Sector size:        4096
Filesystem size:    931.48GiB
Block group profiles:
  Data:             single            8.00MiB
  Metadata:         DUP               1.01GiB
  System:           DUP              12.00MiB
SSD detected:       no
Incompat features:  extref, skinny-metadata
Number of devices:  1
Devices:
   ID        SIZE  PATH
    1   931.48GiB  /dev/sdb
```

2. mount it to /data
```  
mount /dev/sdb /data/
```
3. add /dev/sdc to /data
```
btrfs device  add /dev/sdc /data
```

4. show the usage 
```
# btrfs fi usage /data
Overall:
    Device size:                   1.82TiB
    Device allocated:              2.02GiB
    Device unallocated:            1.82TiB
    Device missing:                  0.00B
    Used:                        512.00KiB
    Free (estimated):              1.82TiB      (min: 930.48GiB)
    Data ratio:                       1.00
    Metadata ratio:                   2.00
    Global reserve:               16.00MiB      (used: 0.00B)

Data,single: Size:8.00MiB, Used:256.00KiB
   /dev/sdb        8.00MiB

Metadata,DUP: Size:1.00GiB, Used:112.00KiB
   /dev/sdb        2.00GiB

System,DUP: Size:8.00MiB, Used:16.00KiB
   /dev/sdb       16.00MiB

Unallocated:
   /dev/sdb      929.46GiB
   /dev/sdc      931.48GiB
```

5. enable quota under /data
```
 btrfs  quota enable /data
```

6. create subvolume under /data

```
#cd /data
#btrfs subvolume create nfs-provisioner
  Create subvolume './nfs-provisioner'
```

7. limit the size of nfs-provisioner
```
btrfs qgroup limit 100G /data/nfs-provisioner
```

7. create nfs-provision service account and binding roles 
```
kubectl apply -f nfs-provisioner-rbac.yaml
```

8. get secret of the service account 
```
secret=$(kubectl get sa nfs-provisioner -o json | jq -r .secrets[].name)
```


19. Get service account token from secret
```
user_token=$(kubectl get secret $secret -o json | jq -r '.data["token"]' | base64 -d)
```

10. create nfs-prvisoner.kubeconfig

```
kubectl config set-cluster kubernetes --certificate-authority=/srv/kubernetes/ca.pem --embed-certs=true --server=https://10.58.137.243:6443 --kubeconfig=/srv/kubernetes/nfs-prvisoner.kubeconfig
kubectl config set-credentials nfs-provisioner  --token=$user_token  --kubeconfig=/srv/kubernetes/nfs-prvisoner.kubeconfig
kubectl config set-context nfs-provisioner@kubernetes --cluster=kubernetes --user=nfs-provisioner  --kubeconfig=/srv/kubernetes/nfs-prvisoner.kubeconfig
kubectl config  use-context nfs-provisioner@kubernetes  --kubeconfig=/srv/kubernetes/nfs-prvisoner.kubeconfig
```

11. run nfs-provisioner outside of cluster

```
