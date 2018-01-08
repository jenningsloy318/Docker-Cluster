Aspects about running k8s.

1. [Deployment](./Deployment)
2. [Operations](./Operations)



to do list: 

- [ ] 1.  ODIC (IDP) provider and RBAC control to restrict the access permission for individual users/groups and different role-binding;
- [ ] 2.  resource restrict and isolation, figure out what permissions each pod needs when we are going to limit the permission for Pods;
- [ ] 3.  failure  auto-recovery and data backup strategy,for kubernetes itself , we can consider to backup etcd cluster;
- [ ] 4.  persistent volume storage, now we use nfs-provision for nfs storage, but still have many options such as aws/azure/gce/ceph/gluster...;
- [ ] 5.  blue/green deployment and roll-upgrading of deployment, via creating new yaml file or use command line to edit current configration or operation its API;
- [ ] 6.  better service exposure method, currently use ingress controller with ingress rules defined , new method kube2haproxy can be taken into account ;
- [x] 7.  configure docker service to enable un-previleged docker/tcp socket which can be used to build docker images remotely;
- [ ] 8.  priviate docker registry(jfrog/artifactory, vmware/harbor) with https setting;
- [ ] 9.  auto-create pod/devployment config based on template(python/jinja2, go/template), we can reference ingress as an example, which can create nginx conf  based on ingress rule;
- [ ] 10. ELK and monitor system are up with initial configuration, we need deep investigation and configuration to meet our operation needs.
- [ ] 11. add [Liveness and Readiness Probes for pods](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-probes/)
- [ ] 12. manifest templates and generation tool [ktmpl](https://github.com/InQuicker/ktmpl)
