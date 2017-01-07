Description:
--
My demo environment has two hosts, one is used for master and the other one is node. and I will use traditional systemd to run these services.

1. Hosts: 
  
  | hostname    | IP address     | 
  | ----------- | -------------- | 
  | kube-master | 192.168.49.141 | 
  | kube-node1: | 192.168.49.135 | 

2. Software version:

  | Component    | Version         | 
  | -----------  |-----------------|
  | OS           | Ubuntu 16.04.1  |     
  | Kubernetes   | 1.5.1           |     
  | etcd         | 3.0.15          |      
  | docker       | 1.12.5          |      


Preparation before install:
--



1. Network : CNI model with calico plugin, in the nework area, there are IP ranges: 	 

  1.1 container IP: defaut is ```172.17.0.1/16```.

  1.2 Pod IP: Defined in calico plugin, default is ```192.168.0.0/16```.

  1.3 service cluster IP:  defined when aipserver is started with ```--service-cluster-ip-range=10.96.0.0/12``` .

2. DNS:

  2.1  DNS is also considered, since calico/dashboard may need DNS to resolve the IP address inside the cluster.


3. Installation sequence:

  3.1 etcd service on master

  3.2 apiservice service on master

  3.3 controller-manager/scheduler service on master

  3.4 kubelet/kube-proxy on master and node.


Authentication in Kubernetes:

1. there are two kinds of users in kubenetes, normal user and service account. 
    * normal users are managed by priviate key, key store(keystone/google account) or a file which contains the user list. 
    * service accounts are users managed by the Kubernetes API. They are bound to specific namespaces, and created automatically by the API server or manually through API calls.
    * API requests are tied to either a normal user or a service account, or are treated as anonymous requests. 
    * every process inside or outside the cluster must authenticate when making requests to the API server, or be treated as an anonymous user.
2. authentication strategies.
    * client certificates
    * bearer tokens
    * authenticating proxy
    * HTTP basic auth
3. users authenticate torwards kubernetes API have following attributes
    * Username: a string which identifies the end user. Common values might be kube-admin or jane@example.com.
    * UID: a string which identifies the end user and attempts to be more consistent and unique than username.
    * Groups: a set of strings which associate users with as set of commonly grouped users.
    * Extra fields: a map of strings to list of strings which holds additional information authorizers may find useful.
4. authentication method
    * Client certificate authentication, enabled by passing ```--client-ca-file=``` to apiserver, which need to generate client certificate. 
    * Static Token authentication, enabled by passing ```--token-auth-file=``` to apiserver, we should create a token file which contains columns "token,user,uid [,group1,group2,group3]" (groups are optional).
    * Basic authentication, enabled by passing ```--basic-auth-file=``` to apiserver, a stack user,password,uid file will be created.
    * Service Account authentication, Service accounts are usually created automatically by the API server and associated with pods running in the cluster through the ServiceAccount Admission Controller. this also need a cert by passing ```--service-account-key-file ```, if not present, it will use ```--tls-private-key-file```.
5. certificates used in the cluster
    * apiserver certificate: used in https to secure connections to apiserver via 6443 port.
    * service account certificate, used when a pod is deployed in cluster , which need to communicate with apiserver or outside network.
    * client certificate, used in node to connect to master. 
    * all three types of certificate can share same key pairs.
5. Authentications used in kubernetes
    * we should create basic auth, with user/password to provide the login to dashboard.
    * service account is mandatory as described in preceeding section.


Problems during the installation
--

1. certificate issue, these symtoms  appear when configure kubelet on node to connect master, or when depoy dashboard pod cluster.

  1.1 ```x509: failed to load system roots and no roots provided``` 

  1.2 ```x509: certificate signed by unknown authority ```

  1.3 ```certificate is valid for 192.168.49.141, 10.96.0.1, not 192.168.49.135.```

  1.4  ```Failed to setup network for pod "kube-dns-v20-swgmq_kube-system(ff5766a0-d3ce-11e6-b0ed-000c29394d5c)" using network plugins "cni": pods "kube-dns-v20-swgmq" not found; Skipping pod : this is because of wrong configured```

  Investigation:
  *  check the apiserver service log;
  * check regarding pod log  by issuing ```kubectl logs pod/pod-id ``` or ```kubectl describe pod/pod-id```  show all the procedures of deploying that pod.
  
  Solution:
  * remove the service accounts secrets  by two commands; ```kubectl get secretes --all-namespaces``` to get all secretes; then ```kubectl delete secrete/secrete-name -n kube-system``` or ``` kubectl delete secrete/secrete-name ```, the secrets will automatically re-created by kubernetes;
  * re-generate the apiserver certifice, **don't forget to add/modify the IP.1 in openssl.cnf with the first IP of service-cluster-ip and IP.2 with apiserver/master IP**. 
