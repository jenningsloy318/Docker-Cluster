FROM docker.wdf.sap.corp:50000/rhel:7.2_sap


ENV ARTIFACTIMPORTER_HOME /tools/artifactimporter/artifactimporter-0.8
ENV PATH /tools/artifactimporter/artifactimporter-0.8/bin:$PATH
ADD ssh/* /root/.ssh/
RUN mv /root/.ssh/SAPNetCA_G2.crt /etc/pki/ca-trust/source/anchors && \
    update-ca-trust extract &&  \
    yum -y upgrade nss  && \
    yum install unzip openssh-server -y && \
    mkdir -p /tools/artifactimporter && \
    curl "https://nexus.wdf.sap.corp:8443/nexus/service/local/repositories/deploy.milestones/content/com/sap/prd/commonrepo/artifactimporter/com.sap.prd.commonrepo.artifactimporter.dist.cli/0.8/com.sap.prd.commonrepo.artifactimporter.dist.cli-0.8.zip" -o /tools/artifactimporter/com.sap.prd.commonrepo.artifactimporter.dist.cli-0.8.zip && \
    unzip /tools/artifactimporter/com.sap.prd.commonrepo.artifactimporter.dist.cli-0.8.zip -d /tools/artifactimporter && \
    rm /tools/artifactimporter/com.sap.prd.commonrepo.artifactimporter.dist.cli-0.8.zip && \
    yum -y install java-1.7.0-openjdk.x86_64 java-1.7.0-openjdk-devel.x86_64; yum clean all && \
    echo "root:Toor1234"|chpasswd && ssh-keygen -A 


ENV PATH /usr/lib/jvm/java/jre/bin:$PATH
ENV JAVA_HOME /usr/lib/jvm/java/jre

VOLUME /gen
ADD tools/* /tools/
ADD certificates /tools/certificates

CMD ["/usr/sbin/sshd", "-D"]

