--
This directory contains the scripts to deploy k8s in containerized method.

Now I have tried deploy main master service with pod definiation via kubelet service running on eath master node. 
This time I deploy a tree-master and one loadbalancer k8s cluster.

1. Hosts:

   | hostname    | IP address     |Role |
   | ----------- | -------------- |------|
   | kube-master | 192.168.49.150 | LB   |
   | kube-master1 | 192.168.49.151 |Master|
   | kube-master2 | 192.168.49.152 |Master|
   | kube-master3 | 192.168.49.153 |Master|
     

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
   apiserver proxy is setup with tcp stream proxy, and etcd-proxy is stup with etcd software with ```proxy: 'on'```, don't forget the single quotation(```,```). I encontered failed without it.



