#!/bin/bash
if [[ -f /hana/data/SID ]]; then 
    su - ${SID}adm
    HDB start
else
    /hana/shared/SAP_HANA_DATABASE/hdblcm --batch --action=install --components=all --sid=${SID} --number=${INSTANCE_NB}   -password=${PASSWORD} -sapadm_password=${PASSWORD}  -system_user_password=${PASSWORD}  --sapmnt=/hana/shared --datapath=/hana/data --logpath=/hana/log 
    echo ${SID} >/hana/data/SID
fi