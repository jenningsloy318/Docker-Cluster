##Tips

    1.1  create ngrinder-key
    ```
    openssl genrsa   -out ngrinder-key.pem 4096
    ```
    1.2  create owl.csr
    ```
    openssl req -new -key ngrinder-key.pem -out ngrinder.csr  -subj "/CN=ngrinder.gcsc.sap.corp" -config openssl-ngrinder.conf
    ```
    1.3 get cert from https://getcerts.wdf.global.corp.sap/pgwy/request/sapnetca_base64.html and  save the cert to owl-cert.pem

    1.4 create configmap 
    ```
    kubectl create secret tls ngrinder-secret --key ngrinder-key.pem --cert ngrinder-cert.pem -n ngrinder
    ```
    