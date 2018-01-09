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


2. for alertmanager, now it supports  sending notification via wechat.
   
    2.1 get the corpid on enterprise wechat from https://work.weixin.qq.com/wework_admin/frame#profile, you can see `CorpID`.

    2.2 Create new application in enterprise wechat https://work.weixin.qq.com/wework_admin/frame#apps if not exists, you can see   `AgentId`,`Secret`,and `可见范围`. here `AgentId` and `Secret` are generated automatically, we need to configure `可见范围` to some `users` or `department` in `Contacts`, `可见范围` list the user/department list  whom this application has the permission to send the notification to.
    
    2.3 Get the ID of the department in contact, refer to https://work.weixin.qq.com/api/doc#10093

    2.4 for the reciever setting,  `touser`,`toparty`, and `totag` are explained in https://work.weixin.qq.com/api/doc#10167, agentid is retrieved in #2.2