#description

This Method deploy the kubernetes main components(apiserver,controller-manager,scheduler,kubelet,kube-prox) via systemd service,other components(kubeDNS aks skydns, calico netork plugin, dashboard) with pod.

This can be a preparation for the real production, after this we can deploy all components via pod through kubelet service. 
