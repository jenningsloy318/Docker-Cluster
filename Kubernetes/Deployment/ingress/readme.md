1. Create ssl key
```
kubectl create secret tls foo-secret --key /tmp/tls.key --cert /tmp/tls.crt
```
2. create configmap
```
kubectl create configmap nginx-tmpl --from-file=nginx.tmpl=nginx.tmpl -n kube-system
```

3. vts

vts port is 18080, the ingress nginx controller use https://github.com/vozlt/nginx-module-vts to achive this function.