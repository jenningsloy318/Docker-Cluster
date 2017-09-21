FROM registry.gcsc.sap.corp/base/debian:stretch




# Fluent Bit version

ENV REDIS_EXPORTER_VERSION 0.12.2
ENV REDIS_EXPORTER_URL https://github.com/oliver006/redis_exporter/releases/download/v${REDIS_EXPORTER_VERSION}/redis_exporter-v${REDIS_EXPORTER_VERSION}.linux-amd64.tar.gz

ARG HTTPS_PROXY=http://proxy.pvgl.sap.corp:8080
ARG HTTP_PROXY=http://proxy.pvgl.sap.corp:8080
ARG https_proxy=http://proxy.pvgl.sap.corp:8080
ARG http_proxy=http://proxy.pvgl.sap.corp:8080
RUN apt update && apt install curl -y \
    && curl -SL -o "/tmp/redis_exporter-v${REDIS_EXPORTER_VERSION}.linux-amd64.tar.gz" ${REDIS_EXPORTER_URL} \
    && cd /tmp \
    && tar xvf "redis_exporter-v${REDIS_EXPORTER_VERSION}.linux-amd64.tar.gz"  -C  /usr/bin


# Configuration files


# Entry point
CMD ["/usr/bin/redis_exporter"]
