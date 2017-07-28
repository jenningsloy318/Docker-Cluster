1. Create ssl key
```
kubectl create secret tls foo-secret --key /tmp/tls.key --cert /tmp/tls.crt
```
2. create configmap for nginx tmplate
```
kubectl create configmap nginx-tmpl --from-file=nginx.tmpl=nginx.tmpl -n kube-system
```

3. vts

vts port is 18080, the ingress nginx controller use https://github.com/vozlt/nginx-module-vts to achive this function.

4. enable TCP loadbalancing by creating [tcp configmap](./tcp-configmap.yaml) and pass the parameter `--tcp-services-configmap=$(POD_NAMESPACE)/tcp-configmap` to ingress controller. official [example](https://github.com/kubernetes/ingress/tree/master/examples/tcp/nginx).

Note:

1. more conf https://github.com/kubernetes/ingress/blob/master/controllers/nginx/configuration.md

2. Annotations


|Name |	type|
|-----|--------
|ingress.kubernetes.io/add-base-url|	true or false
|ingress.kubernetes.io/affinity|	true or false
|ingress.kubernetes.io/auth-realm	|string
|ingress.kubernetes.io/auth-secret	|string
|ingress.kubernetes.io/auth-type|	basic or digest
|ingress.kubernetes.io/auth-url|	string
|ingress.kubernetes.io/auth-tls-secret|	string
|ingress.kubernetes.io/auth-tls-verify-depth|	number
|ingress.kubernetes.io/enable-cors|	true or false
|ingress.kubernetes.io/force-ssl-redirect|	true or false
|ingress.kubernetes.io/limit-connections|	number
|ingress.kubernetes.io/limit-rps	number|
|ingress.kubernetes.io/proxy-body-size|	string
|ingress.kubernetes.io/rewrite-target|	URI
|ingress.kubernetes.io/secure-backends	|true or false
|ingress.kubernetes.io/session-cookie-name|	string
|ingress.kubernetes.io/session-cookie-hash	|string
|ingress.kubernetes.io/ssl-redirect	true| or false
|ingress.kubernetes.io/upstream-max-fails|	number
|ingress.kubernetes.io/upstream-fail-timeout|	number
|ingress.kubernetes.io/whitelist-source-range|	CIDR

- ingress.kubernetes.io/affinity: enables and sets the affinity type in all Upstreams of an Ingress. This way, a request will always be directed to the same upstream server.
- Server-side HTTPS enforcement through redirect: 
  By default the controller redirects (301) to HTTPS if TLS is enabled for that ingress. If you want to disable that behaviour globally, you can use ssl-redirect: "false" in the NGINX config map.

  To configure this feature for specific ingress resources, you can use the ingress.kubernetes.io/ssl-redirect: "false" annotation in the particular resource.

  When using SSL offloading outside of cluster (e.g. AWS ELB) it may be usefull to enforce a redirect to HTTPS even when there is not TLS cert available. This can be achieved by using the ingress.kubernetes.io/force-ssl-redirect: "true" annotation in the particular resource.
- SSL Passthrough

  The annotation ingress.kubernetes.io/ssl-passthrough allows to configure TLS termination in the pod and not in NGINX. This is possible thanks to the ngx_stream_ssl_preread_module that enables the extraction of the server name information requested through SNI from the ClientHello message at the preread phase.

  Important: using the annotation ingress.kubernetes.io/ssl-passthrough invalidates all the other available annotations. This is because SSL Passthrough works in L4 (TCP).





