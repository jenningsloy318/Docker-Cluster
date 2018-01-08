#!/bin/bash
KUBE_ROOT=$(pwd) 

####check the input 
if [ $# != 1 ] ; then
     echo "USAGE: $0 node-type"
     echo " e.g.: $0 master"
     echo "Type can be master or node"
     exit 1;
fi

if ! which systemctl ; then 
    echo "Unsupported Linux platform, you should upgrade you OS  based on systemd init."
    exit 1;
fi

NODE_TYPE="$1"

source ${KUBE_ROOT}/ko8s.env 


####check docker  installation

if  which docker >/dev/null ; then 
	echo "docker is installed"
else 
	${KUBE_ROOT}/k8s_install_docker_engine.sh
fi
####start docker service
if ps -ef|grep docker |grep -v grep > /dev/null  ; then 

	echo "Docker engine is running."
else
	systemctl start docker
fi

####get etcd and kubernetes binaries 
echo "downloading kubernetes and etcd binaries"

if [ ${NODE_TYPE} == "master" ]; then
    sh ${KUBE_ROOT}/k8s_get_server_bin.sh 
    sh ${KUBE_ROOT}/k8s_get_client_bin.sh 
    cp ${KUBE_ROOT}/server/* /usr/bin
    cp ${KUBE_ROOT}/client/* /usr/bin
elif [ ${NODE_TYPE} == "node" ]; then
    sh ${KUBE_ROOT}/k8s_get_client_bin.sh 
    cp ${KUBE_ROOT}/client/* /usr/bin
fi
