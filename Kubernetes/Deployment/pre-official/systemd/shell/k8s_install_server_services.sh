#!/bin/bash
    GIT_REPO_URL="git@github.com:jenningsloy318/Docker-Cluster.git"
    git clone ${GIT_REPO_URL}
    
    ####Install etcd and kubernetes services
    echo "Install etcd service"
    echo "copying etcd.service to /lib/systemd/system/"
    cp Kubernetes/Deployment/systemd/init/etcd.service /lib/systemd/system/
    if [ -d ! /etc/etcd ]; then 
        mkdir /etc/etcd
    fi
    
    echo "You can customize etcd conf before deploy it to /etc/etcd "
    echo "copying Kubernetes/Deployment/systemd/conf/etcd.conf to /etc/etcd"
    cp Kubernetes/Deployment/systemd/conf/etcd.conf /etc/etcd
    
    echo "enable and start etcd service"
    systemctl daemon-reload && systemctl start etcd
    
    echo "Install k8s services"
    
    echo "modify service files to according the master IP address"
    
    echo "modifying the apiserver IP address in kube-apiservice.service file "
    sed -i -r  "/ExecStart/s/advertise-address=([0-9]{1,3}\.){3}[0-9]{1,3}/advertise-address={MASTER}/g" Kubernetes/Deployment/systemd/init/kube-apiserver.service
    
    echo "You can still change the service cluster ip range in kube-apiserver file  and pod cluster ip cidr in kube-proxy.service/callico.yaml file"
    echo "copying k8s services to /libe/systemd/system" 
    cp Kubernetes/Deployment/systemd/init/kube*.service /lib/systemd/system/ 
    
    echo "enable k8s services"
    cd /lib/systemd/system/ && systemctl daemon-reload && (for svc in `ls kube*.service` ; do  systemctl start $svc;done)
