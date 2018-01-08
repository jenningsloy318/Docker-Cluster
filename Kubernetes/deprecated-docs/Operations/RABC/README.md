1. begin with 1.6+. RBAC is more detailed descirbed [Using RBAC Authorization](https://kubernetes.io/docs/admin/authorization/rbac/)
2. different roles and rolebinding
    
    2.1 Discovery Roles

    |Default |ClusterRole Default ClusterRoleBinding | Description|
    |---------|---------------------------------------|-----------|
    |system:basic-user  | system:authenticated and system:unauthenticated groups |Allows a user read-only access to basic information about themselves.|
    |system:discovery |system:authenticated and system:unauthenticated groups |Allows read-only access to API discovery endpoints needed to discover and negotiate an API level.|


    2.2 User-facing Roles

    |Default |ClusterRole Default ClusterRoleBinding | Description|
    |---------|---------------------------------------|-----------|
    |cluster-admin|system:masters group|Allows super-user access to perform any action on any resource. When used in a ClusterRoleBinding, it gives full control over every resource in the cluster and in all namespaces. When used in a RoleBinding, it gives full control over every resource in the rolebinding's namespace, including the namespace itself.|
    |cluster-status|None|Allows read-only access to basic cluster status information.|
    |admin|None|Allows admin access, intended to be granted within a namespace using a RoleBinding. If used in a RoleBinding, allows read/write access to most resources in a namespace, including the ability to create roles and rolebindings within the namespace. It does not allow write access to resource quota or to the namespace itself.|
    |edit|None|Allows read/write access to most objects in a namespace. It does not allow viewing or modifying roles or rolebindings.|
    |view|None|Allows read-only access to see most objects in a namespace. It does not allow viewing roles or rolebindings. It does not allow viewing secrets, since those are escalating.|

    2.3 Core Component Roles


    |Default |ClusterRole Default ClusterRoleBinding | Description|
    |---------|---------------------------------------|-----------|
    |system:kube-scheduler|system:kube-scheduler user|Allows access to the resources required by the kube-scheduler component.|
    |system:kube-controller-manager|system:kube-controller-manager user|Allows access to the resources required by the kube-controller-manager component. The permissions required by individual control loops are contained in the controller roles.|
    |system:node|system:nodes group|Allows access to resources required by the kubelet component, including read access to secrets, and write access to pods. In the future, read access to secrets and write access to pods will be restricted to objects scheduled to the node. To maintain permissions in the future, Kubelets must identify themselves with the group system:nodes and a username in the form system:node:<node-name>. See [https://pr.k8s.io/40476](https://pr.k8s.io/40476) for details.|
    |system:node-proxier|system:kube-proxy user|Allows access to the resources required by the kube-proxy component.|
    
    2.4 Other Component Roles


    |Default |ClusterRole Default ClusterRoleBinding | Description|
    |---------|---------------------------------------|-----------|
    |system:auth-delegator|None|Allows delegated authentication and authorization checks. This is commonly used by add-on API servers for unified authentication and authorization.|
    |system:heapster|None|Role for the Heapster component.|
    |system:kube-aggregator|None|Role for the kube-aggregator component.|
    |system:kube-dns|kube-dns service account in the kube-system namespace|Role for the kube-dns component.|
    |system:node-bootstrapper|None|Allows access to the resources required to perform Kubelet TLS bootstrapping.|
    |system:node-problem-detector|None|Role for the node-problem-detector component.|
    |system:persistent-volume-provisioner|None|Allows access to the resources required by most dynamic volume provisioners.|

