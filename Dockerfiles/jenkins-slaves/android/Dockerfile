FROM registry.gcsc.sap.corp/nodejs/maven3-nodejs:1.0.0

MAINTAINER David Lin(I326996)

RUN mkdir -p /opt/android &&\
    wget https://dl.google.com/android/repository/sdk-tools-linux-3859397.zip &&\
    unzip -d /opt/android sdk-tools-linux-3859397.zip &&\
    mkdir -p /opt/gradle &&\
    wget https://services.gradle.org/distributions/gradle-2.14.1-bin.zip &&\
    unzip -d /opt/gradle gradle-2.14.1-bin.zip &&\
    echo "JAVA_HOME=/srv/java/jdk" > /etc/environment &&\
    echo "GIT_SSL_NO_VERIFY=1" >> /etc/environment &&\
    echo "ANDROID_HOME=/opt/android" >> /etc/environment &&\
    echo "GRADLE_HOME=/opt/gradle/gradle-2.14.1" >> /etc/environment &&\
    echo "PATH=${PATH}:/srv/java/jdk/bin:/srv/java:/opt/android/tools/bin:/opt/gradle/gradle-2.14.1/bin" >> /etc/environment &&\
    . /etc/environment &&\
    yes | /opt/android/tools/bin/sdkmanager --no_https --proxy=http --proxy_host=proxy.wdf.sap.corp --proxy_port=8080 --licenses &&\
    touch /root/.android/repositories.cfg &&\
    /opt/android/tools/bin/sdkmanager --no_https --proxy=http --proxy_host=proxy.wdf.sap.corp --proxy_port=8080 \
    "platform-tools" "platforms;android-27" "platforms;android-26" "platforms;android-25" "platforms;android-23" \
    "tools" "build-tools;23.0.1" "build-tools;25.0.1" "build-tools;25.0.2" "build-tools;26.0.1" "build-tools;27.0.3" \
    "extras;android;m2repository" &&\
    apt-get install lib32stdc++6 lib32z1 python3 python3-pip -y

CMD ["/usr/sbin/sshd", "-D"]
