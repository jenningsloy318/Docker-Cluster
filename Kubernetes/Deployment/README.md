
# Officially deploy a production kubernetes cluster #

# prequisistes #

  1. check the docker and other componenet requirements before deploying the cluster, visit the [Kubernetes CHANGELOG](https://github.com/kubernetes/kubernetes/blob/master/CHANGELOG.md), and find the section `External Dependency Version Information`.
  2. build docker images with `docker build --rm --force-rm  --no-cache --tag XXX . `
  3. configure systemd to enable more cgroup controllers, since kubelet (https://github.com/kubernetes/kubernetes/blob/release-1.7/pkg/kubelet/cm/cgroup_manager_linux.go, line 236) will check if `"cpu", "cpuacct", "cpuset", "memory", "hugetlb", "systemd"`  exist in the cgroup hierarchy. edit `/etc/systemd/system.conf`:
    
  ```
  JoinControllers=cpu,cpuacct,cpuset,net_cls,net_prio,hugetlb,memory
  ```
    This will resove the error `failed to run Kubelet: invalid configuration: cgroup-root "/container.slice/" doesn't exist:`, when specified `--cgroup-root=/container.slice/` in kubelet.service.
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
    - for deb from [http://apt.dockerproject.org](http://apt.dockerproject.org/repo/pool/main/d/docker-engine/)
    - for rpm from [http://yum.dockerproject.org](http://yum.dockerproject.org)

    2.2 install docker-engine 

      ```
      # dpkg -i docker-engine_1.12.6-0~ubuntu-xenial_amd64.deb 
      # apt install -f 
      ```
      or

      ```
      #yum install http://yum.dockerproject.org/repo/main/centos/7/Packages/docker-engine-1.12.6-1.el7.centos.x86_64.rpm
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


4. create SSL keys for etcd, docker and kubernetes, details in [SSL](./SSL); here etcd and docker certs can share same certs, so create once and used in both etcd and docker. for k8s, for enabled RBAC, thus for each kubelet cert with its individual cert. 

5. create [kubeconfig](./kubeconfig) for different components and roles, this is due to RBAC roles used. 

6. prepare [kubelet.service](./systemd/kubelet.service).

    -  add `Slice=kubesvc.slice` into the `[service]` section, this will place kubelet service in kubesvc.slice.

    - `--cgrout-root=/container.slice`:  this will place all pods under `/container.slice/kubepods.slice`

    - `--kube-reserved=cpu=2,memory=4Gi --kube-reserved-cgroup=/kubesvc.slice   --system-reserved=cpu=2,memory=4Gi --system-reserved-cgroup=/system.slice`:  these parameter will limit the kube process and other process resouce.

    - `--enforce-node-allocatable=pods,system-reserved,kube-reserved`: this will garentee that pod,system processes and kubelet/rkt process are all existing in the system, prevent any crashes due to lack of the resources.


7. prepare the static pod manifests,[etcd.yaml](./manifests/etcd.yaml), [kube-apiserver.yaml](./manifests/kube-apiserver.yaml),[kube-controller-manager.yaml](./manifests/kube-controller-manager.yaml) and [kube-scheduler.yaml](kube-scheduler.yaml)

    ## Note:
    -  etcd add tls cert
    - for apiserver,   enable `Node` authorization and add `NodeRestriction` adminsion-control
    - controller add an additional parameter 
    `--use-service-account-credentials`, the details explanation, please refer to [link](https://kubernetes.io/docs/admin/authorization/rbac/#controller-roles). if don't add this parameter, we may encounter permission `DENY` issue.
  

8. get [kubernetes node binaries](https://dl.k8s.io/v1.7.2/kubernetes-node-linux-amd64.tar.gz), this is v1.7.2, now this version of kubelet has an issue that when it starts it will check if the cni configure exists in /etc/cni/net.d. if not, it fails to start. I had to use v1.5.x to start kubelet, and then install calico network, after that reinstall v.17.x version of kubelet.

9. start kubernetes cluster via starting `kubelet.service`.

10. when started, we may got some errors show that `system:node:cnpvgl56588417 don't have permission to update node status ...., permission DENY....`. Here we need to update the rolebinding for this account, refer to [kube-node-binding](./RBAC/kube-node-binding.yaml)

11. install network plugin, here I use [calico](./network/calico), here calico use etcd for storage, I prefer share etcd with k8s, so also need to configure the etcd keys in calico conf.

    11.1 create configmap to storate the etcd TLS certs and ca certs, describe in [calico](./network/calico/readme.md)

    11.2 modify [calico.yaml](./network/calico/calico.yaml)
    - calico-config

    ```
    etcd_endpoints: "https://10.58.137.243:2379"
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
    

    - remove the configmap for creating calico-etcd-secrets, since we created it manually.

    11.3 create role and rolebinding for calico via [calico-rbac.yaml](./network/calico/calico-rbac.yaml)

    11.4 create calico via [calico.yaml](./network/calico/calico.yaml)

12. install [kube-proxy](./addons/kube-proxy/kube-proxy.yaml) via daemonset, but before that created a configmap to store `kube-proxy.kubeconfig`, and then mount in the kube-proxy pods.

13. install [kube-dns](./addons/kube-dns/kube-dns.yaml), this file contains a configmap to store some addtional config of `upstreamNameservers`, and modify the DNS domains and DNS  service IP `clusterIP: 192.168.0.10`, also enable prometheus monitoring on service and exposes coresponding ports.
```
   prometheus.io/scrape: 'true'
   prometheus.io/port: '10055'`
```

14. install ingress controller
    
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

16. Install kubernetes-dashboard.

    16.1 create a clusterrole [cluster-view](./RBAC/cluster-view.yaml) which only have read access to cluster resources.
    
    16.2 create clusterrolebinding via [kubernetes-dashboard-rbac.yaml](./addons/kubernetes-dashboard/kubernetes-dashboard-rbac.yaml).

    16.3 install [kubernetes-dashboard](./addons/kubernetes-dashboard/kubernetes-dashboard.yaml).

    16.4 create [dashboard ingress](./addons/kubernetes-dashboard/kubernetes-dashboard-ingress).



17. configure storage

    17.1  [local storage provisioner](./storage/local-storage)
    17.2  [nfs provisioner](./storage/nfs-provisioner)

18. Install [Monitoring and Logging](./monitoring)

    18.1 Totally we use influxdb as the overall storage backend, save logs from fluentbit, save prometheus metrics and heapster data.

    18.2 as for fluentbit, it reads logs from systemd-journald, as we have configured journald as the docker log-driver, hence install fluentbit as daemonset, read journal logs from shared directory /var/log/journal, after processing, finally save it to influxd.

    18.3 heapster inherently support to external storage influxdb 

    18.4 prometheus has alpha support to save data to remote storage via  remote_storage_adapter, now create prometheus alongside with a remote-storage-adapter container in a single pod. also use alertmanager to send out alerts. 

    18.5 we can reload prometheus via `curl -X POST http(s)://{prometheus-host}:{prometheus-port}/-/reloador` and reload altermanager via `curl -X POST http(s)://{alertmanager-host}:{alertmanager-port}/-/reload`.

    18.6 we can customize prometheus by creating different prometheus.yaml and alter-rules via [prometheus-cm.yaml](./monitoring/prometheus/prometheus-cm.yml) 

    18.7 customize alertmanager by creating [alertmanager-cm.yaml](./monitoring/prometheus/alertmanager-cm.yml) and [template](./monitoring/prometheus/default.tmpl)

    18.8 visulization via [grafana](./monitoring/grafana), we still need to customizing the dashboards