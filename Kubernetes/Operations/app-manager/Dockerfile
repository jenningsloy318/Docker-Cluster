FROM ubuntu:16.04
RUN export HTTP_PROXY=http://proxy.wdf.sap.corp:8080 && export http_proxy=http://proxy.wdf.sap.corp:8080 &&export https_proxy=http://proxy.wdf.sap.corp:8080&& HTTPS_PROXY=http://proxy.wdf.sap.corp:8080&&apt-get update && apt-get install -y build-essential file curl  && curl -SLO https://github.com/emcrisostomo/fswatch/releases/download/1.9.3/fswatch-1.9.3.tar.gz &&  tar -xvzf fswatch-1.9.3.tar.gz && cd fswatch-1.9.3 &&  ./configure --prefix=/usr --sysconfdir=/etc && make && make install && ldconfig && cd ../ && rm -rf fswatch* &&  curl -SL https://storage.googleapis.com/kubernetes-release/release/v1.5.3/bin/linux/amd64/kubectl -o /usr/bin/kubectl && chmod +x /usr/bin/kubectl
COPY app-manager.sh /
CMD ["/app-manager.sh"]