2. ```connection refused```: this can be found in deploying the dashboard/kubedns.
   Investigation:
   * be sure configure the correct apiserver IP address in other service configuration, it should be the ```http://localhost:8080``` or ```https://192.168.49.141:6443```.
   * pod/service which need to connect apiserver actually will connect its first IP of ```service_cluster_ip_range```, ```10.96.0.1:443``` for example here, then this IP address will forward the request to real apiserver. this IP address is created when the cluster is up . 

3. other errors:

  3.1  Failed to setup network for pod "kube-dns-v20-swgmq_kube-system(ff5766a0-d3ce-11e6-b0ed-000c29394d5c)" using network plugins "cni": pods "kube-dns-v20-swgmq" not found; Skipping pod 
    * cause is : the incorrect configuration of following valube in the calico calico,yaml when deploy the cni network by excute ```kubectl apply -f calico.yaml```;
      
      ```conf
            - name: K8S_API
              value: "https://kubernetes.default:443"
      ````
    * symtom: this happens when deploy kubedns/dashboard pods, both of them need request network info from calico, eventually need to connect to apiserver to retrieve these info, but calico is misconfigured so it can't get IP address through calico, so the pod can't be created.

   * solution, leave it there when it can cooperate with kubedns to resolve this IP to ```10.96.0.1``` , so after kubedns is created, this issue is gone. or change it to that ip which is the first ip of service cluster range.  the only thing to remember is to update the value ```etcd_endpoints: "http://192.168.49.141:2379"```, we may fail to deploy calico, most of the cases are  the certificate issue or the secrets are incorrect, just re-create all apiserver cert and delelete all secrets in all namespaces.


Installation
--

**Configure on master node**



**1. Get kubernetes binary and etcd binary.**

  1.1 get kubernetes binary 
   
   ```shell
   
   # wget https://github.com/kubernetes/kubernetes/releases/download/v1.5.0/kubernetes.tar.gz
   # untar kubernetes.tar.gz 
   # cd kubernetes
   # cluster/get-kube-binaries.sh
   Kubernetes release: v1.5.0
   Server: linux/amd64
   Client: linux/amd64
   
   Will download kubernetes-server-linux-amd64.tar.gz from https://storage.googleapis.com/kubernetes-release/release/v1.5.0
   Will download and extract kubernetes-client-linux-amd64.tar.gz from https://storage.googleapis.com/kubernetes-release/release/v1.5.0
   
   Will download and extract kubernetes-client-linux-amd64.tar.gz from https://storage.googleapis.com/kubernetes-release/release/v1.5.0
   Is this ok? [Y]/n y
   
   
   kubernetes/server/kubernetes-server-linux-amd64.tar.gz 
   kubernetes/client/kubernetes-client-linux-amd64.tar.gz 
   
   #tar xf kubernetes/server/kubernetes-server-linux-amd64.tar.gz 
   # tar xf kubernetes/client/kubernetes-client-linux-amd64.tar.gz 
  
   ```

   then copy all binaries to /usr/bin on master and node 

  1.2 get etcd binary
    
   ```shell
   # wget https://github.com/coreos/etcd/releases/download/v3.0.15/etcd-v3.0.15-linux-amd64.tar.gz
   #tar xf etcd-v3.0.15-linux-amd64.tar.gz
   ```

   then copy all binary to /usr/bin

**2. Start etcd on master.**

   copy [etcd.service](./init/etcd.service) to /etc/systemd/system/multi-user.target.wants/;
   
   copy [etcd.conf](./conf/etcd.conf) to /etc/etcd/
   
   ```shell
   #systemctl daemon-reload
   #systemctl start etcd
   # ss -lptn | column -n |grep etcd
   LISTEN     0      128         :::2379                    :::*                   users:(("etcd",pid=2108,fd=6))
   LISTEN     0      128         :::2380                    :::*                   users:(("etcd",pid=2108,fd=5))
    
   ```

**3 prepare the authentications for communication between master and node.**

 *create certification for  authentication, using openssl.*


 3.1  create CA key pair.
   * Create CA priviate key
      
   ```shell
          # openssl genrsa -out ca-key.pem 2048
   ```

   * Extract the public key
       
   ```shell
            # openssl rsa -in ca-key.pem -pubout -out ca-pub.pem
   ```

   * create CA  self  signed cert
        
   ```shell
            # openssl req -x509 -new -nodes -key ca-key.pem -days 10000 -out ca.pem -subj "/CN=kube-ca"
   ```


 3.2  Create apiserver key pair signed by preceding created CA.
   * Create CA priviate key
        
   ```shell
            # openssl genrsa -out apiserver-key.pem 2048
   ```

   * Extract the public key
        
    ```shell
            # openssl rsa -in apiserver-key.pem -pubout -out apiserver-pub.pem
    ```
        
   * Edit openssl.cnf to feed the needs,modify the DNS.n and IP.n, the DNSs is the internal service cluster DNS domain, and IP.1 is the first ```IP``` in the ```SERVICE_IP_RANGE```, and IP.2 is the master IP address. refter to [Cluster TLS using OpenSSL](https://coreos.com/kubernetes/docs/latest/openssl.html)
        
    ```shell
        # cat openssl.cnf
        [req]
        req_extensions = v3_req
        distinguished_name = req_distinguished_name
        [req_distinguished_name]
        [ v3_req ]
        basicConstraints = CA:FALSE
        keyUsage = nonRepudiation, digitalSignature, keyEncipherment
        subjectAltName = @alt_names
        [alt_names]
        DNS.1 = kubernetes
        DNS.2 = kubernetes.default
        DNS.3 = kubernetes.default.svc
        DNS.4 = kubernetes.default.svc.cluster.local
        IP.1 = 10.96.0.1
        IP.2 = 192.168.49.141
    ```

   * Create sign request for apiserver key
        
   ```shell
            # penssl req -new -key apiserver-key.pem -out apiserver.csr -subj "/CN=kube-apiserver" -config openssl.cnf
   ```

   * Sign apiserver key

   ```
        #openssl x509 -req -in apiserver.csr -CA ca.pem -CAkey ca-key.pem -CAcreateserial -out apiserver.pem -days 365 -extensions v3_req -extfile openssl.cnf
   ```
 3.3  if we want to create other service account key, repeat step 2. 
 
 3.4 All of these key and cert are stored in /etc/kubernetes/pki. 

**4 start apiserver service**. 

 4.1 command and parameters used when starting apiserver service
   
   ```shell  
   #/usr/bin/hyperkube apiserver \
   --insecure-bind-address=127.0.0.1 \
   --admission-control=NamespaceLifecycle,LimitRanger,ServiceAccount,PersistentVolumeLabel,DefaultStorageClass,ResourceQuota \
   --service-cluster-ip-range=10.96.0.0/12 \
   --service-account-key-file=/etc/kubernetes/pki/apiserver-key.pem \
   --client-ca-file=/etc/kubernetes/pki/ca.pem \
   --tls-cert-file=/etc/kubernetes/pki/apiserver.pem \
   --tls-private-key-file=/etc/kubernetes/pki/apiserver-key.pem \
   --token-auth-file=/etc/kubernetes/pki/tokens.csv \
   --secure-port=6443 \
   --allow-privileged \
   --advertise-address=192.168.49.135 \
   --kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname \
   --anonymous-auth=false \
   --etcd-servers=http://127.0.0.1:2379 \
   --v=5
   ```
   explanation: 

   * ```--admission-control=NamespaceLifecycle,LimitRanger,ServiceAccount,PersistentVolumeLabel,DefaultStorageClass,ResourceQuota ``` : determine the admission control to access apiserver;
   * ```--service-cluster-ip-range=10.96.0.0/12 ```: define the service cluster IP pool,this is mentioned in the openssl,cnf, its first IP(10.96.0.1) is the value of IP.1 ;
   * ```--client-ca-file=/etc/kubernetes/pki/ca.pem ```: CA cert use for signning client certificate, not the ca priviate key or public key;
   * ```--tls-cert-file=/etc/kubernetes/pki/apiserver.pem ```: server certificate
   * ```--tls-private-key-file=/etc/kubernetes/pki/apiserver-key.pem ```: server priviate key
   * ```--token-auth-file=/etc/kubernetes/pki/tokens.csv ```: token authentication
   * ```--etcd-servers=http://127.0.0.1:2379```: **etcd server endpoint**, it is very important;
   * ```--advertise-address=192.168.49.135```:  the IP address on which to advertise the apiserver to members of the cluster.
   
 
 4.2 apiserver service listen at two ports  default, one it http://localhost:8080, which is not encrypted; so when other services running on the same master, it can use this endpoint, the other is https://{external_IP}:6443, whose connections are encrypted by TLS, it serves other node and services securely. 

 4.3 now we use the systemd service file [kube-apiservice.service](./init/kube-apiserver.service) to start apiserver service.

