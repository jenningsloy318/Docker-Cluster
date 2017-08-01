/*set nodeslaveport*/

import hudson.model.*;
import jenkins.model.*;
Thread.start {
      sleep 10000
      println "--> setting agent port for jnlp"
      def env = System.getenv()
      int port = env['JENKINS_SLAVE_AGENT_PORT'].toInteger()
      Jenkins.instance.setSlaveAgentPort(port)
      println "--> setting agent port for jnlp... done"
}


/*set E-mail Notification*/
import jenkins.model.*
def instance = Jenkins.getInstance()
def desc = instance.getDescriptor("hudson.tasks.Mailer")
desc.setReplyToAddress("jennings.liu@sap.com")
desc.setSmtpHost("mailsin.sap.corp")
desc.setUseSsl(false)
desc.setSmtpPort("25")
desc.setCharset("UTF-8")
desc.save()



/*install plugin*/
import jenkins.model.*
import hudson.model.*;
def instance = Jenkins.getInstance()
def activatePlugin(plugin) {
        if (! plugin.isEnabled()) {
        plugin.enable()
        deployed = true
        }
        plugin.getDependencies().each {
            activatePlugin(pm.getPlugin(it.shortName))
        }
    }
Thread.start {
    sleep 10000
    pm = instance.pluginManager
    uc = instance.updateCenter
    pm.plugins.each { 
        plugin ->plugin.disable()
        }
    
    deployed = false

    
    ["git", "active-directory","role-strategy","github","gerrit-trigger"].each {
    if (! pm.getPlugin(it)) {
      println("Installing plugin $it")
      deployment = uc.getPlugin(it).deploy(true)
      deployment.get()
    
    }
    activatePlugin(pm.getPlugin(it))
    }
    
    if (deployed) {
    println("saving Jenkins configuration!")
    instance.save()
    }

}
/*set global security,set active directory*/

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


/*Configuring Git Identity*/
def desc_git_scm = instance.getDescriptor("hudson.plugins.git.GitSCM")
Thread.start {
    sleep 10000
    println "--> Configuring Git Identity"
    desc_git_scm.setGlobalConfigName(gitGlobalConfigName)
    desc_git_scm.setGlobalConfigEmail(gitGlobalConfigEmail)
}



/*configure gerrit*/
import hudson.model.*;
import jenkins.model.*;
import com.sonyericsson.hudson.plugins.gerrit.trigger.PluginImpl;
import com.sonyericsson.hudson.plugins.gerrit.trigger.GerritServer;
import com.sonyericsson.hudson.plugins.gerrit.trigger.config.Config;


// Variables
def gerrit_host_name = env['GERRIT_HOST_NAME']
def gerrit_front_end_url = env['GERRIT_FRONT_END_URL']
def gerrit_ssh_port = env['GERRIT_SSH_PORT'] ?: "29418"
gerrit_ssh_port = gerrit_ssh_port.toInteger()
def gerrit_username = env['GERRIT_USERNAME'] ?: "jenkins"
def gerrit_profile = env['GERRIT_PROFILE'] ?: "ADOP Gerrit"
def gerrit_email = env['GERRIT_EMAIL'] ?: ""
def gerrit_ssh_key_file = env['GERRIT_SSH_KEY_FILE'] ?: "/var/jenkins_home/.ssh/id_rsa"
def gerrit_ssh_key_password = env['GERRIT_SSH_KEY_PASSWORD'] ?: null

// Constants
def instance = Jenkins.getInstance()

Thread.start {
    sleep 10000

    // Gerrit
    println "--> Configuring Gerrit"

    def gerrit_trigger_plugin = PluginImpl.getInstance()

    def gerrit_server = new GerritServer(gerrit_profile)

    def gerrit_servers = gerrit_trigger_plugin.getServerNames()
    def gerrit_server_exists = false
    gerrit_servers.each {
        server_name = (String) it
        if ( server_name == gerrit_server.getName() ) {
            gerrit_server_exists = true
            println("Found existing installation: " + server_name)
        }
    }

    if (!gerrit_server_exists) {
        def gerrit_server_config = new Config()

        gerrit_server_config.setGerritHostName(gerrit_host_name)
        gerrit_server_config.setGerritFrontEndURL(gerrit_front_end_url)
        gerrit_server_config.setGerritSshPort(gerrit_ssh_port)
        gerrit_server_config.setGerritUserName(gerrit_username)
        gerrit_server_config.setGerritEMail(gerrit_email)
        gerrit_server_config.setGerritAuthKeyFile(new File(gerrit_ssh_key_file))
        gerrit_server_config.setGerritAuthKeyFilePassword(gerrit_ssh_key_password)

        gerrit_server.setConfig(gerrit_server_config)
        gerrit_trigger_plugin.addServer(gerrit_server)
        gerrit_server.start()
        gerrit_server.startConnection()
    }

    // Save the state
    instance.save()
}



