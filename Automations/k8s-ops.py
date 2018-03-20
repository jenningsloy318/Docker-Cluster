#!/usr/bin/env python3


from kubernetes.client import *
import json
from os import environ
from str2bool import str2bool
import  requests
import argparse





###kubernetes client configuration

print('Make sure the following environment variables are set before running this program:\n')

print('KUBE_URL: API url of the kubernetes cluster')
print('KUBE_TOKEN: Bearer Tokeb to access kubernetes cluster')
print('KUBE_VERIFY_SSL: if verify the SSL when access kuberbetes cluster, True or False')
print('KUBE_SSL_CA_CERT_FILE: if KUBE_VERIFY_SSL is True, this env must be set')
print('\n')


kube_url=environ.get('KUBE_URL','NOTSET').strip()
kube_token=environ.get('KUBE_TOKEN','NOTSET').strip()
kube_verify_ssl=environ.get('KUBE_VERIFY_SSL','NOTSET').strip()
kube_ssl_ca_cert_file=environ.get('KUBE_SSL_CA_CERT_FILE','NOTSET').strip()


# Configs can be set in Configuration class directly

configuration=Configuration()

if   kube_url == 'NOTSET':
        print('ENV KUBE_URL is not set')
        exit(1)
else:
        configuration.host=kube_url

if   kube_token == 'NOTSET':
        print('ENV KUBE_TOKEN is not set')
        exit(1)
else:
    configuration.api_key['authorization']=kube_token
    configuration.api_key_prefix['authorization']='Bearer'


if   kube_verify_ssl =='NOTSET':
        print('ENV KUBE_VERIFY_SSL is not set')
        exit(1)
elif kube_verify_ssl.upper() not in ['TRUE','FALSE','NOTSET']:
        print('KUBE_VERIFY_SSL is not corect, please set it to True or False')
        exit(1)
elif str2bool(kube_verify_ssl):
        if kube_ssl_ca_cert_file =='NOTSET':
            print('ENV KUBE_VERIFY_SSL is set,but KUBE_SSL_CA_CERT_FILE is not set!')
            exit(1)
        else:
            configuration.verify_ssl=True
            configuration.ssl_ca_cert=kube_ssl_ca_cert_file
else:
    configuration.verify_ssl=False
    requests.packages.urllib3.disable_warnings()
    

# define the different API group client
apiClient=ApiClient(configuration)
#coreV1Api=CoreV1Api(apiClient)
#extensionsV1beta1Api=ExtensionsV1beta1Api(apiClient)
Version=VersionApi(apiClient)
#
#
### list/get the objects in API instance
#
print(Version.get_code().git_version)
#print(coreV1Api.list_node(pretty=True).items)
#print(extensionsV1beta1Api.list_deployment_for_all_namespaces())