**5. start controller-manager service.**
 
 5.1 prepare the configuration file located  at /etc/kubernetes/admin.conf which can be passed to it via  ```--kubeconfig=```. This file contains the   authorization and master location information.
   
   * setup the cluster info 

   ```shell
   #kubectl config set-cluster kubernetes --certificate-authority=/etc/kubernetes/pki/ca.pem --embed-certs=true --server=https://192.168.49.141:6443 --kubeconfig=/etc/kubernetes/admin.conf
   ```

   * set admin user and context
   
   ```shell
   # kubectl config set-credentials admin --client-certificate=/etc/kubernetes/pki/apiserver.pem --client-key=/etc/kubernetes/pki/apiserver-key.pem --embed-certs=true  --kubeconfig=/etc/kubernetes/admin.conf
   # kubectl config set-context admin@kubernetes --cluster=kubernetes --user=admin  --kubeconfig
   ```

   * set kubelet user and context
   
   ```shell
   # kubectl config set-credentials kubelet --client-certificate=/etc/kubernetes/pki/apiserver.pem --client-key=/etc/kubernetes/pki/apiserver-key.pem --embed-certs=true  --kubeconfig=/etc/kubernetes/admin.conf
   # kubectl config set-context kubelet@kubernetes --cluster=kubernetes --user=kubelet  --kubeconfig=/etc/kubernetes/admin.conf
   ```

   * set current context 

   ```shell
   # kubectl config  use-context admin@kubernetes  --kubeconfig=/etc/kubernetes/admin.conf
   ```
 5.2  command and  parameters used in starting controller-manager
  
   ```shell
    #/usr/bin/hyperkube controller-manager \
   --leader-elect --master=http://localhost:8080 \
   --cluster-name=kubernetes \
   --root-ca-file=/etc/kubernetes/pki/ca.pem \
   --service-account-private-key-file=/etc/kubernetes/pki/apiserver-key.pem \
   --cluster-signing-cert-file=/etc/kubernetes/pki/ca.pem \
   --cluster-signing-key-file=/etc/kubernetes/pki/ca-key.pem \
   --kubeconfig=/etc/kubernetes/admin.conf \
   --v=5  
   ```

   explanation: 

   * ```--root-ca-file=/etc/kubernetes/pki/ca.pem ``` : This **root certificate authority** will be included in service account's token secret. This must be a valid PEM-encoded CA bundle.

   * ```--cluster-signing-cert-file=/etc/kubernetes/pki/ca.pem ```: Filename containing a PEM-encoded X509 **CA certificate** used to issue cluster-scoped certificates.
   * ```--cluster-signing-key-file=/etc/kubernetes/pki/ca-key.pem```: Filename containing a PEM-encoded RSA or ECDSA **private key** used to sign cluster-scoped certificates
   * ```--kubeconfig=/etc/kubernetes/admin.conf```: kubeconfig file with authorization and master location information.
 
 5.3 now we can use [kube-controller-manager.service](./init/kube-contorller-manager.service) to start controller-manager service.


