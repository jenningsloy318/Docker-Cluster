
# Officially deploy a production kubernetes cluster #

# prequisistes #

  1. check the docker and other componenet requirements before deploying the cluster, visit the [Kubernetes CHANGELOG](https://github.com/kubernetes/kubernetes/blob/master/CHANGELOG.md), and find the section `External Dependency Version Information`.

# Deployment #
1. create cgroup slice to accommodate docker containers and pods, here created a slice nemed [container.slice](./systemd/container.slice) 

    ```
    [Unit]
    Description=Limited resources Slice
    DefaultDependencies=no
    Before=slices.target
    
    [Slice]
    MemoryLimit=48G
   ```
    
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
      - slice into the `[service]` section, 
      - add HTTP_PROXY / HTTPS_PROXY Environment, 
      - since we have moved all docker conf to `/etc/docker/daemon.json`, then modify `ExecStart` to `ExecStart=/usr/bin/dockerd`

    2.4 configure docker via [daemon.json](./Docker/daemon.json).serveral things need to mention.
        
      - `cgroup-parent: container.slice` which means that all container will under  `/container.slice/` 
      - `cgroup driver`: systemd
        ```
        #systemd-cgls
        Control group /:
        -.slice
        ├─container.slice
        │ ├─docker
        │ │ └─5748929de54c59338de0f75dcedb736e5635edc42979fd3ff4e2da2de7fc1c2a
        │ │   ├─3560 nginx: master process nginx -g daemon off
        │ │   └─3583 nginx: worker proces
        │ └─docker.service
        │   ├─3357 /usr/bin/dockerd
        │   ├─3371 docker-containerd -l unix:///var/run/docker/libcontainerd/docker-containerd.sock --shim docker-containerd-shim --metrics-interval=0 --start-timeout 2m --state-di
        │   ├─3524 /usr/bin/docker-proxy -proto tcp -host-ip 0.0.0.0 -host-port 8080 -container-ip 172.17.0.2 -container-port 80
        │   └─3540 docker-containerd-shim 5748929de54c59338de0f75dcedb736e5635edc42979fd3ff4e2da2de7fc1c2a /var/run/docker/libcontainerd/5748929de54c59338de0f75dcedb736e5635edc4297
        ```
      - `hosts: ["tcp://0.0.0.0:2375","unix:///var/run/docker.sock"]`, which makes it not only listen to unix socket, but also listen on tcp socket.

      - `log-driver": "journald"`: since we use systemd as init system, we can also use `system-journald` for docker log driver. leveraging journald make all containers logs will be aggreated and sent to journald daemon, thus it is easy for log rotation and other operations, so we don't deal with logs in individual container. In addition to the text of the log message itself, the journald log driver stores the following metadata in the journal with each message:

        Field	|Description
        --------|---------
        CONTAINER_ID|	The container ID truncated to 12 characters.
        CONTAINER_ID_FULL|	The full 64-character container ID.
        CONTAINER_NAME|	The container name at the time it was started. If you use docker rename to rename a container, the new name is not reflected in the journal entries.
        CONTAINER_TAG	|The container tag (log tag option documentation).
        CONTAINER_PARTIAL_MESSAGE|	A field that flags log integrity. Improve logging of long log lines.

      with log driver, we can view logs in two methods
      
      * docker logs CONTAINER_ID/CONTAINER_NAME
        ```
        # docker logs 5748929de54c
        10.130.226.76 - - [13/Jul/2017:04:35:40 +0000] "GET / HTTP/1.1" 304 0 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36" "-"
        10.130.226.76 - - [13/Jul/2017:04:35:41 +0000] "GET / HTTP/1.1" 304 0 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36" "-"
        10.130.226.76 - - [13/Jul/2017:04:35:41 +0000] "GET / HTTP/1.1" 304 0 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36" "-"
        10.130.226.76 - - [13/Jul/2017:04:35:41 +0000] "GET / HTTP/1.1" 304 0 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36" "-"
        ```

      * journalctl CONTAINER_ID=xxx or CONTAINER_NAME=xxx
        ```
        journalctl CONTAINER_ID=5748929de54c
        -- Logs begin at Thu 2017-07-13 10:57:49 CST, end at Thu 2017-07-13 12:35:42 CST. --
        Jul 13 12:35:40 cnpvgl56588417 dockerd[3357]: 10.130.226.76 - - [13/Jul/2017:04:35:40 +0000] "GET / HTTP/1.1" 304 0 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebK
        Jul 13 12:35:41 cnpvgl56588417 dockerd[3357]: 10.130.226.76 - - [13/Jul/2017:04:35:41 +0000] "GET / HTTP/1.1" 304 0 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebK
        Jul 13 12:35:41 cnpvgl56588417 dockerd[3357]: 10.130.226.76 - - [13/Jul/2017:04:35:41 +0000] "GET / HTTP/1.1" 304 0 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebK
        Jul 13 12:35:41 cnpvgl56588417 dockerd[3357]: 10.130.226.76 - - [13/Jul/2017:04:35:41 +0000] "GET / HTTP/1.1" 304 0 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebK
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


