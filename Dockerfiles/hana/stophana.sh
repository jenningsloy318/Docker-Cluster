#!/bin/bash

SID=$(cat /hana/data/SID)
user=$(echo "${SID}adm"|awk '{print tolower($0)}')
group=$(echo "${SID}shm"|awk '{print tolower($0)}')
uid=$(cat /usr/sap/${SID}/${SID}.uid)
gid=$(cat /usr/sap/${SID}/${SID}.gid)
GID=$(cat /usr/sap/${SID}/${SID}.Gid)
groupadd -g ${gid} sapsys
groupadd -g ${GID} ${group}
useradd  -d /usr/sap/${SID}/home -u ${uid} -s /bin/sh  -g sapsys -G ${group}  ${user}
su - ${user} -c " source /usr/sap/${SID}/.profile && HDB stop"

