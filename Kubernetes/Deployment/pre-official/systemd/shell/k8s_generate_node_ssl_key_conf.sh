#!/usr/bin/env bash
create_self_sign_node_cert(){
    echo "sync CA cert  from master"
    mkdir -p ${KUBE_ROOT}/ssl/self_sign/ && cd  ${KUBE_ROOT}/ssl/self_sign/ && rsync -av ${MASTER}:/etc/kubernetes/pki/ca.*  ${KUBE_ROOT}/ssl/self_sign/

    echo "create openssl-node.conf"
    cat << EOF > openssl-node.conf

	 [req]
	 req_extensions = v3_req
	 distinguished_name = req_distinguished_name
	 [req_distinguished_name]
	 [ v3_req ]
	 basicConstraints = CA:FALSE
	 keyUsage = nonRepudiation, digitalSignature, keyEncipherment
	 subjectAltName = @alt_names
	 [alt_names]
	 IP.1 = ${LOCAL_ADDR}
	
	echo "create node priviate key"
	openssl genrsa -out node-key.pem 2048
	
    echo "extract node public key"
    openssl rsa -in node-key.pem -pubout -out node-pub.pem

    echo "create sign request"
    openssl req -new -key node-key.pem -out node.csr -subj "/CN=${LOCAL_ADDR}" -config openssl-node.cnf

    echo "create node self-signed cert"
    openssl x509 -req -in node.csr -CA ca.pem -CAkey ca-key.pem -CAcreateserial -out node.pem -days 365 -extensions v3_req -extfile openssl-node.cnf

    echo "copy cert to /etc/kubernetes/pki"
    mkdir -p /etc/kubernetes/pki && cp  ${KUBE_ROOT}/ssl/self_sign/*.pem /etc/kubernetes/pki
}


create_k8s_node_conf() {
    kubectl config set-cluster kubernetes --certificate-authority=/etc/kubernetes/pki/ca.pem --embed-certs=true --server=${APISERVER} --kubeconfig=/etc/kubernetes/kubelet.conf
    kubectl config set-credentials kubelet --client-certificate=/etc/kubernetes/pki/node.pem --client-key=/etc/kubernetes/pki/node-key.pem --embed-certs=true  --kubeconfig=/etc/kubernetes/kubelet.conf
    kubectl config set-context admin@kubernetes --cluster=kubernetes --user=kubelet  --kubeconfig=/etc/kubernetes/kubelet.conf
}




echo "create node cert"
create_self_sign_node_cert


echo "create kubelet.conf used for kubelet and kube-proxy on node"
create_k8s_node_conf
