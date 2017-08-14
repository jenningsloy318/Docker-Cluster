FROM ubuntu:16.04
ARG DEBIAN_FRONTEND=noninteractive
ARG DEBCONF_NONINTERACTIVE_SEEN=true
ARG uid=1000
ARG gid=1000
ARG user=jenkins
ARG group=jenkins
ARG passwd=jenkins
ENV JAVA_HOME /usr/lib/jvm/java-1.8.0-openjdk-amd64
ENV JENKINS_HOME /var/jenkins_home
ARG http_port=8080
ARG agent_port=50000

RUN apt-get -y update && \
    apt-get install  --no-install-recommends -y ca-certificates  openjdk-8-jdk-headless git curl openssh-client openssh-server supervisor sudo maven && \
    apt-get clean all &&  rm -rf /var/lib/apt/lists/* && \
    groupadd -g ${gid} ${group} &&\
    useradd -d "$JENKINS_HOME" -u ${uid} -g ${gid} -G sudo -m -s /bin/bash ${user} && \
    echo  "${user}:${passwd}"|chpasswd && \
    echo "%jenkins  ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers



VOLUME /var/jenkins_home

# `/usr/share/jenkins/ref/` contains all reference configuration we want 
# to set on a fresh new installation. Use it to bundle additional plugins 
# or config file with your custom jenkins Docker image.

# jenkins version being bundled in this docker image
ENV JENKINS_SLAVE_AGENT_PORT ${agent_port}
ARG JENKINS_VERSION
ENV JENKINS_VERSION ${JENKINS_VERSION:-2.60.2}

# jenkins.war checksum, download will be validated using it
ARG JENKINS_SHA=14d0788d89be82958a46965de039a55813f9727bd4d0592dc77905976483ba95

# Can be used to customize where jenkins.war get downloaded from
ARG JENKINS_URL=https://repo.jenkins-ci.org/public/org/jenkins-ci/main/jenkins-war/${JENKINS_VERSION}/jenkins-war-${JENKINS_VERSION}.war

# could use ADD but this one does not check Last-Modified header neither does it allow to control checksum 
# see https://github.com/docker/docker/issues/8331
RUN mkdir -p /usr/share/jenkins /var/run/sshd && \
    curl -fsSL ${JENKINS_URL} -o /usr/share/jenkins/jenkins.war &&\
    echo "${JENKINS_SHA}  /usr/share/jenkins/jenkins.war" | sha256sum -c -  &&\
    curl -SL  https://storage.googleapis.com/kubernetes-release/release/v1.7.3/bin/linux/amd64/kubectl -o /usr/bin/kubectl  && \
    chmod +x /usr/bin/kubectl &&\
    curl -SL  https://get.docker.com/builds/Linux/x86_64/docker-1.12.6.tgz -o /tmp/docker-1.12.6.tgz && \
    tar xvf /tmp/docker-1.12.6.tgz --exclude="docker[d-]*" --strip-components 1 -C /usr/bin && rm -rf /tmp/docker-1.12.6.tgz &&\
    curl -SL "https://cli.run.pivotal.io/stable?release=linux64-binary&source=github" | tar -zx &&\
	  mv cf /usr/bin && rm -rf cf-cli_*.tgz &&\
    curl -SLO https://github.infra.hana.ondemand.com/cloudfoundry/cf-cli-mta-plugin/releases/download/v0.7.0/mta_plugin_linux_amd64 &&\
    chmod +x mta_plugin_linux_amd64 &&\
    cf install-plugin mta_plugin_linux_amd64 -f && rm -f mta_plugin_linux_amd64 && \
    curl -SL  -k http://aia.pki.co.sap.com/aia/SAPNetCA_G2.crt -o /usr/local/share/ca-certificates/SAPNetCA_G2.crt && \
    curl -SL  -k http://aia.pki.co.sap.com/aia/SAP%20Global%20Root%20CA.crt -o /usr/local/share/ca-certificates/SAP%20Global%20Root%20CA.crt && \
    keytool -noprompt -import -alias sapglobalrootca -file /usr/local/share/ca-certificates/SAP%20Global%20Root%20CA.crt -keystore /usr/lib/jvm/java-8-openjdk-amd64/jre/lib/security/cacerts -storepass changeit && \
    keytool -noprompt -import -alias sapnetcag2 -file /usr/local/share/ca-certificates/SAPNetCA_G2.crt  -keystore /usr/lib/jvm/java-8-openjdk-amd64/jre/lib/security/cacerts -storepass changeit && \
	  keytool -trustcacerts -noprompt -keystore /etc/ssl/certs/java/cacerts -importcert -alias SAP_Global_Root_CA.crt -file  /usr/local/share/ca-certificates/SAP%20Global%20Root%20CA.crt  -storepass changeit && \
	  keytool -trustcacerts -noprompt -keystore /etc/ssl/certs/java/cacerts -importcert -alias SAPNetCA_G2 -file  /usr/local/share/ca-certificates/SAPNetCA_G2.crt  -storepass changeit && \
    update-ca-certificates &&\
    sed -i /PasswordAuthentication/s/no/yes/ /etc/ssh/sshd_config


    
    
	  

ENV PATH $JAVA_HOME/bin:/opt/maven/bin:$PATH
ENV JENKINS_UC https://updates.jenkins.io
ENV JENKINS_UC_EXPERIMENTAL=https://updates.jenkins.io/experimental

# for main web interface and slave agents:

EXPOSE ${http_port}
EXPOSE ${agent_port}

USER root
COPY download-ci-connect-plugin.sh  /usr/local/bin/
ENTRYPOINT ["/usr/bin/supervisord"]
