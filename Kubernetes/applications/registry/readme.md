## TLS request

## create Docker server cert
1. create registry-key
```
openssl genrsa  -aes256 -out registry-key.pem 4096
```
2. create registry.csr 

openssl-registry.conf
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
DNS.1=registry.gcsc.lmy.corp
```


```
openssl req -new -key registry-key.pem -out registry.csr  -subj "/CN=registry.gcsc.lmy.corp" -config openssl-registry.conf
```
3. verify the csr 
```
openssl req -in registry.csr  -text -noout
```

4. create secret
```
 kubectl create secret tls registry-secret --key registry-key.pem --cert registry-cert.pem -n registry
 ```