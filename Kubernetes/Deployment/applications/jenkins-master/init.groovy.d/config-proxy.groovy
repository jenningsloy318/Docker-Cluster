pc = new hudson.ProxyConfiguration(name, port, userName, password, noProxyHost);
jenkins.model.Jenkins.instance.proxy = pc;"
println "Jenkins-Proxy settings updated!