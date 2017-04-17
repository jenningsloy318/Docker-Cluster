
Two methods to deploy k8s cluster.

1. Running the k8s in [systemd](./systemd) services.
2. Start k8s master service in [pod](./Containerized) which is boot by kubelet.service.
3. For RBAC, if enabled, each component should have its individual certification and kubeconfig to identify itself. details RABC roles and binding refer to [Using RBAC Authorization](https://kubernetes.io/docs/admin/authorization/rbac)
