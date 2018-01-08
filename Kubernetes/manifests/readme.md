
```
        --requestheader-client-ca-file=/srv/kubernetes/ca.pem
        - --requestheader-allowed-names=system:kube-controller-manager,system:kube-proxy,system:kube-scheduler,system:node:cnpvgl56588417,system:node:cnpvgl56588418
        - --requestheader-extra-headers-prefix=X-Remote-Extra-
        - --requestheader-group-headers=X-Remote-Group
        - --requestheader-username-headers=X-Remote-User
```
- `--requestheader-allowed-names=`: will allow these users to access `/apis/metrics.k8s.io/v1beta1` on apiserver. 
- all these options are used to set the permission to access `/apis/metrics.k8s.io/v1beta1`, which these metrics are register into  apiserver by metrics-server.
