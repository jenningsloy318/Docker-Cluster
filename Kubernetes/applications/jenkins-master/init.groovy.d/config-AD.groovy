import jenkins.model.*
import hudson.security.*
import hudson.plugins.active_directory.*
   
def instance = Jenkins.getInstance()
Thread.start {
    sleep 10000
    String domain = 'my.domain.com'
    String site = 'site'
    String server = '192.168.1.1'
    String bindName = 'account@my.domain.com'
    String bindPassword = 'password'
    adrealm = new ActiveDirectorySecurityRealm(domain, site, bindName, bindPassword, server)
    instance.setSecurityRealm(adrealm)
}