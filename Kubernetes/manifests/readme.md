1. 
```
--requestheader-client-ca-file=/srv/kubernetes/ca.pem
--requestheader-allowed-names=system:kube-controller-manager,system:kube-proxy,system:kube-scheduler,system:node:cnpvgl56588417,system:node:cnpvgl56588418
--requestheader-extra-headers-prefix=X-Remote-Extra-
--requestheader-group-headers=X-Remote-Group
--requestheader-username-headers=X-Remote-User
```

- `--requestheader-allowed-names=`: will allow these users to access `/apis/metrics.k8s.io/v1beta1` on apiserver. 
- all these options are used to set the permission to access `/apis/metrics.k8s.io/v1beta1`, which these metrics are register into  apiserver by metrics-server. details described [here](https://github.com/kubernetes-incubator/apiserver-builder/blob/master/docs/concepts/aggregation.md)


2. we can set the `--bind-address` to its one external address of the master node, since we will running a pod of apiserver-proxy which serves on `127.0.0.1:6443`


3. The API aggregator is integrated into the main Kubernetes API server,in order for the aggregator to work properly, it needs to have the appropriate certificates.These certificates must be passed to the main Kubernetes API server using the flags `--proxy-client-cert-file` and `--proxy-client-key-file`.  This allows the aggregator to identify itself when making requests, so that addon API servers can use its delegated RequestHeader authentication.


flag| kind |from| to |notes
----|---|---|---|---
--client-ca-file |CA |(clients) |API server |Clients can still use other creds (e.g. bearer token) instead of client cert.
--etcd-cafile| CA| API server| etcd 
--etcd-certfile |client cert| API server| etcd 
--etcd-keyfile| client key |API server |etcd 
--experimental-keystone-ca-file |CA| API server |Keystone instance| Only used for Keystone auth.
--kubelet-certificate-authority |CA |API server |kubelet |If not provided, kubelet serving cert isn't verified.
--kubelet-client-certificate| client cert| API server| kubelet 
--kubelet-client-key |client key |API server |kubelet 
--oidc-ca-fil| CA |API server |OpenID Connect provider |Only used for OIDC auth.
--proxy-client-cert-file |client cert |API server| Aggregated API server| CA bundle is specified in dynamic config.
--proxy-client-key-file| client key| API server |Aggregated API server 
--requestheader-client-ca-file| CA |Authenticating proxy| API server |https://kubernetes.io/docs/admin/authentication/#authenticating-proxy
--service-account-key-file |public key| N/A| N/A |Public (or private) key to verify service account JWTs. Defaults to --tls-private-key-file.
--tls-ca-file| CA |(service accounts) |API server |CA to pass to service accounts to trust API server.
--tls-cert-file| serving cert |(clients) |API server 
--tls-private-key-file| serving key |(clients) |API server 
--tls-sni-cert-key| serving cert/key|(clients) |API server |Can be used to serve traffic based on SNI/

details refer to https://github.com/kubernetes/kubernetes/issues/54665

