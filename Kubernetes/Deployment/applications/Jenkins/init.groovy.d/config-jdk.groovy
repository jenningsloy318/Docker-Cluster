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