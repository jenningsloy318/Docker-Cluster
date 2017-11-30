FROM docker.wdf.sap.corp:50000/hana/sles12-for-hana:latest

ARG HANA_SOURCE=http://moo-repo.wdf.sap.corp:8080/static/monsoon/hana/newdb/1.0.122_08/SAP_HANA_DATABASE100_122_08_Linux_on_x86_64.SAR 
ARG SAPCAR_SOURCE="http://moo-repo.wdf.sap.corp:8080/static/monsoon/hana/newdb/SAPCAR"
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



