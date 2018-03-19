#!/usr/bin/env python3


from kubernetes.client import *

# Configs can be set in Configuration class directly
configuration=Configuration()
configuration.host='https://10.58.137.243:6443'
configuration.api_key['authorization']='yJnmXguRe0N4sXyPudnSxcyPSMIUKbFA'
configuration.api_key_prefix['authorization']='Bearer'
configuration.verify_ssl= True
configuration.ssl_ca_cert='ca.pem'
configuration.assert_hostname = False


# define the different API group client
apiClient=ApiClient(configuration)
coreV1Api=CoreV1Api(apiClient)
extensionsV1beta1Api=ExtensionsV1beta1Api(apiClient)
## list the objects in API instance


print(coreV1Api.list_node(pretty=True))
print(extensionsV1beta1Api.list_deployment_for_all_namespaces())


