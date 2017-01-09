Introduction
--
 
   From very beginning, I plan to build a kubernetes demo, the question is in what way we create it. there we have at least two methods to build kubernetes cluster from scratch, one is to dockerize all components, and the other one is to use traditional way of init scripts aka systemd services. the biggest problem is  that when I started, I realized that I didn't even know what parameters I can use, what authentication strategy I should use, how to create the certificate when I choose  certificate method , ...  and so on. I am totally confused and don't have clear vision. 

   In the two weeks, I tried both methods, searched tremendous materials through google, this made me even frustrating and exhousting but got very little progress, but I did have some understanding. At last I chose to use kubeadm to start a two-node demo to see what does it configure to make a cluster, I analyzed the configuration and paramters, and used analogous setting to build my own systemd based cluster, through still had some trouble but at last I chieved. 

   This is a big step of thinking how to make a sophisticated system, "copy" is not a bad idea, I chose a mirror to make me understand in-depth.  I summarized all the steps and problems during this procedure. finally I will also try to build such cluster in dockerized way through pod/kubelet.
    
   There are at least three docker orchestrations, I will try them one by one to do a whole test. 

   * [Kubernetes](./Kubernetes)
