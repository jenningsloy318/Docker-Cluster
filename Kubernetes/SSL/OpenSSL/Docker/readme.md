## create Docker server cert
1. create docker-key
```
openssl genrsa -out docker-key.pem 4096
```
2. create docker.csr 

openssl-docker.conf
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
IP.1=10.58.137.243
IP.2=10.58.137.244
IP.3=127.0.0.1
DNS.1=cnpvgl56588418.pvg.global.corp.lmy
DNS.2=cnpvgl56588417.pvg.global.corp.lmy
```


```
openssl req -new -key docker-key.pem -out docker.csr  -subj "/CN=cnpvgl56588417.pvg.global.corp.lmy" -config openssl-docker.conf
```
3. verify the csr 
```
openssl req -in docker.csr  -text -noout
```
4. sign the csr
```
openssl x509 -req -in docker.csr -CA ../CA/ca.pem -CAkey ../CA/ca-key.pem -CAcreateserial -out docker.pem -days 3650 -extensions v3_req -extfile openssl-docker.conf
```
5. verify the cert 
```
openssl x509 -in docker.pem -text -noout
```
## create docker client cert 

1. create dockerclient-key.pem
```
openssl genrsa -out dockerclient-key.pem 4096
```
2. create csr 
```
openssl req -subj '/CN=client' -new -key dockerclient-key.pem -out dockerclient.csr
```

3. create extfile.cnf
```
echo "extendedKeyUsage = clientAuth" > docker-client.cnf
```
3. sign csr 
``` 
openssl x509 -req -in dockerclient.csr -CA ../CA/ca.pem -CAkey ../CA/ca-key.pem -CAcreateserial -out dockerclient.pem -days 3650   -extfile   docker-client.cnf

## configure tls in /etc/docker/daemon.json

```
    "hosts": ["tcp://0.0.0.0:2376","unix:///var/run/docker.sock"]
    "tlsverify" : true,
    "tlscacert": "/etc/docker/ssl/ca.pem",
    "tlscert": "/etc/docker/ssl/docker.pem",
    "tlskey": "/etc/docker/ssl/docker-key.pem"
```


## verify the connection
```
docker --tlsverify --tlscacert=../CA/ca.pem  --tlscert=dockerclient.pem  --tlskey=dockerclient-key.pem -H=cnpvgl56588417.pvg.global.corp.lmy:2376 version

Client:
 Version:      1.12.6
 API version:  1.24
 Go version:   go1.6.4
 Git commit:   78d1802
 Built:        Tue Jan 10 20:38:45 2017
 OS/Arch:      linux/amd64

Server:
 Version:      1.12.6
 API version:  1.24
 Go version:   go1.6.4
 Git commit:   78d1802
 Built:        Tue Jan 10 20:38:45 2017
 OS/Arch:      linux/amd64
 ```