**6. start scheduler service**
 
 6.1 prepare the confi file, this file is identical  with the one used in controller-manager service.

 6.2 command and parameters used to start scheduler service
   
   ```shell
   /usr/bin/hyperkube scheduler \
   --master=http://localhost:8080 \
   --leader-elect=true \
   --kubeconfig=/etc/kubernetes/admin.conf \
   --v=2 
   ```

   explanation

   * ```--master=http://localhost:8080```: is the address of apiserver endpoint
   * ```--kubeconfig=/etc/kubernetes/admin.conf```: kubeconfig file with authorization and master location information.

   
 6.3 now we can start scheduler service via [scheduler service file] (./init/kube-scheduler.service)

**Untill now all master services are started, since in most cases, master can also be node role, so next step we will configure kubelte and kube-proxy service to provide node function**

**7. (optional) start kubelet service.**

 7.1 set the conf file /etc/kubernetes/kubelet.conf
    
   * at this point, the node role is co-exist with master node, so the conf is same with admin.conf, we can just copy admin.conf to kubelet.conf

 7.2 command and parameters to start kubelet service. 
   
   ```shell
   # /usr/bin/kubelet --kubeconfig=/etc/kubernetes/kubelet.conf --require-kubeconfig=true --allow-privileged=true \
   --network-plugin=cni --cni-conf-dir=/etc/cni/net.d --cni-bin-dir=/opt/cni/bin \
   --cluster-dns=10.96.0.10 --cluster-domain=cluster.local
   ```

   explanation

   * ``` --network-plugin=cni --cni-conf-dir=/etc/cni/net.d --cni-bin-dir=/opt/cni/bin```: we should use third-party plugins to provide the network function, later we will deploy calico plugin with pod.


  * ``` --cluster-dns=10.96.0.10 --cluster-domain=cluster.local```: this setting is related with the cluster internal DNS setting, we will deploy the DNS pod after calico is deployed. 

 7.3 now we can use [kubelet.service](./init/kubelet.service) to start kubelet 

