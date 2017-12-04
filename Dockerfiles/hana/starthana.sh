#!/bin/bash
if [ -f /hana/data/SID ]; then 
    SID=$(cat /hana/data/SID)
    user=$(echo "${SID}adm"|awk '{print tolower($0)}')
    group=$(echo "${SID}shm"|awk '{print tolower($0)}')
    uid= $(cat /usr/sap/${SID}/${SID}.uid)
    gid=$(cat /usr/sap/${SID}/${SID}.gid)
    GID=$(cat /usr/sap/${SID}/${SID}.Gid)
    groupadd -g ${gid} sapsys
    groupadd -g ${GID} ${group}
    useradd  -d /usr/sap/${SID}/home -u ${uid} -s /bin/sh  -g sapsys -G ${group}  ${user}
    echo "export SID=${SID}" >>/etc/profile
    su - ${user} -c "  source /usr/sap/${SID}/home/.profile  &&    HDB start "

else
    /hana/shared/SAP_HANA_DATABASE/hdblcm --batch --action=install --components=all --sid=${SID} --number=${INSTANCE_NB}   -password=${PASSWORD} -sapadm_password=${PASSWORD}  -system_user_password=${PASSWORD}  --sapmnt=/hana/shared --datapath=/hana/data --logpath=/hana/log 
    echo ${SID} >/hana/data/SID
    echo "export SID=${SID}" >>/etc/profile
    user=$(echo "${SID}adm"|awk '{print tolower($0)}')
    su - ${user} -c " \
    id -u >/usr/sap/${SID}/${SID}.uid && \
    id -g >/usr/sap/${SID}/${SID}.gid && \
    id -G |awk '{print $2}'>/usr/sap/${SID}/${SID}.Gid && \
    chown ${user} /usr/sap/${SID}/${SID}.uid  /usr/sap/${SID}/${SID}.gid  /usr/sap/${SID}/${SID}.Gid"
 fi