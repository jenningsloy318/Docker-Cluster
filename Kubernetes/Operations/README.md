---

Here I listed the aspects about how to run k8s better.

1. Ingress 
   
   we use Ingress controller and individual ingress rules to expose services. 
*Kubernetes has several ways to expose the service to outside.*

   - Nodeport: as we discussed in the ```deployment/dashboard``` section, use ```Nodeport``` plus ```externalIPs```to expose the service, and this can be integreated with outside loadbalancer

   -we can also use ingres to expose the services.

     - for details about ingress, refer to [kubernetes userguide](https://kubernetes.io/docs/user-guide/ingress/) and [ingress github](https://github.com/kubernetes/ingress).

     - since we have some special demands about the ingress, we need to change the some default settings in nginx, so we create [nginx.tmpl](./ingress/nginx.tmpl), I changed the default http port to 8080 since 80 port is disabed by fault in our datacenter. 

     -  create the configmap for it.

          ```sh
          $ kubectl create configmap nginx-template --from-file=nginx.tmpl=./ingress/nginx.tmpl
          ```

     - create [default-backend](./ingress/default-backend.yaml) for ingress controller.

         ```sh
         $ kubecte create -f default-backend.yaml
         ```
     - create [ingress controller](./ingress/nginx-ingress-controller.yaml)

         ```sh
         $ kubectl create -f nginx-ingress-controller.yaml
         ```

     - create [dashboard ingress](./ingress/dashboard-ingress.yaml)

         ```yaml
         $ kubectl create -f dashboard-ingress.yaml
         ```

    now we can access dashboard via ```http://kube-master/```