**8. (optional) start kube-proxy service .**
 
 8.1 for simplistic, this service is to make TCP,UDP stream forwarding or round robin TCP,UDP forwarding accross the cluster.
 
 8.2 command and parameters used to start kube-proxy service

   ```shell
   #/usr/bin/hyperkube proxy --kubeconfig=/etc/kubernetes/kubelet.conf --master=https://192.168.49.141:6443
   ```
 8.3 now we can start kube-proxy by [kube-proxy.service](./init/kube-proxy.service)


**9. now this cluster is up without network plugin, as I mentioned earlier, I will install calico plugin to provide the networking.**
  
  From the homepage of calico, there are several deployment types. here I choose [Standard Hosted Install](http://docs.projectcalico.org/v2.0/getting-started/kubernetes/installation/hosted/hosted)

  the only thing which need to chagne is ```etcd_endpoints: https://192.168.49.141:6443``` in calico.yaml, and then create it. 
  
  ```shell 
  # wget http://docs.projectcalico.org/v2.0/getting-started/kubernetes/installation/hosted/calico.yaml
  
  change the etcd_endpoints value
  
  # kubectl apply -f calico.yaml
  ```
  all pods and networkpolicies will be deployed without any errors, although  below dns may be not correctly resolved, but after DNS is resolved, it will be ok. actually this name will resolved to ```10.96.0.1```, the first IP of service cluster.
  
  ```yaml
   - name: K8S_API
     value: "https://kubernetes.default:443"
  ```

  next step is to deploy kubeDNS

**10. install kubeDNS in kubernetes cluster to provide internal dns parse.**

 10.1 since we don't bring up kubeDNS with kubernetes cluster, we need to deploy it seperately, first we need to prepar the pod. I got the pod definination from [coreos install addons](https://coreos.com/kubernetes/docs/latest/deploy-addons.html)
   
   The content of the file ```dns-addon.yml```, we need to modify ```${DNS_SERVICE_IP}``` to an address we'd like to set the pod , for example ```10.96.0.10```.

   ```yaml

   apiVersion: v1
   kind: Service
   metadata:
     name: kube-dns
     namespace: kube-system
     labels:
       k8s-app: kube-dns
       kubernetes.io/cluster-service: "true"
       kubernetes.io/name: "KubeDNS"
   spec:
     selector:
       k8s-app: kube-dns
     clusterIP: 10.96.0.10
     ports:
     - name: dns
       port: 53
       protocol: UDP
     - name: dns-tcp
       port: 53
       protocol: TCP
   
   
   ---
   
   
   apiVersion: v1
   kind: ReplicationController
   metadata:
     name: kube-dns-v20
     namespace: kube-system
     labels:
       k8s-app: kube-dns
       version: v20
       kubernetes.io/cluster-service: "true"
   spec:
     replicas: 1
     selector:
       k8s-app: kube-dns
       version: v20
     template:
       metadata:
         labels:
           k8s-app: kube-dns
           version: v20
         annotations:
           scheduler.alpha.kubernetes.io/critical-pod: ''
           scheduler.alpha.kubernetes.io/tolerations: '[{"key":"CriticalAddonsOnly", "operator":"Exists"}]'
       spec:
         containers:
         - name: kubedns
           image: gcr.io/google_containers/kubedns-amd64:1.8
           resources:
             limits:
               memory: 170Mi
             requests:
               cpu: 100m
               memory: 70Mi
           livenessProbe:
             httpGet:
               path: /healthz-kubedns
               port: 8080
               scheme: HTTP
             initialDelaySeconds: 60
             timeoutSeconds: 5
             successThreshold: 1
             failureThreshold: 5
           readinessProbe:
             httpGet:
               path: /readiness
               port: 8081
               scheme: HTTP
             initialDelaySeconds: 3
             timeoutSeconds: 5
           args:
           - --domain=cluster.local.
           - --dns-port=10053
           ports:
           - containerPort: 10053
             name: dns-local
             protocol: UDP
           - containerPort: 10053
             name: dns-tcp-local
             protocol: TCP
         - name: dnsmasq
           image: gcr.io/google_containers/kube-dnsmasq-amd64:1.4
           livenessProbe:
             httpGet:
               path: /healthz-dnsmasq
               port: 8080
               scheme: HTTP
             initialDelaySeconds: 60
             timeoutSeconds: 5
             successThreshold: 1
             failureThreshold: 5
           args:
           - --cache-size=1000
           - --no-resolv
           - --server=127.0.0.1#10053
           - --log-facility=-
           ports:
           - containerPort: 53
             name: dns
             protocol: UDP
           - containerPort: 53
             name: dns-tcp
             protocol: TCP
         - name: healthz
           image: gcr.io/google_containers/exechealthz-amd64:1.2
           resources:
             limits:
               memory: 50Mi
             requests:
               cpu: 10m
               memory: 50Mi
           args:
           - --cmd=nslookup kubernetes.default.svc.cluster.local 127.0.0.1 >/dev/null
           - --url=/healthz-dnsmasq
           - --cmd=nslookup kubernetes.default.svc.cluster.local 127.0.0.1:10053 >/dev/null
           - --url=/healthz-kubedns
           - --port=8080
           - --quiet
           ports:
           - containerPort: 8080
             protocol: TCP
         dnsPolicy: Default
   ```
 


 10.2  we can create it with 
 
   ```shell
   kubectl crate -f dns-addon.yml
   ```

 10.3 check the pod 
   

   ```shell
   # kubectl get pod -n kube-system  -o wide
   NAME                                        READY     STATUS    RESTARTS   AGE       IP               NODE
   kube-dns-v20-hvbbz                          3/3       Running   3          1d        192.168.9.77     kube-node1
   ```

 10.4 check the service 
  
   ```shell
   #kubectl get svc -n kube-system  -o wide
   NAME                   CLUSTER-IP       EXTERNAL-IP   PORT(S)         AGE       SELECTOR
   kube-dns               10.96.0.10       <none>        53/UDP,53/TCP   1d        k8s-app=kube-dns
   ```

   
   
       
