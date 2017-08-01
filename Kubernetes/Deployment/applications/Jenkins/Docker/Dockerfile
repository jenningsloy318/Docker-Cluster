FROM jenkins/jenkins:lts
COPY install-ci-connect.sh /usr/local/bin
RUN apt -qq -y install maven && chmod +x /usr/local/bin/install-ci-connect.sh

