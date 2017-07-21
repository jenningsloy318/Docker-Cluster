#!/usr/bin/env bash
create_self_sign_apiserver_cert(){
    mkdir -p  ${KUBE_ROOT}/ssl/self_sign  && cd ${KUBE_ROOT}/ssl/self_sign
    echo "create CA priviate key"
    openssl genrsa -out ca-key.pem 2048
    
    echo "extract CA public key "
    openssl rsa -in ca-key.pem -pubout -out ca-pub.pem

    echo "create CA self-signed cert"
    openssl req -x509 -new -nodes -key ca-key.pem -days 10000 -out ca.pem -subj "/CN=${MASTER}"

    echo "create apiserver priviate key"
    openssl genrsa -out apiserver-key.pem 2048

    echo "extract apiserver public key"
    openssl rsa -in apiserver-key.pem -pubout -out apiserver-pub.pem

    echo "create the openssl-apiserver.conf, which is used to create apiserver cert request"

    cat  << EOF > openssl-apiserver.conf
	[req]
    req_extensions = v3_req
    distinguished_name = req_distinguished_name
    [req_distinguished_name]
    [ v3_req ]
    basicConstraints = CA:FALSE
    keyUsage = nonRepudiation, digitalSignature, keyEncipherment
    subjectAltName = @alt_names
    [alt_names]
    DNS.1 = kubernetes
    DNS.2 = kubernetes.default
    DNS.3 = kubernetes.default.svc
    DNS.4 = kubernetes.default.svc.cluster.local
    IP.1 = 10.96.0.1
    IP.2 = ${MASTER}
	EOF

    echo "create apiserver sign request" 
	openssl req -new -key apiserver-key.pem -out apiserver.csr -subj "/CN=${MASTER}" -config openssl-apiserver.conf

    echo "create apiserver self-sign cert" 
    openssl x509 -req -in apiserver.csr -CA ca.pem -CAkey ca-key.pem -CAcreateserial -out apiserver.pem -days 365 -extensions v3_req -extfile openssl-apiserver.conf
    
    echo "copy the ssl keys to /etc/kubernetes/pki"
    mkdir -p /etc/kubernetes/pki 
    cp ${KUBE_ROOT}/ssl/self_sign/*.pem /etc/kubernetes/pki
}

create_k8s_server_conf() {
    kubectl config set-cluster kubernetes --certificate-authority=/etc/kubernetes/pki/ca.pem --embed-certs=true --server=${APISERVER} --kubeconfig=/etc/kubernetes/admin.conf
    kubectl config set-credentials kubelet --client-certificate=/etc/kubernetes/pki/apiserver.pem --client-key=/etc/kubernetes/pki/apiserver-key.pem --embed-certs=true  --kubeconfig=/etc/kubernetes/admin.conf
    kubectl config set-context kubelet@kubernetes --cluster=kubernetes --user=kubelet  --kubeconfig=/etc/kubernetes/admin.conf
    kubectl config use-context kubelet@kubernetes  --kubeconfig=/etc/kubernetes/admin.conf
}

create_basic_auth_file(){
    echo  "kubernetes,admin,admin" > /etc/kubernetes/pki/basic-auth.csv
}
create_token_auth_file(){
    echo "generate token" 
    TOKEN=$(dd if=/dev/urandom bs=128 count=1 2>/dev/null | base64 | tr -d "=+/" | dd bs=32 count=1 2>/dev/null)
    echo  "${TOKEN},admin,admin" >/etc/kubernetes/pki/tokens.csv
}



echo "create APISERVER server cert"
create_self_sign_apiserver_cert

echo "create kubelet.conf used for kublelt and kube-proxy on master" 
create_k8s_server_conf

echo "create basic and token auth file used in apiserver service" 
create_basic_auth_file
create_token_auth_file
