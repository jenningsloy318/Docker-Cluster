FROM registry.gcsc.sap.corp/base/debian:stretch




# Fluent Bit version
ENV FLB_MAJOR 0
ENV FLB_MINOR 12
ENV FLB_PATCH 1
ENV FLB_VERSION 0.12.1

ENV FLB_TARBALL https://github.com/fluent/fluent-bit/archive/v${FLB_VERSION}.zip

RUN mkdir -p /fluent-bit/bin /fluent-bit/etc /fluent-bit/log /fluent-bit/db
ARG HTTPS_PROXY=http://proxy.pvgl.sap.corp:8080
ARG HTTP_PROXY=http://proxy.pvgl.sap.corp:8080
ARG https_proxy=http://proxy.pvgl.sap.corp:8080
ARG http_proxy=http://proxy.pvgl.sap.corp:8080
RUN apt-get  update   \
    && apt-get install -y \
       ca-certificates \
       build-essential \
       cmake \
       make \
       sudo \
       wget \
       unzip \
       libsystemd-dev \
       procps\
       curl \
       bash\
    && apt-get install -y --no-install-recommends  -qq --reinstall lsb-base lsb-release \
    && curl -SL -o "/tmp/fluent-bit-${FLB_VERSION}.zip" ${FLB_TARBALL} \
    && cd /tmp && unzip "fluent-bit-${FLB_VERSION}.zip" \
    && cd "fluent-bit-${FLB_VERSION}"/build/ \
    && cmake -DFLB_DEBUG=On -DFLB_TRACE=On -DFLB_JEMALLOC=On -DFLB_BUFFERING=On ../ \
    && make \
    && install bin/fluent-bit /fluent-bit/bin/ \
    && apt-get remove --purge --auto-remove -y -qq \
       build-essential \
       cmake \
       make \
       wget \
       unzip \
       libsystemd-dev \
    && rm -rf /tmp/*

# Configuration files
COPY fluent-bit.conf /fluent-bit/etc/


# Entry point
CMD ["/fluent-bit/bin/fluent-bit", "-c", "/fluent-bit/etc/fluent-bit.conf","--verbose"]
