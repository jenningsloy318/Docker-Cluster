1. create etcd CA. 

    1.1 create EtcdCA-csr.json for `Root CA`
    ```

    {
        "CN": "Kubernetes ETCD CA",
        "hosts": [
        ],
        "key": {
            "algo": "rsa",
            "size": 4096
        },
        "names": [
            {
                "C": "CN",
                "ST": "SC",
                "L": "Chengdu",
                "O": "lmy.com .ltd",
                "OU": "DevOps"
            }
        ],
         "ca": {
        "expiry": "262800h"
         }
    }
    ```
    1.2 Generate the ETCD CA
    ```
    cfssl genkey -initca DockerCA-csr.json | cfssljson -bare DockerCA
    ```


    1.3 Create DockerCA-config.json, which contains profiles of server/client.
    ```
    {
      "signing": {
        "default": {
          "expiry": "8760h"
        },
        "profiles": {
          "server": {
            "usages": [
              "signing",
              "key encipherment",
              "server auth"
            ],
            "expiry": "35040h"
          },
          "client": {
            "usages": [
              "signing",
              "key encipherment",
              "client auth"
            ],
            "expiry": "35040h"
          }
        }
      }
    }
    ``` 
  1.4 Create server/client certs
  ```
  cfssl gencert -ca=DockerCA.pem -ca-key=DockerCA-key.pem -config=DockerCA-config.json -profile=server Docker-server-csr.json | cfssljson -bare docker-server
  cfssl gencert -ca=DockerCA.pem -ca-key=DockerCA-key.pem -config=DockerCA-config.json -profile=client Docker-client-csr.json | cfssljson -bare docker-client
  ```