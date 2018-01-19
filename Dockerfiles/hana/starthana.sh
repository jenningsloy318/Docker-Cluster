#!/bin/bash
if [ -f /hana/data/SID ]; then 
    SID=$(cat /hana/data/SID)
    user=$(echo "${SID}adm"|awk '{print tolower($0)}')
    group=$(echo "${SID}shm"|awk '{print tolower($0)}')
    uid=$(cat /usr/lmy/${SID}/${SID}.uid)
    gid=$(cat /usr/lmy/${SID}/${SID}.gid)
    GID=$(cat /usr/lmy/${SID}/${SID}.Gid)

    groupadd -g ${gid} lmysys
    groupadd -g ${GID} ${group}
    useradd  -d /usr/lmy/${SID}/home -u ${uid} -s /bin/sh  -g lmysys -G ${group}  ${user}
    mkdir /run/uuidd  && uuidd
    mkdir /var/lib/hdb  && chown -R ${user} /var/lib/hdb 
    echo root:$PASSWORD | chpasswd
    echo "export SID=${SID}" >>/etc/profile
    su - ${user} -c "  source /usr/lmy/${SID}/home/.profile  &&    HDB start "

else
    /mnt/SAP_HANA_DATABASE/hdblcm --batch --action=install --components=all --sid=${SID} --number=${INSTANCE_NB}   -password=${PASSWORD} -lmyadm_password=${PASSWORD}  -system_user_password=${PASSWORD}  --lmymnt=/hana/shared --datapath=/hana/data --logpath=/hana/log 
    echo root:$PASSWORD | chpasswd
    echo ${SID} >/hana/data/SID
    echo "export SID=${SID}" >>/etc/profile
    user=$(echo "${SID}adm"|awk '{print tolower($0)}')
    su - ${user} -c " \
    id -u >/usr/lmy/${SID}/${SID}.uid && \
    id -g >/usr/lmy/${SID}/${SID}.gid && \
    id -G |cut -d ' ' -f 2 >/usr/lmy/${SID}/${SID}.Gid && \
    chown ${user} /usr/lmy/${SID}/${SID}.uid  /usr/lmy/${SID}/${SID}.gid  /usr/lmy/${SID}/${SID}.Gid"
 fi