#!/usr/bin/env bash
create_self_sign_apiserver_cert(){
    echo "create CA priviate key"
    openssl genrsa -out ca-key.pem 2048
    
    echo "extract CA public key "
    openssl rsa -in ca-key.pem -pubout -out ca-pub.pem

    echo "create CA self-signed cert"
    openssl req -x509 -new -nodes -key ca-key.pem -days 10000 -out ca.pem -subj "/CN=k8s-ca"

    echo "create apiserver priviate key"
    openssl genrsa -out apiserver-key.pem 2048

    echo "extract apiserver public key"
    openssl rsa -in apiserver-key.pem -pubout -out apiserver-pub.pem


    echo "create apiserver sign request" 
	openssl req -new -key apiserver-key.pem -out apiserver.csr -subj "/CN=k8s-master" -config $1

    echo "create apiserver self-sign cert" 
    openssl x509 -req -in apiserver.csr -CA ca.pem -CAkey ca-key.pem -CAcreateserial -out apiserver.pem -days 365 -extensions v3_req -extfile $1
    
}


create_basic_auth_file(){
    echo  "kubernetes,admin,admin" > basic_auth.csv
}

create_token_auth_file(){
    echo "generate token" 
    TOKEN=$(dd if=/dev/urandom bs=128 count=1 2>/dev/null | base64 | tr -d "=+/" | dd bs=32 count=1 2>/dev/null)
    echo  "${TOKEN},admin,admin" > tokens.csv
}


echo "create APISERVER server cert"
create_self_sign_apiserver_cert $1


echo "create basic and token auth file used in apiserver service" 
create_basic_auth_file
#create_token_auth_file
