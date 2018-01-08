#!/usr/bin/env bash
    GIT_REPO_URL="git@github.com:jenningsloy318/Docker-Cluster.git"
    git clone ${GIT_REPO_URL}
    
    echo "Install k8s services"
    
    cp Kubernetes/Deployment/systemd/init/{kubelet.service,kube-proxy.service} /lib/systemd/system/ 
    
    echo "enable k8s services"
    cd /lib/systemd/system/ && systemctl daemon-reload && (for svc in `ls kube*.service` ; do  systemctl start $svc;done)
