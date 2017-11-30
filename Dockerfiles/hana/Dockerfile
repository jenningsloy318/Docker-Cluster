FROM docker.wdf.sap.corp:50000/hana/sles12-for-hana:latest

ARG HANA_SOURCE=http://moo-repo.wdf.sap.corp:8080/static/monsoon/hana/newdb/1.0.122_08/SAP_HANA_DATABASE100_122_08_Linux_on_x86_64.SAR 
ARG SAPCAR_SOURCE="http://moo-repo.wdf.sap.corp:8080/static/monsoon/hana/newdb/SAPCAR"
ARG HTTPS_PROXY=http://proxy.wdf.sap.corp:8080
ARG HTTP_PROXY=http://proxy.wdf.sap.corp:8080
ARG NO_PROXY=localhost,sap.corp,mo.sap.corp,cc.mo.sap.corp,sap.biz,cloud.sap,sap,cc.ondemand.com,moo-repo,moo-repo.wdf.sap.corp,repo,repo.wdf.sap.corp,169.254.169.254,127.0.0.1
COPY starthana.sh /usr/bin/
COPY supervisord.conf /etc/
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
    mkdir /var/log/supervisor  

ENV SID ${SID:-SPO}
ENV INSTANCE_NB ${INSTANCE_NB:-00}
ENV PASSWORD ${PASSWORD:-Toor1234}
EXPOSE 3${INSTANCE_NB}15 3${INSTANCE_NB}17 3${INSTANCE_NB}18 3${INSTANCE_NB}26   3${INSTANCE_NB}28  3${INSTANCE_NB}30  3${INSTANCE_NB}31 3${INSTANCE_NB}32 43${INSTANCE_NB} 80${INSTANCE_NB} 5${INSTANCE_NB}13 5${INSTANCE_NB}14 5${INSTANCE_NB}15 5${INSTANCE_NB}16
ENTRYPOINT ["/usr/bin/supervisord"]



