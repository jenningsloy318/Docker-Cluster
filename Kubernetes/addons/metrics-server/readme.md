
[Metrics repo](https://github.com/kubernetes-incubator/metrics-server)
- Metric server collects metrics from the Summary API, exposed by Kubelet on each node.
- Metrics Server registered in the main API server through Kubernetes aggregator

- any request to /apis/metrics endpoint  of apiserver will redirect the request from the apiserver to metrics server; and then metrics server will make request to each kubelet, the flags `--proxy-client-cert-file` and `--proxy-client-key-file` will be configured in the kube-apiserver to let kubelet know from where the request from. 