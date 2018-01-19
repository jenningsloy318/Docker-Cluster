##Tips

    1.1  create dashboard-key
    ```
    openssl genrsa   -out owl-key.pem 4096
    ```
    1.2  create owl.csr
    ```
    openssl req -new -key owl-key.pem -out owl.csr  -subj "/CN=owl.gcsc.lmy.corp" -config openssl-owl.conf
    ```
    1.3 get cert from https://getcerts.wdf.global.corp.lmy/pgwy/request/lmynetca_base64.html and  save the cert to owl-cert.pem

    1.4 create configmap 
    ```
    kubectl create secret tls owl-secret --key owl-key.pem --cert owl-cert.pem -n owl
    ```
    