/*config sonar*/
// Configure global sonar
def sonar = { instance, sonar_host, sonar_addr, sonar_db, sonar_user, sonar_password ->
  assert instance : "Must pass a valid jenkins instance. E.g: Jenkins.getInstance()"
  assert sonar_host : "Must pass a valid sonar host. E.g: localhost"
  assert sonar_addr : "Must pass a valid sonar address. E.g: http://${sonar_host}:9000"
  assert sonar_db : "Must pass a valid sonar db connection. E.g: jdbc:mysql://${sonar_host}:3306/sonar?useUnicode=true&characterEncoding=utf8&rewriteBatchedStatements=true&useConfigs=maxPerformance&autoReconnect=true"
  assert sonar_user : "Must pass a valid sonar user"
  assert sonar_password : "Must pass a valid sonar password"

  def descriptor = instance.getDescriptor("hudson.plugins.sonar.SonarGlobalConfiguration")
  def sonar = new hudson.plugins.sonar.SonarInstallation(
    sonar_host,
    sonar_addr,
    "5.1",
    "",
    sonar_db,
    sonar_user,
    sonar_password,
    "",
    "-Dsonar.sourceEncoding=\"UTF-8\"",
    new hudson.plugins.sonar.model.TriggersConfig(),
    sonar_user,
    sonar_password,
    ""
  )
  descriptor.setInstallations(sonar)
  descriptor.save()
  println "Setting up global Sonar installation"
}


/*configure mvn*/
import jenkins.model.*
def instance = Jenkins.getInstance()

// Tell jenkins where maven is
def mavenTask = Jenkins.instance.getExtensionList(
  hudson.tasks.Maven.DescriptorImpl.class
)[0]
mavenTask.setInstallations(
  new hudson.tasks.Maven.MavenInstallation(
    "Maven", "$M2_HOME", []
  )
)
mavenTask.save()

// Configure global maven options
def maven = Jenkins.instance.getExtensionList(
  hudson.maven.MavenModuleSet.DescriptorImpl.class
)[0]
maven.setGlobalMavenOpts("-Dmaven.test.failure.ignore=false")
maven.save()


/*set global email*/
Global email settings

import jenkins.model.*
def instance = Jenkins.getInstance()

// set email
def location_config = JenkinsLocationConfiguration.get()
location_config.setAdminAddress("jenkins@azsb.skybet.net")


/*set proxy*/
pc = new hudson.ProxyConfiguration(name, port, userName, password, noProxyHost);
jenkins.model.Jenkins.instance.proxy = pc;"
println "Jenkins-Proxy settings updated!



/*auto-installing  jdk */
import jenkins.model.*
import hudson.model.*
import hudson.tools.*

def inst = Jenkins.getInstance()

def desc = inst.getDescriptor("hudson.model.JDK")

def versions = [
  "jdk8": "jdk-8u102-oth-JPR"
]
def installations = [];

for (v in versions) {
  def installer = new JDKInstaller(v.value, true)
  def installerProps = new InstallSourceProperty([installer])
  def installation = new JDK(v.key, "", [installerProps])
  installations.push(installation)
}

desc.setInstallations(installations.toArray(new JDK[0]))

desc.save()  
// Required: enter credentials at http://l:8080/descriptorByName/hudson.tools.JDKInstaller/enterCredential


/*set jdk*/

#!groovy
// On GUI, this is on Configure Tools page, "JDK" section
// In config.xml, this is under <jdks>

import jenkins.model.*
import hudson.model.*
import groovy.io.FileType

def jdkDir = "/usr/java"
def inst = Jenkins.getInstance()
def desc = inst.getDescriptor("hudson.model.JDK")

def dirs = []
def currentDir = new File(jdkDir)
currentDir.eachFile FileType.DIRECTORIES, {
    dirs << it.name
}

def installations = []
for (dir in dirs) {
  def installation = new JDK(dir, jdkDir + "/" + dir)
  installations.push(installation)
}

desc.setInstallations(installations.toArray(new JDK[0]))

desc.save()
inst.save()


/*mail-ext*/
import jenkins.model.*

def inst = Jenkins.getInstance()

def desc = inst.getDescriptor('hudson.tasks.Mailer')

desc.setSmtpHost("#{node['cvent-jenkins']['email-ext-plugin']['host']}")
desc.setDefaultSuffix("#{node['cvent-jenkins']['email-ext-plugin']['defaultSuffix']}")
desc.setReplyToAddress("#{node['cvent-jenkins']['email-ext-plugin']['replyTo']}")
    
desc.save()



/*set admin at boot, password saved in k8s secrets */

 
import jenkins.model.*
import hudson.security.*
import jenkins.security.s2m.AdminWhitelistRule
 
def instance = Jenkins.getInstance()
 
def user = new File("/run/secrets/jenkins-user").text.trim()
def pass = new File("/run/secrets/jenkins-pass").text.trim()
 
def hudsonRealm = new HudsonPrivateSecurityRealm(false)
hudsonRealm.createAccount(user, pass)
instance.setSecurityRealm(hudsonRealm)
 
def strategy = new FullControlOnceLoggedInAuthorizationStrategy()
instance.setAuthorizationStrategy(strategy)
instance.save()
 
Jenkins.instance.getInjector().getInstance(AdminWhitelistRule.class).setMasterKillSwitch(false)