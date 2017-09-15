## set JENKINS_OPTS
```
JENKINS_OPTS --httpPort=-1 --httpsPort=8083 --httpsCertificate=/var/lib/jenkins/cert --httpsPrivateKey=/var/lib/jenkins/pk --prefix=/jenkins
JENKINS_HOME /var/jenkins_home/
```

## we can place all initial conf to $JENKINS_HOME/init.groovy.d

    - tcp-slave-agent-port.groovy
    - ...


##. create TLS key and request, used for configure the https for jenkins
  
- create jenkins-key

    ```
    openssl genrsa   -out jenkins-key.pem 4096
    ```
-  create dashboard.csr
    ```
    openssl req -new -key jenkins-key.pem -out jenkins.csr  -subj "/CN=jenkins.gcsc.sap.corp" -config openssl-jenkins.conf
    ```
- get cert from https://getcerts.wdf.global.corp.sap/pgwy/request/sapnetca_base64.html and save the cert to jenkins-cert.pem

- create secret 
    ```
    kubectl create secret tls jenkins-tls  --key jenkins-key.pem --cert jenkins-cert.pem    
    ```

- create keystore 
    ```
    openssl pkcs12 -export -in jenkins-cert.pem   -inkey jenkins-key.pem -name "jenkins-keystore" -out jenkins-keystore.p12
    ```

- create secret for keystore
    ```
    kubectl create secret generic jenkins-tls-keystore --from-file=jenkins-keystore.p12
    ```

##. Extra conf

1. Configure Global Security

    if we use AD for authentication, we can set set following two parameters in order to accelerate the access speed.
    ![Configure-Global-Security](./imgs/Configure-Global-Security.jpg)
    
    - `Remove irrelevant groups`
    - `Enable cache` and `Cache TTL`