#!/usr/bin/env bash
####Install docker-engine
DOCKER_RELEASE=1.13.0
DOCKER_TAR=docker-${DOCKER_RELEASE}.tgz
DOCKER_DOWNLOAD_URL_PREFIX="${DOCKER_RELEASE_URL:-https://get.docker.com/builds/Linux/x86_64}"
DOCKER_DOWNLOAD_URL="${DOCKER_DOWNLOAD_URL_PREFIX}/${DOCKER_TAR}"


install_docker_engine() {
	echo "Downloading docker binary"
	curl -SL ${DOCKER_DOWNLOAD_URL} -o ${KUBE_ROOT}/${DOCKER_TAR}
	echo "uncomressing the tar package to /usr/bin"
	tar xvf ${KUBE_ROOT}/${DOCKER_TAR} --exclude="*completion*"   --strip-components 1 -C /usr/bin
	echo "Creating systemd service file"
    if [ -d /data/docker ] ; then 
        mkdir -p /data/docker 
    fi

	curl -SL 'https://raw.githubusercontent.com/jenningsloy318/Docker-Cluster/master/Kubernetes/Deployment/systemd/init/docker.service' -o /lib/systemd/system/docker.service
	echo "enable docker service"
 	systemctl daemon-reload && systemctl enable docker
}

