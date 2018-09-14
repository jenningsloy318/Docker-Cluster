1. create Root CA. 

    1.1 create RootCA-csr.json for `Root CA`
    ```

    {
        "CN": "Kubernetes Root CA",
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
    1.2 Generate the Root CA
    ```
    cfssl genkey -initca ca-csr.json | cfssljson -bare RootCA
    ```


    1.3 Create ca-config.json, which contains profiles of    server/client/intermidiate.
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
          },
          "intermediate": {
                    "expiry": "35040h",
                    "usages": [
                        "signing",
                        "key encipherment",
                        "cert sign",
                        "crl sign"
                    ],
                    "ca_constraint": {
                        "is_ca": true,
                        "max_path_len":1
                    }
                }
        }
      }
    }
    ``` 

2. create Client CA

    2.1 ClientCA-csr.json
    ```
    {
        "CN": "Kubernetes Client CA",
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
    
    2.2
    and then create ClientCA  private key/csr/cert
    ```
    cfssl gencert -initca ClientCA-csr.json | cfssljson -bare  ClientCA
    ```
    
    2.3 finally sign clientCA certs with RootCA
    ```
    cfssl sign -ca RootCA.pem -ca-key RootCA-key.pem -config ca-config.json     -profile=intermediate ClientCA.csr | cfssljson -bare ClientCA
    ```

    2.4 create ClientCA-config.json used to sign the certs of the kubernetes components
    ```

    {
        "signing": {
          "default": {
            "expiry": "8760h"
          },
          "profiles": {
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

3. create RequestHeader  Client CA

    3.1 RequestHeaderClientCA.json
    ```
    {
        "CN": "Kubernetes RequestHeader Client CA",
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
    
    3.2 and then create ClientCA certs,both private key and cert.
    ```
    cfssl gencert -initca RequestHeaderClientCA.json | cfssljson -bare  RequestHeaderClientCA
    ```
    
    3.3 finally sign clientCA certs with RootCA
    ```
    cfssl sign -ca RootCA.pem -ca-key RootCA-key.pem -config ca-config.json     -profile=intermediate RequestHeaderClientCA.csr | cfssljson -bare RequestHeaderClientCA
    ```
4. create certificates for kubernetes components

    4.1 apiserver certs, create kube-apiserver-csr.json
    
    ```
    {
      "CN": "apiserver",
      "hosts": [
        "127.0.0.1",
        "192.168.59.201",
        "192.168.59.202",
        "192.168.59.203",
         "192.168.0.1",
        "kubernetes",
        "kubernetes.default",
        "kubernetes.default.svc",
        "kubernetes.default.svc.cluster.local",
        "kube-master1",
        "kube-master2",
        "kube-master3",
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
      ]
    }
    ```
    and Sign kube-apiserver certs
    ```
    cfssl gencert -ca=RootCA.pem -ca-key=RootCA-key.pem -config=RootCA-config.json -profile=server kube-apiserver-csr.json | cfssljson -bare kube-apiserver
    ```

    ## Except apiserver certs, all other components will be signed by ClientCA,not RootCA.



    4.2 kube-controller-manager cert, create  kube-controller-manager-csr.json
    ```
    {
        "CN": "kube-controller-manager",
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
        ]
    }
    ```
    and Sign kube-controller-manager certs

    ```
    cfssl gencert -ca=ClientCA.pem -ca-key=ClientCA-key.pem -config=ClientCA-config.json -profile=client kube-controller-manager-csr.json | cfssljson -bare kube-controller-manager
    ```




    4.3 kube-scheduler cert, create  kube-scheduler-csr.json
    ```
    {
        "CN": "system:kube-scheduler",
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
        ]
    }
    ```
    and Sign kube-controller-manager certs

    ```
    cfssl gencert -ca=ClientCA.pem -ca-key=ClientCA-key.pem -config=ClientCA-config.json -profile=client kube-scheduler-csr.json | cfssljson -bare kube-scheduler
    ```


    4.3 kube-proxy cert, create  kube-proxy-csr.json
    ```
    {
        "CN": "system:kube-proxy",
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
        ]
    }
    ```
    and Sign kube-proxy certs

    ```
    cfssl gencert -ca=ClientCA.pem -ca-key=ClientCA-key.pem -config=ClientCA-config.json -profile=client kube-proxy-csr.json | cfssljson -bare kube-proxy
    ```
    4.4 kube-kubelet cert, create  kube-kubelet-csr.json
    ```
    {
        "CN": "system:node:kube-node",
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
        ]
    }
    ```
    and Sign kube-proxy certs

    ```
    cfssl gencert -ca=ClientCA.pem -ca-key=ClientCA-key.pem -config=ClientCA-config.json -profile=client kube-proxy-csr.json | cfssljson -bare kube-proxy
    ```

    4.5 create proxy certs for apiserver signed by  RequestHeader Client CA,create RHClient-apiserver-csr.json
    ```
    {
        "CN": "system:kube-apiserver",
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
        ]
    }
    ```    
    then sign the cert
    ```
    cfssl gencert -ca=RequestHeaderClientCA.pem -ca-key=RequestHeaderClientCA-key.pem -config=RequestHeaderClientCA-config.json -profile=client RHClient-apiserver-csr.json| cfssljson -bare RHClient-apiserver
    ```

    4.5 create kubelet certs
        - kubelet-192.168.59.201-csr.json
        ```
        {
        "CN": "system:node:192.168.59.201",
        "key": {
            "algo": "rsa",
            "size": 4096
        },
        "names": [
            {
                "C": "CN",
                "ST": "SC",
                "L": "Chengdu",
                "O": "system:nodes",
                "OU": "DevOps"
            }
        ]
        }
        ```
        sign the certs
        ```
        cfssl gencert -ca=ClientCA.pem -ca-key=ClientCA-key.pem -config=ClientCA-config.json -profile=client kubelet-192.168.59.201-csr.json | cfssljson -bare kubelet-192.168.59.201

        ```


        - kubelet-192.168.59.202-csr.json
        ```
        {
        "CN": "system:node:192.168.59.202",
        "key": {
            "algo": "rsa",
            "size": 4096
        },
        "names": [
            {
                "C": "CN",
                "ST": "SC",
                "L": "Chengdu",
                "O": "system:nodes",
                "OU": "DevOps"
            }
        ]
        }
        ```
        sign the certs
        ```
        cfssl gencert -ca=ClientCA.pem -ca-key=ClientCA-key.pem -config=ClientCA-config.json -profile=client kubelet-192.168.59.202-csr.json | cfssljson -bare kubelet-192.168.59.202

        ```
        - kubelet-192.168.59.203-csr.json
        ```
        {
        "CN": "system:node:192.168.59.203",
        "key": {
            "algo": "rsa",
            "size": 4096
        },
        "names": [
            {
                "C": "CN",
                "ST": "SC",
                "L": "Chengdu",
                "O": "system:nodes",
                "OU": "DevOps"
            }
        ]
        }
        ```
        sign the certs
        ```
        cfssl gencert -ca=ClientCA.pem -ca-key=ClientCA-key.pem -config=ClientCA-config.json -profile=client kubelet-192.168.59.203-csr.json | cfssljson -bare kubelet-192.168.59.203

        ```
        - kubelet-192.168.59.204-csr.json
        ```
        {
        "CN": "system:node:192.168.59.204",
        "key": {
            "algo": "rsa",
            "size": 4096
        },
        "names": [
            {
                "C": "CN",
                "ST": "SC",
                "L": "Chengdu",
                "O": "system:nodes",
                "OU": "DevOps"
            }
        ]
        }
        ```
        sign the certs
        ```
        cfssl gencert -ca=ClientCA.pem -ca-key=ClientCA-key.pem -config=ClientCA-config.json -profile=client kubelet-192.168.59.204-csr.json | cfssljson -bare kubelet-192.168.59.204

        ```        