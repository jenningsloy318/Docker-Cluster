1. create ca-key.pem

```
openssl genrsa -aes256  -out ca-key.pem 4096
```
  - set password to devops
2. self sign 
```
openssl req -x509 -new -nodes -key ca-key.pem -days 10000 -out ca.pem
Enter pass phrase for ca-key.pem:
You are about to be asked to enter information that will be incorporated
into your certificate request.
What you are about to enter is what is called a Distinguished Name or a DN.
There are quite a few fields but you can leave some blank
For some fields there will be a default value,
If you enter '.', the field will be left blank.
-----
Country Name (2 letter code) [AU]:CN
State or Province Name (full name) [Some-State]:SH
Locality Name (eg, city) []:SH
Organization Name (eg, company) [Internet Widgits Pty Ltd]:SAP
Organizational Unit Name (eg, section) []:CSC
Common Name (e.g. server FQDN or YOUR name) []:CDDEVOPS
Email Address []:DL_57BA68805F99B710F600001A@exchange.sap.corp
```
