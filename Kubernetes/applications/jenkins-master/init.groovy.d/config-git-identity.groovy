def desc_git_scm = instance.getDescriptor("hudson.plugins.git.GitSCM")
Thread.start {
    sleep 10000
    println "--> Configuring Git Identity"
    desc_git_scm.setGlobalConfigName(gitGlobalConfigName)
    desc_git_scm.setGlobalConfigEmail(gitGlobalConfigEmail)
}