#!/usr/bin/env python3


from kubernetes.client import *
import json
from os import environ
from str2bool import str2bool
import requests
import argparse
import logging



def getCluserVersion(apiClient):
        Version=VersionApi(apiClient)
        log.info('Versio of kubernetes cluster is %s.\n'%Version.get_code().git_version)


if __name__ == "__main__":
        log = logging.getLogger('__name__')
        log.setLevel(logging.DEBUG)
        logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")

        # create a file handler
        FileHandler = logging.FileHandler('k8sOps.log')
        FileHandler.setLevel(logging.WARNING)
        FileHandler.setFormatter(logFormatter)
        # create a file handler
        ConsoleHandler = logging.StreamHandler()
        ConsoleHandler.setFormatter(logFormatter)
        # create a logging format

        # add the handlers to the logger
        log.addHandler(FileHandler)
        log.addHandler(ConsoleHandler)



        ###kubernetes client configuration
        log.info('Make sure the following environment variables are set before running this program:\n')

        log.info('KUBE_URL: API url of the kubernetes cluster.\n')
        log.info('KUBE_TOKEN: Bearer Tokeb to access kubernetes cluster.\n')
        log.info('KUBE_VERIFY_SSL: if verify the SSL when access kuberbetes cluster, True or False,\n')
        log.info('KUBE_SSL_CA_CERT_FILE: if KUBE_VERIFY_SSL is True, this env must be set.\n')


        kube_url=environ.get('KUBE_URL','NOTSET').strip()
        kube_token=environ.get('KUBE_TOKEN','NOTSET').strip()
        kube_verify_ssl=environ.get('KUBE_VERIFY_SSL','NOTSET').strip()
        kube_ssl_ca_cert_file=environ.get('KUBE_SSL_CA_CERT_FILE','NOTSET').strip()


        # Configs can be set in Configuration class directly

        configuration=Configuration()

        if   kube_url == 'NOTSET':
                log.error('Error: ENV KUBE_URL is not set')
                exit(1)
        else:
                configuration.host=kube_url

        if   kube_token == 'NOTSET':
                log.error('Error: ENV KUBE_TOKEN is not set')
                exit(1)
        else:
            configuration.api_key['authorization']=kube_token
            configuration.api_key_prefix['authorization']='Bearer'


        if   kube_verify_ssl =='NOTSET':
                log.error('Error: ENV KUBE_VERIFY_SSL is not set')
                exit(1)
        elif kube_verify_ssl.upper() not in ['TRUE','FALSE','NOTSET']:
                log.error('Error: KUBE_VERIFY_SSL is not corect, please set it to True or False')
                exit(1)
        elif str2bool(kube_verify_ssl):
                if kube_ssl_ca_cert_file =='NOTSET':
                    log.error('Error: ENV KUBE_VERIFY_SSL is set,but KUBE_SSL_CA_CERT_FILE is not set!')
                    exit(1)
                else:
                    configuration.verify_ssl=True
                    configuration.ssl_ca_cert=kube_ssl_ca_cert_file
        else:
            configuration.verify_ssl=False
            requests.packages.urllib3.disable_warnings()
        

        # define the different API group client
        apiClient=ApiClient(configuration)

        #get the version of the cluster.
        getCluserVersion(apiClient)

