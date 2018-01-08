## when we configure TLS for docker engine, client need to set following ENV 

1. DOCKER_CERT_PATH, defualt is ~/.docker, ca.pem,key.pem,cert.pem will be stored in this directory
2. DOCKER_HOST=tcp://$HOST:2376: set the endpoint of the docker engine
3.  DOCKER_TLS_VERIFY=1: enable the TLS verification
