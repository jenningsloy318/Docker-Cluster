    import jenkins.model.*
    import hudson.security.*
    import jenkins.security.s2m.AdminWhitelistRule
    sleep 300000

    def instance = Jenkins.getInstance()
     
    def user = new File("/run/secrets/username").text.trim()
    def pass = new File("/run/secrets/password").text.trim()
     
    def hudsonRealm = new HudsonPrivateSecurityRealm(false)
    hudsonRealm.createAccount(user, pass)
    instance.setSecurityRealm(hudsonRealm)
     
    def strategy = new FullControlOnceLoggedInAuthorizationStrategy()
    instance.setAuthorizationStrategy(strategy)
    instance.save()
     
    Jenkins.instance.getInjector().getInstance(AdminWhitelistRule.class).setMasterKillSwitch(false)