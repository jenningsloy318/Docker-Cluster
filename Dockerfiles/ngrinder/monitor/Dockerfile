FROM jeanblanchard/java:serverjre-8
MAINTAINER JunHo Yoon "junoyoon@gmail.com"

RUN apk update; apk add curl bash


# Set up environment variables
ENV BASE_DIR=/opt \
    NGRINDER_MONITOR_BASE=/opt/ngrinder-monitor \
    NGRINDER_MONITOR_HOME=/opt/ngrinder-monitor/.ngrinder-monitor

VOLUME $NGRINDER_MONITOR_BASE

# Copy initial execution script
ADD scripts /scripts

# Excution
ENTRYPOINT ["/scripts/run.sh"]