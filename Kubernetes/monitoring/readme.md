1. shell to simulate alerts

```sh
#!/bin/bash
url='http://10.58.137.244:9093/api/v1/alerts'
echo "firing up alert myservice alert"

curl -XPOST $url -d '[{
"labels": {
"alertname": "my-service alter",
"service": "my-service",
"severity": "warning",
"instance": "myservice.example.net"
},
"annotations": {
"summary": "High latency is high!"
},
"generatorURL": "http://prometheus.int.example.net/generating_expression"
}]'
```