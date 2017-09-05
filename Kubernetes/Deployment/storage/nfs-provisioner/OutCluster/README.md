**Notes about running nfs-provisioner outside of kubernetes**
1. make sure `rpcbind.service`,`nfs-idmapd.service`,`nfs-server.service` are running, configure nfs-server to export `/export *(rw,no_root_squash)`
2. still need to create serviceaccount for nfs-provisioner, and give it proper permissions, export the token used in the kubeconfig file
3. build and copy the nfs-provisioner binary to server
4. start nfs-provisioner via `systemctl start nfs-provisioner`
