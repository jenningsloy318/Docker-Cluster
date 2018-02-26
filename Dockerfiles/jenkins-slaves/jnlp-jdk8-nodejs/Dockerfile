FROM ubuntu:16.04

RUN  apt-get update && \
     apt-get install -y software-properties-common && \
     echo oracle-java8-installer shared/accepted-oracle-license-v1-1 select    true | debconf-set-selections && \
     add-apt-repository -y ppa:webupd8team/java && \
     apt-get update && \
     apt-get install -y curl oracle-java8-installer && \
     echo "export JAVA_HOME=/usr/lib/jvm/java-8-oracle" >>/etc/profile && \
     echo "export PATH=$PATH:$JAVA_HOME/bin:/opt/maven/bin/" >>/etc/profile   && \
     echo "export PATH=$PATH:$JAVA_HOME/bin:/opt/maven/bin/" >>/etc/environment && \
     . /etc/profile  && \ 
     . /etc/environment && \
     mkdir -p  /home/jenkins/agent /home/jenkins/.m2  /home/jenkins/.kube     /home/jenkins/.docker /root/.m2  /root/.kube  /root/.docker     /var/run/sshd  /var/log/supervisor&&\
     curl -sL https://deb.nodesource.com/setup_6.x | bash - &&\
     apt-get -y update &&\
     apt-get install -y -q sudo wget zip vim  unzip bzip2 git    redis-tools openssh-client openssh-server apt-transport-https    ca-certificates supervisor nodejs && \
     curl -SL http://archive.apache.org/dist/maven/maven-3/3.3.9/binaries/apache-maven-3.3.9-bin.tar.gz -o /tmp/apache-maven-3.3.9.tar.gz  &&\
     echo "516923b3955b6035ba6b0a5b031fbd8b /tmp/apache-maven-3.3.9.tar.gz" |    md5sum -c &&\
     tar xzf /tmp/apache-maven-3.3.9.tar.gz -C /opt/ &&\
     mv /opt/apache-maven-3.3.9 /opt/maven &&\
     ln -s /opt/maven/bin/mvn /usr/bin && \
     rm -f /tmp/apache-maven-3.3.9.tar.gz &&\
     curl -SL    https://storage.googleapis.com/kubernetes-release/release/v1.9.3/bin/linux/amd64/kubectl -o /usr/bin/kubectl  && \
     chmod +x /usr/bin/kubectl &&\
     curl -SLo /tmp/docker-17.03.2-ce.tgz   https://download.docker.com/linux/static/stable/x86_64/docker-17.03.2-ce.tgz && \
     tar xvf /tmp/docker-17.03.2-ce.tgz --exclude="*completion*"   --strip-components 1 -C /usr/bin &&\ 
     rm -rf /tmp/docker-17.03.2-ce.tgz &&\
     curl -L "https://cli.run.pivotal.io/stable?release=linux64-binary&source=github" | tar -zx &&\
     mv cf /usr/bin &&\
     curl -SL     https://github.infra.hana.ondemand.com/cloudfoundry/cf-cli-mta-plugin/releases/download/v0.6.0/mta_plugin_linux_amd64 -o     /tmp/mta_plugin_linux_amd64 &&\
     chmod +x /tmp/mta_plugin_linux_amd64 &&\
     cf install-plugin /tmp/mta_plugin_linux_amd64 -f &&\
     rm -rf /tmp/mta_plugin_linux_amd64 && \
     groupadd -g 10000 jenkins &&\
     useradd -m -d /home/jenkins/  -u 10000 -g 10000 jenkins &&\
     usermod -aG sudo jenkins &&\
     echo "%jenkins  ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers &&\
     echo "jenkins:jenkins" | chpasswd &&\
     chown -R jenkins:jenkins /home/jenkins &&\
     curl --create-dirs -sSLo /usr/share/jenkins/slave.jar    https://repo.jenkins-ci.org/public/org/jenkins-ci/main/remoting/3.17/remoting-3.17.jar && \
     chmod 755 /usr/share/jenkins &&\
     chmod 644 /usr/share/jenkins/slave.jar && \
     curl -SL  https://raw.githubusercontent.com/jenkinsci/docker-jnlp-slave/master/jenkins-slave -o  /usr/bin/jenkins-slave  &&\
     chmod +x /usr/bin/jenkins-slave && \
     npm install -g bower &&\
     npm install -g gulp  &&\
     npm install -g yarn && \
     rm -rf /var/lib/apt/lists/*  /var/cache/apt/archives/* && \
     rm -rf /var/cache/oracle-jdk8-installer  

ENV AGENT_WORKDIR=/home/jenkins/agent

ENV MAVEN_HOME /opt/maven
ENV MAVEN_CONFIG "/home/jenkins/.m2"
ENV JAVA_HOME=/usr/lib/jvm/java-8-oracle 
ENV PATH=${PATH}:${JAVA_HOME}/bin:/opt/maven/bin/
COPY .npmrc /home/jenkins/
COPY settings.xml /home/jenkins/.m2/
COPY supervisord.conf /etc/supervisor/supervisord.conf

ENTRYPOINT ["/usr/bin/supervisord"]
