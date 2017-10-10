
1. CNI configuration 
```
mkdir -p /etc/cni/net.d
echo '{
    "name": "cilium",
    "type": "cilium-cni",
    "mtu": 1450
}' > /etc/cni/net.d/10-cilium.conf

```

2. install CNI plugin

```
sudo mkdir -p /opt/cni
wget https://storage.googleapis.com/kubernetes-release/network-plugins/cni-0799f5732f2a11b329d9e3d51b9c8f2e3759f2ff.tar.gz
sudo tar -xvf cni-0799f5732f2a11b329d9e3d51b9c8f2e3759f2ff.tar.gz -C /opt/cni
rm cni-0799f5732f2a11b329d9e3d51b9c8f2e3759f2ff.tar.gz
```