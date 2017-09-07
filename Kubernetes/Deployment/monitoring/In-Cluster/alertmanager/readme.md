1. create configmap to accommodate altermanager templates.
  ```
  kubectl create configmap alertmanager-templates --from-file=default.tmpl -n monitoring
  ```
