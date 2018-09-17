- [metalLB](https://github.com/google/metallb)

----
 
Manual 

Using MetalLB as Kubernetes load balancer with Ubiquiti EdgeRouter
I’m running Kubernetes in my five-board Picocluster. I read Miek Gieben’s article about MetalLB and got intrigued — maybe I could also have a load balancing setup for my cluster without too much hassle? I have a Ubiquiti EdgeRouter Lite, which is a pretty common and capable router for small networks, so I decided to try out BGP load balancing. The MetalLB BGP tutorial explained how MetalLB part inside the cluster has to be configured, but BGP requires both ends to have matching configuration. I couldn’t find any documentation about how MetalLB and the EdgeRouter can be made to work together, so I decided to write down my own experiences.


BGP load balancing is conceptually pretty simple, even though BGP itself is a complex protocol. MetalLB uses only a subset of BGP features. You can read the details about how MetalLB uses BGP from it’s own documentation. The idea is this: the router and the Kubernetes worker nodes are configured to be neighbors. Then, when a service of type=LoadBalancer is started, MetalLB assigns it a service IP from an address pool it controls. MetalLB tells the router that it can route traffic to the service IP via a set of nodes on which the pod runs. Since all the nodes carry the same routing cost, the router selects the route by hashing the network connection details (such as source and destination IPs and the network protocol). This means that all packets belonging to a certain connection are routed to the same node, which is exactly what we need.

The network setup I have is pretty straightforward. The router is at 192.168.1.1. A switch sits between the router and the Kubernetes nodes. The Kubernetes master node is at 192.168.1.200, and the four worker nodes are at 192.168.1.201–192.168.1.204. The service address range is specified to be 192.168.1.224/27 (192.168.1.224–192.168.1.255). MetalLB gives out the addresses from this set.

![network-setup](./network-setup.png)


MetalLB deployment to Kubernetes starts a control pod and as many speaker pods as there are worker nodes. MetalLB installation is simple and well explained in the documentation, so I’ll focus on the configuration.
In order to set up MetalLB, I applied this ConfigMap:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  namespace: metallb-system
  name: config
data:
  config: |
    peers:
    - peer-address: 192.168.1.1
      peer-asn: 64512
      my-asn: 64512
    address-pools:
    - name: default
      protocol: bgp
      addresses:
      - 192.168.1.224/27
```
The **peer-address** field has the address of the router. I chose both **peer-asn** (the router) and **my-asn** (the cluster) number to be the same, indicating that both ends of the route are in the same Autonomous System. The number 64512 is the first “private” ASN, meaning it doesn’t belong to any real AS — it can be compared to a private IP address. The default address pool has the Service addresses that MetalLB can give out as the addresses field.

To configure the EdgeRouter, one has to ssh into the device or open the CLI window from the GUI, because there is no BGP support in the GUI. Then the following commands set up BGP configuration and start up the BGP service in the router:

```sh
configure
set protocols bgp 64512 parameters router-id 192.168.1.1
set protocols bgp 64512 neighbor 192.168.1.201 remote-as 64512
set protocols bgp 64512 neighbor 192.168.1.202 remote-as 64512
set protocols bgp 64512 neighbor 192.168.1.203 remote-as 64512
set protocols bgp 64512 neighbor 192.168.1.204 remote-as 64512
set protocols bgp 64512 maximum-paths ibgp 32
commit
save
exit
```
The **configure**, **commit**, **save**, and **exit** commands are just the way how the EdgeRouter’s configuration mode is entered and the changes applied. The first real command sets the router-id to 192.168.1.1. The following four commands set each of the Kubernetes worker nodes to be a neighbor to the router. Note that the same ASN is used. The **maximum-paths** value tells how many potential BGP routing targets there can be. The number should be at least as big as the maximum number of replicas your load-balancing applications will have.

After the configuration is applied the current BGP neighbors can be listed with this command:
```sh
show ip bgp neighbors
```
If everything went well, something like this is printed out for each node:
```sh
BGP neighbor is 192.168.1.201, remote AS 64512, local AS 64512, internal link
 BGP version 4, remote router ID 192.168.1.201
 BGP state = Established, up for 00:38:08
 Last read 00:38:08, hold time is 90, keepalive interval is 30 seconds
 Neighbor capabilities:
 Route refresh: advertised
 4-Octet ASN Capability: advertised and received
 Address family IPv4 Unicast: advertised and received
 Address family IPv6 Unicast: received
 Received 1790 messages, 0 notifications, 0 in queue
 Sent 1779 messages, 0 notifications, 0 in queue
 Route refresh request: received 0, sent 0
 Minimum time between advertisement runs is 5 seconds
 For address family: IPv4 Unicast
 BGP table version 35, neighbor version 35
 Index 2, Offset 0, Mask 0x4
 Community attribute sent to this neighbor (both)
 1 accepted prefixes
 0 announced prefixes
 Connections established 5; dropped 4
Local host: 192.168.1.1, Local port: 179
Foreign host: 192.168.1.201, Foreign port: 44153
Nexthop: 192.168.1.1
Nexthop global: xxxx:xxxx:xxx:xxxx::x
Nexthop local: fe80::f29f:c2ff:fe12:428
BGP connection: non shared network
```

At this point the load balancing is ready to be used. A service uses load balancing when type=LoadBalancer is added to the Kubernetes service description. The External-IP address from kubectl get services is then to access the service. I also add externalTrafficPolicy=Local to the service descriptions to make MetalLB advertise routes only to those nodes which are actually running the pods belonging to the service. If you do this, you can check the routes with this command:

```sh
show ip route bgp
```
For me, it returns the following table showing that I have four services using load balancing:

```sh
IP Route Table for VRF “default”
B *> 192.168.1.224/32 [200/0] via 192.168.1.205, eth1, 00:00:04
B *> 192.168.1.225/32 [200/0] via 192.168.1.203, eth1, 00:08:04
  *> [200/0] via 192.168.1.201, eth1, 00:08:04
B *> 192.168.1.226/32 [200/0] via 192.168.1.205, eth1, 00:08:04
  *> [200/0] via 192.168.1.202, eth1, 00:08:04
  *> [200/0] via 192.168.1.201, eth1, 00:08:04
B *> 192.168.1.227/32 [200/0] via 192.168.1.205, eth1, 00:00:04
Gateway of last resort is not set
```

The service at service IP 192.168.1.225 is replicated on two nodes (192.168.1.203 and 192.168.1.201) and the service at 192.168.1.226 is replicated on three nodes (192.168.1.205, 192.168.1.202, and 192.168.1.201). If you are running a http service in the pods, you can try that everything works by accessing the service IP directly from the EdgeRouter command line using curl or similar tool.

The last caveat is this: because the router handles the load balancing to the service IP addresses, you can’t access the service IP addresses from the same LAN segment in which the cluster is! The traffic must go through the router. Luckily, the EdgeRouter Lite has three configurable ethernet ports. I use eth0 for WAN, eth1 for the Kubernetes cluster, and eth2 for the “normal LAN”. This means that I can access the cluster from computers connected to eth2 using the service IPs. Of course, if you set up port forwarding in the router, you can access the service IPs also from WAN and enjoy load balancing for your application.

URL: https://medium.com/@ipuustin/using-metallb-as-kubernetes-load-balancer-with-ubiquiti-edgerouter-7ff680e9dca3