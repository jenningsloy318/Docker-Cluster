FROM docker.wdf.sap.corp:50000/hana/sles12-for-hana:latest

ARG HANA_SOURCE=http://moo-repo.wdf.sap.corp:8080/static/monsoon/hana/newdb/1.0.122_08/SAP_HANA_DATABASE100_122_08_Linux_on_x86_64.SAR 
ARG SAPCAR_SOURCE="http://moo-repo.wdf.sap.corp:8080/static/monsoon/hana/newdb/SAPCAR"
ARG HTTPS_PROXY=http://proxy.wdf.sap.corp:8080
ARG HTTP_PROXY=http://proxy.wdf.sap.corp:8080
ARG NO_PROXY=localhost,sap.corp,mo.sap.corp,cc.mo.sap.corp,sap.biz,cloud.sap,sap,cc.ondemand.com,moo-repo,moo-repo.wdf.sap.corp,repo,repo.wdf.sap.corp,169.254.169.254,127.0.0.1
COPY starthana.sh /usr/bin/
RUN curl -SL $SAPCAR_SOURCE -o /usr/bin/SAPCAR && \
    chmod +x /usr/bin/SAPCAR && \
    mkdir -p /hana/shared /hana/data  /hana/log &&  \ 
    curl -SL $HANA_SOURCE -o /hana/shared/SAP_HANA_DATABASE100_122_08_Linux_on_x86_64.SAR && \
    cd /hana/shared/ && \
    SAPCAR -xvf SAP_HANA_DATABASE100_122_08_Linux_on_x86_64.SAR   &&  \
    rm -f /hana/shared/*.SAR  && \ 
    curl -SLO https://bootstrap.pypa.io/get-pip.py && \ 
    python get-pip.py && \
    pip install supervisor ordered-startup-supervisord && \
    chmod +x /usr/bin/starthana.sh && \
    which supervisord

env SID ${SID:-SPO}
env INSTANCE_NB ${INSTANCE_NB:-00}
env PASSWORD ${INSTANCE_NB:-Toor1234}
CMD ["/usr/bin/supervisord]



