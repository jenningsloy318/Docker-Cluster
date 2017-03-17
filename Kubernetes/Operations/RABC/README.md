1. admin user
  
   add the group system:masters means the most powerful user
    
    - cert, we'd add ***/O=system:masters*** for the group

        ```shell
         openssl genrsa -out admin-key.pem 2048
         openssl req -new -key admin-key.pem -out admin.csr -subj "/O=system:masters/CN=admin"
         openssl x509 -req -in admin.csr -CA ca.pem -CAkey ca-key.pem -CAcreateserial -out admin.pem -days 365
        ```
    - basic auth

        ```csv
        password,user,uid,"group1,group2,group3"
        kubernetes,admin,admin,system:masters
        ```

    - token auth

        ```csv
        token,user,uid,"group1,group2,group3"
        eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9,admin,admin,system:masters
        ```

2. kubelet user

3. kube-proxy user

4. defualt service account in kube-system namespace

5. roles and rolesbinding, take this blog [How we got RBAC working in Kubernetes](http://blog.screwdriver.cd/post/150999692902/how-we-got-rbac-working-in-kubernetes) as reference; also we can check this page [kubernete auth plugin example](https://github.com/kubernetes/kubernetes/tree/master/plugin/pkg/auth/authorizer/rbac/bootstrappolicy/testdata)

6. for other users, we can create after k8s is up.
