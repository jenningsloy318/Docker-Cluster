**Description:**
    
  while in the previous settings, when add new node to cluster, administrator need to create certificates for the node, while TLS bootstraping can make node get its certificate by itself, details explanation refer to [TLS bootstrapping](https://kubernetes.io/docs/admin/kubelet-tls-bootstrapping/).

  1. Enable the **Bootstrap Token Authenticator** with the `--enable-bootstrap-token-auth` flag on the API Server, also Add the `--client-ca-file= ` flag.
  2. add new bootstrap token into `/srv/kubernetes/token.csv`.
     for example:
     ```
     02b50b05283e98dd0fd71db496ef01e8,system:node:192.168.59.130,10001,"system:bootstrappers,system:node-bootstrapper,system:nodes"
     ```
   explanation: 
   - bind to `system:bootstrappers` will let apiserver's to authenticate tokens as a user in the `system:bootstrappers` group
   - set the name of the user to `system:node:<node>` and place in group `system:nodes` will grant it permission to register it into the cluster automatically.


  3. Enable the **TokenCleaner** and **bootstrapsigner** controller via the --controllers flag on the Controller Manager. This is done with something like `--controllers=*,tokencleaner,bootstrapsigner`, and also configure `--cluster-signing-cert-file=` and `--cluster-signing-key-file=`

  4. to auto approve all CSRs for the group "system:bootstrappers", create a ClusterRoleBinding targeting that group:
   ```yaml
   kind: ClusterRoleBinding
   apiVersion: rbac.authorization.k8s.io/v1
   metadata:
     name: auto-approve-csrs-for-group
   subjects:
   - kind: Group
     name: system:bootstrappers
     apiGroup: rbac.authorization.k8s.io
   roleRef:
     kind: ClusterRole
     name: system:certificates.k8s.io:certificatesigningrequests:nodeclient
     apiGroup: rbac.authorization.k8s.io
   ````
  to renew its own credentials for the group "system:bootstrappers", create a ClusterRoleBinding targeting that group:
   ```yaml
   kind: ClusterRoleBinding
   apiVersion: rbac.authorization.k8s.io/v1
   metadata:
     name: auto-approve-renewal-csrs-for-group
   subjects:
   - kind: Group
     name: system:bootstrappers ## Let group "system:bootstrappers" renew its client certificate.
     apiGroup: rbac.authorization.k8s.io
   roleRef:
     kind: ClusterRole
     name: system:certificates.k8s.io:certificatesigningrequests:selfnodeclient
     apiGroup: rbac.authorization.k8s.io
   ```

  5. kubelet configuration
     
     5.1 create kubeconfig for kubelet,`kubectl config set-cluster`, `set-credentials`, and `set-context` to build this kubeconfig. Provide the name kubelet-bootstrap to `kubectl config set-credentials` and include `--token=<token-value>` as follows:
     
     ```
     kubectl config set-credentials kubelet-bootstrap --token=02b50b05283e98dd0fd71db496ef01e8 --kubeconfig=/srv/kubernetes/kubelet.kubeconfig
     kubectl config set-context kubelet-bootstrap@kubernetes --cluster=kubernetes --user=kubelet-bootstrap  --kubeconfig=/srv/kubernetes/kubelet.kubeconfig
     kubectl config use-context kubelet-bootstrap@kubernetes  --kubeconfig=/srv/kubernetes/kubelet.kubeconfig
     ```
     5.2 add following flags to
     ```
     --require-kubeconfig
     --bootstrap-kubeconfig="/srv/kubernetes/kubelet.kubeconfig"
     ```