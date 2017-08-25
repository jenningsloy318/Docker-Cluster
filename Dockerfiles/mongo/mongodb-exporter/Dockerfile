FROM         registry.gcsc.sap.corp/base/debian:stretch

COPY mongodb_exporter-linux-amd64 /bin/mongodb_exporter

EXPOSE      9001
ENTRYPOINT  [ "/bin/mongodb_exporter" ]
