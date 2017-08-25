FROM ubuntu:16.04
ARG DEBIAN_FRONTEND=noninteractive
ARG DEBCONF_NONINTERACTIVE_SEEN=true
ARG uid=1000
ARG gid=1000
ARG user=chisel
ARG group=chisel
ARG passwd=chisel 
ARG CHISEL_HOME=/home/chisel

RUN apt-get -y update && \
    apt-get install  --no-install-recommends -y ca-certificates curl supervisor   && \
    apt-get clean all &&  rm -rf /var/lib/apt/lists/* && \
    groupadd -g ${gid} ${group} &&\
    useradd -d "$CHISEL_HOME" -u ${uid} -g ${gid} -G sudo -m -s /bin/bash ${user} && \
    curl -SL https://github.infra.hana.ondemand.com/raw/cloudfoundry/chisel/master/bin/chisel_linux_amd64  -o /usr/bin/chisel &&\
    chmod +x /usr/bin/chisel
# `/usr/share/jenkins/ref/` contains all reference configuration we want 
# to set on a fresh new installation. Use it to bundle additional plugins 
# or config file with your custom jenkins Docker image.

COPY supervisord.conf /etc/
USER root

ENTRYPOINT ["/usr/bin/supervisord"]
