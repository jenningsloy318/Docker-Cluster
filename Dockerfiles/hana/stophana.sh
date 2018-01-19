#!/bin/bash

SID=$(cat /hana/data/SID)
user=$(echo "${SID}adm"|awk '{print tolower($0)}')
#group=$(echo "${SID}shm"|awk '{print tolower($0)}')
#uid=$(cat /usr/lmy/${SID}/${SID}.uid)
#gid=$(cat /usr/lmy/${SID}/${SID}.gid)
#GID=$(cat /usr/lmy/${SID}/${SID}.Gid)
#groupadd -g ${gid} lmysys
#groupadd -g ${GID} ${group}
#useradd  -d /usr/lmy/${SID}/home/ -u ${uid} -s /bin/sh  -g lmysys -G ${group}  ${user}
su - ${user} -c " source /usr/lmy/${SID}/home/.profile && HDB stop"

