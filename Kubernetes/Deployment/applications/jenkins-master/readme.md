## set JENKINS_OPTS
```
JENKINS_OPTS --httpPort=-1 --httpsPort=8083 --httpsCertificate=/var/lib/jenkins/cert --httpsPrivateKey=/var/lib/jenkins/pk --prefix=/jenkins
JENKINS_HOME /var/jenkins_home/
```

## we can place all initial conf to $JENKINS_HOME/init.groovy.d

    - tcp-slave-agent-port.groovy
    - 