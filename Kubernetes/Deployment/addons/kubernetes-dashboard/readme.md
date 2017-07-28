##Tips

1. create proper RBAC, here we use [cluster-view](../../RBAC/cluster-view.yaml), besides normal `get`,`watch`,`list`, dashboard still need `proxy`, to proxy to heapster to get the cluster compute resource usage, so add `proxy` into the verb list.
