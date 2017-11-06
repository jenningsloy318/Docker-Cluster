##Tips

1. create proper RBAC, here we use [cluster-view](../../RBAC/cluster-view.yaml), besides normal `get`,`watch`,`list`, dashboard still need `proxy`, to proxy to heapster to get the cluster compute resource usage, so add `proxy` into the verb list.
2. create TLS key and request
  
    2.1  create dashboard-key
    ```
    openssl genrsa   -out dashboard-key.pem 4096
    ```
    2.2  create dashboard.csr
    ```
    openssl req -new -key dashboard-key.pem -out dashboard.csr  -subj "/CN=k8s.gcsc.sap.corp" -config openssl-dashboard.conf
    ```
    2.3 save the cert to dashboard-cert.pem

    2.4 create secret for dashboard deployment

    ```
    kubectl create secret generic kubernetes-dashboard-certs --from-file=certs/ -n kube-system
    ```

    2.4 create secret for ingress
    ```
    kubectl create secret tls dashboard-ingress-secret --key certs/dashboard.key --cert certs/dashboard.crt -n kube-system
    ```
3. for deployment, refer to https://github.com/kubernetes/dashboard/wiki/Installation