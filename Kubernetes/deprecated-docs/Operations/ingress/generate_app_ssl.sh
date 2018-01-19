#!/bin/bash

echo "Generating priviate key"
openssl genrsa -out app-key.pem 2048


echo "Create sign request for  it"
openssl req -new -key app-key.pem -out app.csr  -subj "/CN=kube-master.example.com" -config openssl.conf


echo "Go to https://getcerts.wdf.global.corp.lmy/pgwy/request/lmynetca_base64.html to get your application signed"



