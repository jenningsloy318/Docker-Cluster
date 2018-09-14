
# Officially deploy a production kubernetes cluster #

# prequisistes #

  1. check the docker and other componenet requirements before deploying the cluster, visit the [Kubernetes CHANGELOG](https://github.com/kubernetes/kubernetes/blob/master/CHANGELOG.md), and find the section `External Dependency Version Information`.
  2. build docker images with `docker build --rm --force-rm  --no-cache --tag XXX . `
  3. configure systemd to enable more cgroup controllers, since kubelet (https://github.com/kubernetes/kubernetes/blob/release-1.7/pkg/kubelet/cm/cgroup_manager_linux.go, to check the keyword 'whitelistControllers' ) will check if  `"cpu", "cpuacct", "cpuset", "memory", "hugetlb", "systemd"`  exist in the cgroup hierarchy. edit `/etc/systemd/system.conf`:
    
    
  ```
  JoinControllers=cpu,cpuacct,cpuset,net_cls,net_prio,hugetlb,memory
  ```
    This will resove the error `failed to run Kubelet: invalid configuration: cgroup-root "/container.slice/" doesn't exist:`, when specified `--cgroup-root=/container.slice/` in kubelet.service.

  4. enable CPUAccounting  and MemoryAccounting  by modify `/etc/systemd/system.conf`:
  ```
  DefaultCPUAccounting=true 
  DefaultMemoryAccounting=true
  ```
  5. check for the kernel, for ubuntu 16.04.3, install latest kernel `apt install  linux-image-generic-hwe-16.04 linux-headers-generic-hwe-16.04 -y` 
# Deployment #
1. create cgroup slices
    
    - [container.slice](./systemd/container.slice), used for containers and pods

        ```
        [Unit]
        Description=Limited resources Slice
        DefaultDependencies=no
        Before=slices.target
        Requires=-.slice
        After=-.slice
        [Slice]
        MemoryLimit=48G

        ```
    - [kubesvc.slice](./systemd/kubesvc.slice), used for kubelet and docker runtime processes

        ```
        [Unit]
        Description=Limited resources Slice
        DefaultDependencies=no
        Before=slices.target
        Requires=-.slice
        After=-.slice
        [Slice]
        MemoryLimit=4G

        ```        

    - [system.slice](./systemd/system.slice), used for other processes

        ```
        MemoryLimit[Unit]
        Description=Limited resources Slice for system services
        DefaultDependencies=no
        Before=slices.target
        Requires=-.slice
        After=-.slice

        [Slice]
        MemoryLimit=4G
        ```
    `MemoryLimit`: set the memory limits in cgroup v1.

    MemoryHigh and MemoryMax are cgroup v2 memory limits which will replace MemoryLimit in future.
  
    more description on resouce control, refer to [systemd.resource-control](https://www.freedesktop.org/software/systemd/man/systemd.resource-control.html)
    and [cgroupv2: Linux's new unified control group hierarchy](https://fosdem.org/2017/schedule/event/cgroupv2/)。

     to enable cgroup2 in kernel >4.6, modify `GRUB_CMDLINE_LINUX=" "` in file ` /etc/default/grub`,  to `GRUB_CMDLINE_LINUX="systemd.unified_cgroup_hierarchy=1 cgroup_no_v1=all"`, but right now cpu controller is not merged into main kernel, so we can't use cgroup v2 right now.

2. Deploy and configure docker engine

    2.1 get the docker-engine file 
    - for deb from [https://download.docker.com/linux/](https://download.docker.com/linux/)

    2.2 install docker-engine 

      ```
      # dpkg -i docker-ce_17.03.2~ce-0~ubuntu-xenial_amd64.deb 
      # apt install -f 
      ```
      or

      ```
      #yum install https://download.docker.com/linux/centos/7/x86_64/stable/Packages/docker-ce-17.03.2.ce-1.el7.centos.x86_64.rpm
      ``` 
    
    2.3 modify systemd service file [docker.service](./systemd/docker.service)

      - add `Slice=kubesvc.slice` into the `[service]` section, this will place docker service in kubesvc.slice.
      - add HTTP_PROXY / HTTPS_PROXY Environment, 
      - since we have moved all docker conf to `/etc/docker/daemon.json`, then modify `ExecStart` to `ExecStart=/usr/bin/dockerd`

    2.4 configure docker via [daemon.json](./Docker/daemon.json).serveral things need to mention.
        
      - `cgroup-parent: container.slice`  which means that all container will under be created under  `/container.slice/`.
      - `"exec-opts": ["native.cgroupdriver=systemd"]`,  the cgroup drivers has two types `cgroupfs` and `systemd`, if specified with `systemd`, `cgroup-parent` is `container.slice`, if specified `cgroupfs`,`cgroup-parent` is `/container.slice`.

      - `hosts: ["tcp://0.0.0.0:2375","unix:///var/run/docker.sock"]`, which makes it not only listen to unix socket, but also listen on tcp socket.

      - `log-driver": "journald"`: since we use systemd as init system, we can also use `system-journald` for docker log driver. leveraging journald make all containers logs will be aggreated and sent to journald daemon, thus it is easy for log rotation and other operations, so we don't deal with logs in individual container. In addition to the text of the log message itself, the journald log driver stores the following metadata in the journal with each message:

        Field	|Description
        --------|---------
        CONTAINER_ID|	The container ID truncated to 12 characters.
        CONTAINER_ID_FULL|	The full 64-character container ID.
        CONTAINER_NAME|	The container name at the time it was started. If you use docker rename to rename a container, the new name is not reflected in the journal entries.
        CONTAINER_TAG	|The container tag (log tag option documentation).
        CONTAINER_PARTIAL_MESSAGE|	A field that flags log integrity. Improve logging of long log lines.

      with log driver, we can view logs in two methods: 

      
      * docker logs CONTAINER_ID/CONTAINER_NAME

        ```
        # docker logs 5748929de54c
        10.130.226.76 - - [13/Jul/2017:04:35:40 +0000] "GET / HTTP/1.1" 304 0 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36" "-"
        10.130.226.76 - - [13/Jul/2017:04:35:41 +0000] "GET / HTTP/1.1" 304 0 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36" "-"
        10.130.226.76 - - [13/Jul/2017:04:35:41 +0000] "GET / HTTP/1.1" 304 0 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36" "-"
        10.130.226.76 - - [13/Jul/2017:04:35:41 +0000] "GET / HTTP/1.1" 304 0 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36" "-"
        ```

        * journalctl CONTAINER_ID=xxx or CONTAINER_NAME=xxx
        ```~~****~~
        journalctl CONTAINER_ID=5748929de54c
        -- Logs begin at Thu 2017-07-13 10:57:49 CST, end at Thu 2017-07-13 12:35:42 CST. --
        Jul 13 12:35:40 cnpvgl56588417 dockerd[3357]: 10.130.226.76 - - [13/Jul/2017:04:35:40 +0000] "GET / HTTP/1.1" 304 0 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebK
        Jul 13 12:35:41 cnpvgl56588417 dockerd[3357]: 10.130.226.76 - - [13/Jul/2017:04:35:41 +0000] "GET / HTTP/1.1" 304 0 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKvvvvvvvv
        Jul 13 12:35:41 cnpvgl56588417 dockerd[3357]: 10.130.226.76 - - [13/Jul/2017:04:35:41 +0000] "GET / HTTP/1.1" 304 0 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebK
        Jul 13 12:35:41 cnpvgl56588417 dockerd[3357]: 10.130.226.76 - - [13/Jul/2017:04:35:41 +0000] "GET / HTTP/1.1" 304 0 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebK
        ```
      - `"log-opts":  {"tag":"docker_{{.Name}}_{{.ID}}"}`: this will create container tag with docker_CONTAINER_NAME_CONTAINER_ID

      - add TLS cert after creating SSL keys.

      - enable docker engine metrics
         ```
        "metrics-addr" : "0.0.0.0:9323",
        "experimental" : true
         ```

3. journald configuration, which is located in `/etc/systemd/journald.conf`.
    ```
    [Journal]
    Storage=auto
    #Compress=yes
    #Seal=yes
    #SplitMode=uid
    #SyncIntervalSec=5m
    #RateLimitInterval=30s
    #RateLimitBurst=1000
    SystemMaxUse=20%
    #SystemKeepFree=
    #SystemMaxFileSize=
    #SystemMaxFiles=100
    #RuntimeMaxUse=20
    #RuntimeKeepFree=
    #RuntimeMaxFileSize=
    #RuntimeMaxFiles=100
    #MaxRetentionSec=
    #MaxFileSec=1month
    #ForwardToSyslog=yes
    #ForwardToKMsg=no
    #ForwardToConsole=no
    #ForwardToWall=yes
    #TTYPath=/dev/console
    #MaxLevelStore=debug
    #MaxLevelSyslog=debug
    #MaxLevelKMsg=notice
    #MaxLevelConsole=info
    #MaxLevelWall=emerg
    ```

    - Storage=auto：“auto”: The storage mode is like persistent — data will be written to disk under /var/log/journal/
    - SystemMaxuse: This parameter controls the maximum disk space the journal can consume when it’s persistent
    - **make sure the dir /var/log/journal exists**


4. create SSL keys for etcd, docker and kubernetes, details in [SSL](./SSL); . now we will create one bundle of 3 CA certs which can be used in the cluster, also docker and etcd have their individual CA certs.

    NOTE: we can also use TLS bootstraping for kubelet, thus we don't need to create certificates for each node when joining into the cluster, details steps in [TLS Booststraping](./TLS_Bootstrapping)

5. create [kubeconfig](./kubeconfig) for different components and roles, this is due to RBAC roles used. 

6. prepare [kubelet.service](./systemd/kubelet.service).


    - for the cert used in kubelet, we should  set its org and CN ` O=system:nodes/CN=system:node:<node-name>`, it is related with RBAC

    - the kubeconfig used in kubelet, since we have have configured [apiserver proxy](./applications/apiserver-proxy) via haproxy or nginx on each node, which listens on https://0.0.0.0:8443 and proxy all apiserver request to the real apiservers, hence the apiserver configure in kubeconfig can be set to `https://localhost:8443`

    - Create cni conf on the nodes running kubelet service, starting from v1.7.2, kubelet has an issue that when it starts it will check if the cni configure exists in /etc/cni/net.d. if not, it fails to start. so we need to create CNI conf before we start kubelet on each node and then install calico network.

    - now, many kubelet flags are moved to a config file, we need to create it first, and set it via `--config=/var/lib/kubelet/kubelet.config`:
    
    ```
    kind: KubeletConfiguration
    apiVersion: kubelet.config.k8s.io/v1beta1
    CgroupDriver: "systemd"
    ClusterDNS: ["192.168.0.10"]
    ClusterDomain: "cluster.local"
    StaticPodPath: "/var/lib/kubernetes/manifests"
    EvictionHard:
        memory.available": "300Mi"
        nodefs.available:  "10%"
    EvictionSoft:
        memory.available": "600Mi"
        nodefs.available:  "15%"
    SystemReserved: "cpu=200m,memory=10G,nodefs=10G"
    SystemReservedCgroup: "/system.slice"
    KubeReserved: "cpu=200m,memory=5G,nodefs=10G"
    KubeReservedCgroup: "/kubesvc.slice"
    EnforceNodeAllocatable: "system-reserved,kube-reserved,pod"
    ```

    details are list in the source code： https://github.com/kubernetes/kubernetes/blob/master/pkg/kubelet/apis/kubeletconfig/v1beta1/types.go

7. prepare the static pod manifests,[etcd.yaml](./manifests/etcd.yaml), [kube-apiserver.yaml](./manifests/kube-apiserver.yaml),[kube-controller-manager.yaml](./manifests/kube-controller-manager.yaml) , [kube-scheduler.yaml](kube-scheduler.yaml) and [apiserver-proxy](./applications/apiserver-proxy)

    ## Note:
    -  etcd add tls cert
    - for apiserver,   enable `Node` authorization and add `NodeRestriction` adminsion-control
    - controller add an additional parameter 
    `--use-service-account-credentials`, the details explanation, please refer to [link](https://kubernetes.io/docs/admin/authorization/rbac/#controller-roles). if don't add this parameter, we may encounter permission `DENY` issue.
  

8. get [kubernetes node binaries](https://dl.k8s.io//v1.10.0/kubernetes-node-linux-amd64.tar.gz), 

9. start kubernetes nodes via starting `kubelet.service`.

10. when started, we may got some errors show that `system:node:cnpvgl56588417 don't have permission to update node status ...., permission DENY....`. Here we need to update the rolebinding for this account, refer to [kube-node-binding](./RBAC/kube-node-binding.yaml)

11. install network plugin, two types of network plugins are taken into consideration. one is  [calico](./network/calico), here calico use etcd for storage, I prefer share etcd with k8s, so also need to configure the etcd keys in calico conf, the iother one is [cilium](./network/cilium).

    *if we need to append certs in the secret, just  base64 -w 0 ./ca.pem then add the result to the secret value if neccessary both in calico and cilium*

    - Calico

        0. install [calico cni conf](./network/calico/10-calico.conf) into  /etc/cni/net.d on each node
    
        1. create configmap to storate the etcd TLS certs and ca certs, describe in [calico](./network/calico/readme.md)

        2. modify [calico.yaml](./network/calico/calico.yaml)
        - calico-config

        ```
        etcd_endpoints: "https://192.168.59.201:2379,https://192.168.59.202:2379,https://192.168.59.203:2379"
        ```

        and 

        ```
        etcd_ca: "/calico-secrets/etcd-ca"
        etcd_cert: "/calico-secrets/etcd-cert"
        etcd_key: "/calico-secrets/etcd-key"
        ```
        - calico-node
        ```
         - name: CALICO_IPV4POOL_CIDR
           value: "192.188.0.0/16"

         and other domain related fileds.
        ```


        - remove the configmap for creating calico-etcd-secrets, since  we created it manually.
        - remove all entries about colico-cni-conf, and mount it from hostPath

        3. create role and rolebinding for calico via     [calico-rbac.yaml](./network/calico/calico-rbac.yaml)

        4. create calico via [calico.yaml](./network/calico/calico.yaml)

    - Cilium
        - before install this plugin, install [cilium cni conf](./network/cilium/10-cilium.conf) into  /etc/cni/net.d on each node

        - we will still consider using [cilium]   (https://github.com/cilium/cilium), it has many advanced   features, it will implement kube-proxy function, and use bpf to   replace iptables thus has higher performance, but now it lacks some functionality, such as NodePort, ingress,..etcd.

        full deployment of cilium, refer to [cilium deployment](./network/cilium).



12. install [kube-proxy](./addons/kube-proxy/kube-proxy.yaml) via daemonset, but before that created a configmap to store `kube-proxy.kubeconfig`, and then mount in the kube-proxy pods. or we can start it as a static pod, now kube-proxy can be running in ipvs mode which may be more performant than iptables. 


13. install [kube-dns](./addons/kube-dns/kube-dns.yaml), this file contains a configmap to store some addtional config of `upstreamNameservers`, and modify the DNS domains and DNS  service IP `clusterIP: 192.168.0.10`, also enable prometheus monitoring on service and exposes coresponding ports.
```
   prometheus.io/scrape: 'true'
   prometheus.io/port: '10055'`
```

14. install ingress controller, details in [ingress](./ingress)
    
    14.1 create customized tmplates, because we need to change the listen port to 8088

    14.2 customizde ingress by [ingress-customization.yaml](./ingress/ingress-customization.yaml), especially enable vts `enable-vts-status: "true"`

    14.3 enable tcp by [tcp-configmap.yaml](./ingress/tcp-configmap.yaml), try to expose influxdb endpoints, it is working. 

    14.4 modify the parameter via [nginx-ingress-controller.yaml](./ingress/nginx-ingress-controller.yaml)

    ```
    - /nginx-ingress-controller
    - --default-backend-service=$(POD_NAMESPACE)/default-http-backend
    - --configmap=$(POD_NAMESPACE)/ingress-customization
    - --tcp-services-configmap=$(POD_NAMESPACE)/tcp-configmap
    ```

    depoly multiple controllers, so I use daemonset to running multple instances.

15. create resource limits and quota, exampes refer to [ResourceLimitQuota](./ResourceLimitQuota), these limits and quotas are based on namespace scope.

16. Install kubernetes-dashboard, follow the guide in [dashboard deployment](./addons/kubernetes-dashboard).


17. configure storage

    17.1  [local storage provisioner](./storage/local-storage), now it doesn't support **Dynamic provisioning**, so we don't use it at this moment, consider it in future.
    17.2  [nfs provisioner](./storage/nfs-provisioner), here we deploy on nodes, not in of kubernetes, this makes the storage system more robust.

    17.3 [nfs client](./storage/nfs-client), if we already have setup nfs server, we can start a nfs-client to reference this nfs server, then provision the staorage to the cluster.

18. Install [Monitoring and Logging](./monitoring), 

    18.1 Totally we use influxdb as the overall storage backend, save logs from fluentbit, save prometheus metrics and heapster data.

    18.2 as for fluentbit, it reads logs from systemd-journald, as we have configured journald as the docker log-driver, hence install fluentbit as daemonset, read journal logs from shared directory /var/log/journal, after processing, finally save it to influxd. we deploy influxdb on nodes, not in kubernetes cluster.

    18.3 heapster inherently support to external storage influxdb 

    18.4 prometheus has alpha support to save data to remote storage via  remote_storage_adapter, now create prometheus alongside with a remote-storage-adapter container in a single pod. also use alertmanager to send out alerts. we deploy prometheus,alertmanager,node-exporter and remote-storage-adapter on nodes, not in kubernetes cluster.

    18.5 we can reload prometheus via `curl -X POST http(s)://{prometheus-host}:{prometheus-port}/-/reload` and reload altermanager via `curl -X POST http(s)://{alertmanager-host}:{alertmanager-port}/-/reload`.

    18.6 we can customize prometheus by creating different prometheus.yaml and alter-rules via  in-cluster configmap [prometheus-cm.yaml](./monitoring/In-Cluster/prometheus/prometheus-cm.yml) or out-cluster [prometheus.yml](./monitoring/Out-Cluster/prometheus/prometheus.yml)

    18.7 customize alertmanager by creating  in-cluster configmap [alertmanager-cm.yaml](./monitoring/In-Cluster/alertmanager/alertmanager-cm.yml) and [template](./monitoring/In-Cluster/alertmanagerdefault.tmpl) or out-cluster [altermanager.yml](./monitoring/Out-Cluster/alertmanager/altermanager.yml)

    18.8 visulization via in-cluster [grafana](./monitoring/In-Cluster/grafana) or out-cluster [grafana](./monitoring/Out-Cluster/grafana)  , we still need to customizing the dashboards

    18.9 deploying prometheus/altermanager/kibana both in and out of cluster is possible. 


19. Create default [ResourceLimt and Quota](./ResourceLimitQuota).

20. deploy multiple [applications](./applications) and [kubernetes addons](./addons)

    ## To enforce scheduler pods on master nodes, label the maste node as:
    ```
    kubectl label nodes 192.168.59.201 dedicated=master
    ```
    
21. define some [autoscaler](./Autoscaler) rules, details refer to [AutoScaler](https://github.com/kubernetes/autoscaler), there are four types of autoscaler
    - [Cluster Autoscaler](https://github.com/kubernetes/autoscaler/tree/master/cluster-autoscaler)
    - [Vertical Pod Autoscaler ](https://github.com/kubernetes/autoscaler/tree/master/vertical-pod-autoscaler)
    - [Addon Resizer](https://github.com/kubernetes/autoscaler/tree/master/addon-resizer)
    - [HPA (Horizontal Pod Autoscaler)](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)

22. [Network policy](./NetworkPolicy) is another considerations. kubernetes has [built-in networkpolicy](https://kubernetes.io/docs/concepts/services-networking/network-policies/) and also some third-parties also implement this via [CRD](https://kubernetes.io/docs/concepts/api-extension/custom-resources/), for example cilium or calico. 

24. [External loadbalancer](./LoadBalancer), if we don't deploy kubernetes cluster in cloud provider, we can't leverage loadbalancer service(Service objects with `spec.type=LoadBalancer`), so there is a project [metalLB](https://github.com/google/metallb), which can address this problem if we deploy it in bare metal environment. 

25. for HA deployment, we will deploy multiple master nodes, so we will have proxy to mulitple apiserver, detail setup of [apiserver proxy](./applications/apiserver-proxy)


26. [Service Mesh](./ServiceMesh) is a dedicated infrastructure layer for making service-to-service communication safe, fast, and reliable. If you’re building a cloud native application, you need a service mesh! now we have two candidates, [Istio](./ServiceMesh/istio) and [conduit](./ServiceMesh/conduit).

