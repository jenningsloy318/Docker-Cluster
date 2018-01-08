etcd env and commands


etcdv3

env:

Global flags (e.g., dial-timeout, --cacert, --cert, --key) can be set with environment variables:
```
export ETCDCTL_API=3
export ETCDCTL_CACERT=/srv/kubernetes/ca.pem
export ETCDCTL_CERT=/srv/kubernetes/etcd.pem
export ETCDCTL_KEY=/srv/kubernetes/etcd-key.pem
export ETCDCTL_ENDPOINTS=https://xx.xx.xx.xx:2379
```
commands:
1. list all entries
```
etcdctl get / --prefix --keys-only  

/registry/apiregistration.k8s.io/apiservices/v1.

/registry/apiregistration.k8s.io/apiservices/v1.authentication.k8s.io

/registry/apiregistration.k8s.io/apiservices/v1.authorization.k8s.io

/registry/apiregistration.k8s.io/apiservices/v1.autoscaling

/registry/apiregistration.k8s.io/apiservices/v1.batch

/registry/apiregistration.k8s.io/apiservices/v1.networking.k8s.io

/registry/apiregistration.k8s.io/apiservices/v1.storage.k8s.io

/registry/apiregistration.k8s.io/apiservices/v1alpha1.rbac.authorization.k8s.io

/registry/apiregistration.k8s.io/apiservices/v1alpha1.settings.k8s.io

/registry/apiregistration.k8s.io/apiservices/v1beta1.apiextensions.k8s.io

...
```

2. get value for perticular key
```
etcdctl get /registry/storageclasses/cscdevops-nfs -w fields
"ClusterID" : 409811084952378386
"MemberID" : 4133983650327343170
"Revision" : 12107052
"RaftTerm" : 35
"Key" : "/registry/storageclasses/cscdevops-nfs"
"CreateRevision" : 8314828
"ModRevision" : 8314828
"Version" : 1
"Value" : "k8s\x00\n!\n\x11storage.k8s.io/v1\x12\fStorageClass\x12\xc7\x04\n\xea\x03\n\rcscdevops-nfs\x12\x00\x1a\x00\"\x00*$bf5f3a6e-92a7-11e7-83ac-30e1715dbd382\x008\x00B\f\b\xba\xaf\xbd\xcd\x05\x10ى\xe4\x9c\x02b\xe3\x02\n0kubectl.kubernetes.io/last-applied-configuration\x12\xae\x02{\"apiVersion\":\"storage.k8s.io/v1beta1\",\"kind\":\"StorageClass\",\"metadata\":{\"annotations\":{\"storageclass.kubernetes.io/is-default-class\":\"true\"},\"name\":\"cscdevops-nfs\",\"namespace\":\"\"},\"parameters\":{\"mountOptions\":\"hard,intr,bg,noatime,timeo=5,retrans=5,actimeo=10,retry=5\"},\"provisioner\":\"cscdevops-nfs\"}\nb3\n+storageclass.kubernetes.io/is-default-class\x12\x04truez\x00\x12\rcscdevops-nfs\x1aI\n\fmountOptions\x129hard,intr,bg,noatime,timeo=5,retrans=5,actimeo=10,retry=5\x1a\x00\"\x00"
"Lease" : 0
"More" : false
"Count" : 1
```



etcdv2

env:
```
export ETCDCTL_API=2
export ETCDCTL_CA_FILE=/srv/kubernetes/ca.pem
export ETCDCTL_CERT_FILE=/srv/kubernetes/etcd.pem
export ETCDCTL_KEY_FILE=/srv/kubernetes/etcd-key.pem
export ETCDCTL_ENDPOINTS=https://xx.xx.xx.xx:2379
```

Commands:

1. list all entries
```
etcdctl ls /
/calico
/registry
```