#!/bin/bash
APP_PATH=${APP_PATH:-/data/kubernetes/manifests/applications}
CA_CERT=${CA_CERT:-/var/run/secrets/kubernetes.io/serviceaccount/ca.crt}
TOKEN=${TOKEN:-$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)}
APISERVER=${APISERVER:-https://10.96.0.1:443}
KUBECONF=${KUBECONF:-/kubeconfig}
if [ -f ${KUBECONF}  ]; then 
	ARGS="--kubeconfig=${KUBECONF}"
else
	ARGS="--certificate-authority=${CA_CERT} --token=${TOKEN}"
fi
/usr/bin/fswatch --event=Created --event=Updated  -r ${APP_PATH} |  while read file; 
do 
    echo -e "Ready to apply changes in ${file} at $(date +%Y-%m-%d:%H:%M:%S).\n"
     NS=$(grep "namespace:" ${file} |awk '{print $2}'|uniq)
    if [ "x${NS}" != "x" ];then
      kubectl ${ARGS} get ns ${NS}
      if [ $? !=0 ];then
         kubectl ${ARGS} create ns  ${NS}
      fi
      kubectl ${ARGS} apply -f ${file} -n ${NS}
    else
      kubectl ${ARGS} apply -f ${file}
    fi

    if [ $? -ne 0 ]  ; then 
	    echo -e "Apply changes in ${file} failed at $(date +%Y-%m-%d:%H:%M:%S).\n"
    else
	    echo -e "Apply changes in ${file} sucessfully at $(date +%Y-%m-%d:%H:%M:%S).\n"
    fi
done
