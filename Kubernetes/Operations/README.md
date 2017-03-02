---

Here I listed the aspects about how to run k8s better.

1. [Ingress](./ingress)
   
   we use Ingress controller and individual ingress rules to expose services. 
*Kubernetes has several ways to expose the service to outside.*

   - Nodeport: as we discussed in the ```deployment/dashboard``` section, use ```Nodeport``` plus ```externalIPs```to expose the service, and this can be integreated with outside loadbalancer

   - we can also use ingres to expose the services.

     - for details about ingress, refer to [kubernetes userguide](https://kubernetes.io/docs/user-guide/ingress/) and [ingress github](https://github.com/kubernetes/ingress) and [ingress configuration](https://github.com/kubernetes/ingress/blob/master/controllers/nginx/configuration.md)

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
		 **since ingress controller will watch all namespaces, so we can deploy ingress controller and backend service in any namespces, it will listen other namespaces's requests**
     - create [dashboard ingress](./ingress/dashboard-ingress.yaml)

         ```yaml
         $ kubectl create -f dashboard-ingress.yaml
         ```

     - basic authentication 
        
        - create auth configmap

            ```sh
            htpasswd -b -c  auth  admin kubernetes
            kubectl create secret generic dashboard-basic-auth --from-file=auth  -n kube-system
            ```
        
        -  modify the ingress rules  and add 
            
            ```yaml
            metadata:
             name: kubernetes-dashboard-ingress
             namespace: kube-system
             annotations:
                ingress.kubernetes.io/auth-type: "basic"
                ingress.kubernetes.io/auth-secret: "dashboard-basic-auth"
                ingress.kubernetes.io/auth-realm: "Authentication Required, please inpurt user and password"
            ```
            
            now we have to input user and password to get into the dashboard
    now we can access dashboard via ```http://kube-master/```

      - add ssl for the application.
          - create a priviate key using openssl

             ```sh
             # openssl genrsa -out app-key.pem 2048
             ```

          - modify [openssl.conf](./ssl/openssl.conf), under ```[alt_names]``` replace the ```IP``` and ```DNS``` for the service

             ```conf
             [req]
             req_extensions = v3_req
             distinguished_name = req_distinguished_name
             [req_distinguished_name]
             [ v3_req ]
             basicConstraints = CA:FALSE
             keyUsage = nonRepudiation, digitalSignature, keyEncipherment
             subjectAltName = @alt_names
             [ v3_ca ]
             subjectAltName = @alternate_names
             [alt_names]
             DNS.1=kube-master.mo.sap.corp
             ```
          - create the sign request,replace the valube of ```-subj ``` with your own, which must be a *FQDN* DNS name.

             ```sh
             # openssl req -new -key app-key.pem -out app.csr  -subj "/CN=kube-master.mo.sap.corp" -onfig openssl.conf
             ```



          -  copy the content of ```app.csr```, and paste it to [https://getcerts.wdf.global.corp.sap/pgwy/request/sapnetca_base64.html](https://getcerts.wdf.global.corp.sap/pgwy/request/sapnetca_base64.html) to get the certificate.

          -  copy the content of the certificate and save to app-cert.pem

          - create secret for this cert and key.       
            
            ```sh
            kubectl create secret tls kube-master-secret --key app-key.pem --cert app-cert.pem
            ```
          - modify ingress, add tls setting, then issue ```kubectl apply -f dashboard-ingress.yaml```to apply the changes.
                
            ```yaml
            apiVersion: extensions/v1beta1
            kind: Ingress
            metadata:
             name: kubernetes-dashboard-ingress
            spec:
             tls:
              - hosts:
                - kube-master.mo.sap.corp
                secretName: kube-master-secret
             rules:
               - host: kube-master.mo.sap.corp
                 http:
                   paths:
                     - path: /
                       backend:
                         serviceName: kubernetes-dashboard
                         servicePort: 80
                                          
2. CI/CD integration

    we use jenkins to triger CI/CD jobs, now we have depoyed two kinds of jenkins instances in our environment, with super privilege, because it will utilize docker service on the hosts. 
    Jenkins jobs will be excuting inside these PODs, buiding docker images leveraging host docker service , then pushed to our priviate docker registry.  at the same time CD jobs will be trigered which use ```kubectl apply -f pod.ymal```to create the deployment/pod/replica/svc/ingress rules. 
    examples of the jenkins pod are listed in [jenkins](./jenkins).

    we still have another things to do:
      - configure host docker service, which can be running under normal users but not root user;
      - configure host docker service , which can accept the request from tcp socket, not only unix socket;
      - running the jenkins in non-previleged way, which is more secure;
      - use ingress to expose the jenkins services.

3. Persistent Volume
    
    Types of Persistent volume:
      - static: each PV and PVC should be created before it is used in the pod, and the restrict it one pv can only be bound to one pvc. 
      - dynamic: create storageclass to host the backend storages, then each pvc can claim its storage volumes from the storageclass; thus we only need to create the storageclass and it can be used mulitple times when multiple pvc is created. 

    we still have enough flexible choices to serve the backend storages, we don't have cloud storage service, and it is also expensive to build a openstack cinder or gluster or ceph cluster which need at least 2-3 nodes. we only have one choice *NFS*. luckily I found a incubate project [nfs-provisioner](https://github.com/kubernetes-incubator/nfs-provisioner) which can meet our need. 
      
    3.1 use nfs-provisioner to create nfs service, which use hostpath as its volume; then nfs-provisioner will be used as the backend of storageclass.
				here we use StatefulSet to host the nfs service as suggested.

  	3.2 Create storageClass
						
				
    the  whole content of the file is [nfs-provisoner.yaml](./nfs-provisioner/nfs-provisoner.yaml)
              

4. Auto-deploy option
		
		As we describe ealier, use CI/CD to trigger the deployment is one option, here I listed two more options.
      
      - static pods started by kubelet service, kubelet service will scan the directory ```--pod-manifest-path``` to start them.
      - another one  which is inspired by the kubernetes official addon-manager, I created app-manager. it use fswatch to watch the directory, create new kubernete resources once new changes detected. 

    we use  [Dockerfile](./app-manager/Dockerfile) to create the docker images which includes [app-manager.sh](./app-manager/app-manager.sh) and optional [kubeconfig](./app-manager/kubeconfig)
	 
