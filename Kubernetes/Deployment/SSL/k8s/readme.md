## Create apiserver certificates
1. create apiserver-key
openssl genrsa -out apiserver-key.pem 4096
2. create openssl-k8s.conf
```
[req]
req_extensions = v3_req
distinguished_name = req_distinguished_name
[req_distinguished_name]
[ v3_req ]
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
subjectAltName = @alt_names
[ v3_ca ]
subjectAltName = @alternate_names
[alt_names]
DNS.1 = kubernetes
DNS.2 = kubernetes.default
DNS.3 = kubernetes.default.svc
DNS.4 = kubernetes.default.svc.cluster.local
DNS.5=cnpvgl56588417.pvg.global.corp.sap
DNS.6=cnpvgl56588418.pvg.global.corp.sap
IP.1 = 192.168.0.1
IP.2=10.58.137.243
IP.3=10.58.137.244
IP.4=127.0.0.1
```
3. create sing request 
```
openssl req -new -key apiserver-key.pem -out apiserver.csr -subj "/CN=cnpvgl56588417.pvg.global.corp.sap" -config openssl-k8s.conf 

```

4. sign apiserver.pem
```
openssl x509 -req -in apiserver.csr -CA ../CA/ca.pem -CAkey ../CA/ca-key.pem -CAcreateserial -out apiserver.pem -days 3650   -extensions v3_req  -extfile   openssl-k8s.conf
```


## Create cluster admin certificates


1. create cluster-admin-key
openssl genrsa -out cluster-admin-key.pem 4096

2. create sign request 

```
openssl req -new -key cluster-admin-key.pem -out cluster-admin.csr -subj "/O=system:masters"
```

3. create openssl-client.conf
 echo -e  "[client_server_ssl]\nextendedKeyUsage = serverAuth,clientAuth" > openssl-client.conf
3 sign cluster-admin.pem

```
openssl x509 -req -in cluster-admin.csr -CA ca.pem -CAkey ca-key.pem -CAcreateserial -out cluster-admin.pem -days 3650   -extfile   openssl-client.conf   -extensions client_server_ssl 
```

## create system:kube-scheduler  certificates 
1. create system:kube-scheduler key 

```
openssl genrsa -out kube-scheduler-key.pem 4096 
```
2. create sign request 
```
openssl req -new -key kube-scheduler-key.pem -out kube-scheduler.csr -subj "/CN=system:kube-scheduler" 
```
3. sign kube-scheduler.pem
```
openssl x509 -req -in kube-scheduler.csr -CA ../CA/ca.pem -CAkey ../CA/ca-key.pem -CAcreateserial -out kube-scheduler.pem -days 3650 
```



## create system:kube-controller-manager  certificates 
1. create system:kube-controller-manager key 

```
openssl genrsa -out kube-controller-manager-key.pem 4096 
```
2. create csr 
```
openssl req -new -key kube-controller-manager-key.pem -out kube-controller-manager.csr -subj "/CN=system:kube-controller-manager" 
```
3. sign csr
```
openssl x509 -req -in kube-controller-manager.csr -CA ../CA/ca.pem -CAkey ../CA/ca-key.pem -CAcreateserial -out kube-controller-manager.pem -days 3650 
```

## create system:kube-proxy  certificates 
1. create system:kube-proxy key 

```
openssl genrsa -out kube-proxy-key.pem 4096 
```
2. create csr 
```
openssl req -new -key kube-proxy-key.pem -out kube-proxy.csr -subj "/CN=system:kube-proxy" 
```
3. sign csr
```
openssl x509 -req -in kube-proxy.csr -CA ../CA/ca.pem -CAkey ../CA/ca-key.pem -CAcreateserial -out kube-proxy.pem -days 3650 
```

## create kubelet  certificates 

1. create kubelet key 

```
openssl genrsa -out kubelet-key.pem 4096 
```
2. create csr 
```
openssl req -new -key kubelet-key.pem -out kubelet-cnpvgl56588417.csr -subj "/O=system:nodes/CN=system:node:cnpvgl56588417" 
openssl req -new -key kubelet-key.pem -out kubelet-cnpvgl56588418.csr -subj "/O=system:nodes/CN=system:node:cnpvgl56588418" 

```
3. sign csr
```
openssl x509 -req -in kubelet-cnpvgl56588417.csr -CA ../CA/ca.pem -CAkey ../CA/ca-key.pem -CAcreateserial -out kubelet-cnpvgl56588417.pem -days 3650 
openssl x509 -req -in kubelet-cnpvgl56588418.csr -CA ../CA/ca.pem -CAkey ../CA/ca-key.pem -CAcreateserial -out kubelet-cnpvgl56588418.pem -days 3650 

```

