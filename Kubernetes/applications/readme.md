Tips
---

1. use subPath to mount secret/configmap as subPath under one directory.

    Basically, any volumes will be mount at root of the mountPath, but we can add a subPath to enable it mounted at the subPath of the mountPath

    Cases when the target mount point is already exist, and we don't want to overwrite the whole content of the directory, when need to use subPath to specify the exact mount path of the secret/configmap. 

    - case1: mount configmap which contains supervisord.conf to `/etc/supervisord.conf`. 

      we all know that each configmap is consisted of  key-value pairs, it contains one or more keys with its value. so in the `volumes` section of `pod` definition, we can set the (sub-)path of the configmap key, this (sub-)path is eventually created under the `mountPath` of `volumeMounts`, which means that the content of  this (sub-)path(it should be a file) is same with  configmap data(the data of corresponding key).


        key = the file name or the key you provided on the command line, and
        
        value = the file contents or the literal value you provided on the command line.
    
        ```
        volumes
          configMap:
            name: supervisord-conf
            items:     
            - key: supervisord.conf
              path: supervisord.conf    
        ```

        and the mounts, the subPath should be the same with the `path` in `volumes`.

        ```
        volumeMounts: 
        - name: supervisior-conf
          mountPath: /etc/supervisord.conf
          subPath: supervisord.conf    
        ```
        

        Now file is mounted under /etc/supervisord.conf, and all other files under /etc/ still exist.


    - case2: mount configmap which contains docker certs to /home/jenkins/.docker

        Here we have three keys in the configmap, they will be mounted under same mountPath /home/jenkins/.docker

        ```
        volumes
        - name: dockerconfig
          configMap:
            name: jenkins-conf
            items:
            - key: docker_client_key
              path: key.pem          
            - key: docker_client_cert
              path: cert.pem   
            - key: docker_ca_cert
              path: ca.pem   
        ```

        and the mounts,  multiple files mounted under the same mountPath, no need to specify the subPath

        ```
        volumeMounts: 
        - name: dockerconfig
          mountPath: /home/jenkins/.docker/
        ```