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