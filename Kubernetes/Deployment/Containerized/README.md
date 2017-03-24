--
This directory contains the scripts to deploy k8s in containerized method.

Now I have tried deploy main master service with pod definiation via kubelet service running on eath master node. 
This time I deploy a tree-master and one loadbalancer k8s cluster.

1. Hosts:

   | hostname    | IP address     |Role |
   | ----------- | -------------- |------|
   | kube-master.example.com | 192.168.49.150 | LB   |
   | kube-master1.example.com | 192.168.49.151 |Master|
   | kube-master2.example.com | 192.168.49.152 |Master|
   | kube-master3.example.com | 192.168.49.153 |Master|
     
     ![Architecture](./imgs/kuberntes-arch.png)

2. Etcd cluster configuration.

   Each etcd instance is boot via kubelet too. we should take care of the one para ```initial-cluster-state: new ``` , if this is is the first time to bootstrap that etcd host, we can set it to ```new```, but if it is  restarted , we should change the valune to ```existing```.
     
   - Case 1 :
      ```error
      etcd: member 9b3523b532ddb797 has already been bootstrapped.
      ```
      we need to change the value to ```existing```.
      
   - Case 2 :
     ```error
     etcd: stopping listening for client requests on https://0.0.0.0:2379
     etcd: stopping listening for peers on https://0.0.0.0:2380
     etcd: cannot fetch cluster info from peer urls: etcdserver: could not retrieve cluster information from the given urls
     ```
     
     This time we should change the value to ```new``` since  maybe the cluster info is lost, we can re-bootstrap it again.

3. Setup a loadbalancer reverse-proxy 3 apiservers, expose only one apiserver endpoint to all cluster, other component(kubelet service) can talk to this loadbalancer eventually communitating to actual apiserver. and also setup a etcd-proxy to connect to etcd cluster also exposing one etcd endpoint, which used in calico to store all network info. 
   apiserver proxy is setup with tcp stream proxy, and etcd-proxy is stup with etcd software with ```proxy: 'on'```, don't forget the single quotation(```'```). I encontered failed without it.
    
     
4. for kublet.service, sometimes when add ```--hostname-override=```  to a readable name is very useful to distinguish each sever when we are running k8s in a cloud, inside the cloud the hostname of each VM is not easy to remember. 


5.  for apiserver service running in pod, it is esential to set ```--kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname```, thus when we issue kubectl commands, it will not to lookup the ip address of each node.  

6.  my script also support to deploy single master k8s, and  has some different parametes in the ```etcd.yaml``` and kubelet service. especially for kubelet service,we'd split them into master and worker node, there are different paramters for the way they connect  to apiserver service. 

7.  KubeDNS

    each pod is created with a ```dnsPolicy``` with value ```ClusterFirst```or ```Default```, default vaule is ClusterFirst.

      - ClusterFirst: use cluster DNS fist, if we set ```--cluster-dns={{ CLUSTER_DNS }} ``` parameter in kubelet service, pod will only have this single nameserver configured.

      - Default: this  setting makes pod to use host dns setting, pod has the same copy of the host /etc/resolv.conf file.


    Our environment has both requirement that pod both need to resolve internal DNS and external DNS, thus we have to change dnsmsasq args.

      - prior to 1.6, we need to change the kubedns.yaml file, modify it as flowing:

        ```yaml

        args:
        - --cache-size=1000
        - --no-resolv
        - --server=127.0.0.1#10053
        - --server={{ nameserver1 }}#53
        - --server={{ nameserver2 }}#53
        - --log-facility=-
        ```

      -  begin with 1.6, k8s provide a component dnsmasq-nanny to manage dnsmasq value from ```kube-system:kube-dns configmap```  , according to ([#41826](https://github.com/kubernetes/kubernetes/pull/41826)), as example [kubeDNS](./scripts/templates/addons/kube-dns.yaml.jinja2).

        ```configmap

        "stubDomains": {
        "acme.local": ["1.2.3.4"]
        },
        ```

        is a map of domain to list of nameservers for the domain, This is used to inject private DNS domains into the kube-dns namespace. In the above example, any DNS requests for *.acme.local will be served by the nameserver 1.2.3.4.


        ```"upstreamNameservers": ["8.8.8.8", "8.8.4.4"]```: is a list of upstreamNameservers to use, overriding the configuration specified in /etc/resolv.conf.


    Also, increase the resource of the  pod, which make its perforance better.

9.  Calico networking. 
    
    I recently meet the issue that, in some pod, it can connect its service IP and other service ip, but other pod, it can't connect to both itself and other service IP. I don't figure the reason,  at the beginning, I thought it maybe the calico itself has some issue, or its network policy setting. but no clue. finally fix this issue by upgraing the whole calico manifest. but it only upgrade the calico-network-policy controller, this issue is gone.
