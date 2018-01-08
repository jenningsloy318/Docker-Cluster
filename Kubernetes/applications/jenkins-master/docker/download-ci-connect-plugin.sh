#!/bin/bash
CI_CONNECT_URL=https://nexus.wdf.sap.corp:8443/nexus/content/repositories/build.milestones/com/sap/prd/jenkins/plugins/ci-connect/ci-connect/2.1.8/ci-connect-2.1.8.hpi
curl -SL ${CI_CONNECT_URL} -o ${JENKINS_HOME}/plugins/ci-connect.jpi
#sleep 1000
#curl -X POST    -H "Authorization: Basic YWRtaW46YWRtaW4=" http://localhost:8080/safeRestart