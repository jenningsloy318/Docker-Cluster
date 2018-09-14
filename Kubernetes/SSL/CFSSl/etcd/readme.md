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
    cfssl genkey -initca EtcdCA-csr.json | cfssljson -bare EtcdCA
    ```


    1.3 Create EtcdCA-config.json, which contains profiles of server/client.
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
    1.4 Create certs
    ```
    cfssl gencert -ca=EtcdCA.pem -ca-key=EtcdCA-key.pem -config=EtcdCA-config.json -profile=server Etcd-server-csr.json | cfssljson -bare etcd-server
    cfssl gencert -ca=EtcdCA.pem -ca-key=EtcdCA-key.pem -config=EtcdCA-config.json -profile=peer Etcd-peer-csr.json | cfssljson -bare etcd-peer
    cfssl gencert -ca=EtcdCA.pem -ca-key=EtcdCA-key.pem -config=EtcdCA-config.json -profile=client Etcd-client-csr.json | cfssljson -bare etcd-client
    ```