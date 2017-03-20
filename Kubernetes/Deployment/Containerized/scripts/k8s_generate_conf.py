#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Jennings Liu@ 2017-02-18 11:58:44

import argparse
import sys
import configparser
import re
from pathlib import Path
import subprocess


def create_etcd_cluster_conf(hostIP,name,etcd_dir_root,endpoints,conf_file):
    etcd_datadir=etcd_dir_root+'/data'
    etcd_conf_content=open(conf_file,'w')
    etcd_conf_content.write("name: '%s'\n"%name)
    etcd_conf_content.write("data-dir: %s\n"%etcd_datadir)
    etcd_conf_content.write("initial-cluster: %s\n"%','.join(endpoints))
    etcd_conf_content.write("initial-advertise-peer-urls: http://%s:2380\n"%hostIP)
    etcd_conf_content.write("initial-cluster-token: etcd-cluster\n")
    etcd_conf_content.write("initial-cluster-state: new\n")
    etcd_conf_content.write("listen-peer-urls: http://%s:2380\n"%hostIP)
    etcd_conf_content.write("listen-client-urls: http://0.0.0.0:2379\n")
    etcd_conf_content.write("advertise-client-urls: http://%s:2379\n"%hostIP)
    etcd_conf_content.flush()
    etcd_conf_content.close()

def create_etcd_cluster_proxy_conf(endpoints,conf):
    etcd_proxy_conf_content=open(conf,'w')
    etcd_proxy_conf_content.write("proxy: 'on'\n")
    etcd_proxy_conf_content.write("listen-client-urls: http://0.0.0.0:2379\n")
    etcd_proxy_conf_content.write("initial-cluster: %s\n"%','.join(endpoints))
    etcd_proxy_conf_content.write("advertise-client-urls:  http://0.0.0.0:2379\n")
    etcd_proxy_conf_content.flush()
    etcd_proxy_conf_content.close()


def create_single_etcd_conf(hostIP,etcd_dir_root,conf_file):
    etcd_datadir=etcd_dir_root+'/data'
    etcd_conf_content=open(conf_file,'w')
    etcd_conf_content.write("name: 'default'\n")
    etcd_conf_content.write("data-dir: %s\n"%etcd_datadir)
    etcd_conf_content.write("initial-cluster: default=http://%s:2380\n"%hostIP)
    etcd_conf_content.write("initial-advertise-peer-urls: http://%s:2380\n"%hostIP)
    etcd_conf_content.write("initial-cluster-token: etcd-cluster\n")
    etcd_conf_content.write("initial-cluster-state: new\n")
    etcd_conf_content.write("listen-peer-urls: http://%s:2380\n"%hostIP)
    etcd_conf_content.write("listen-client-urls: http://0.0.0.0:2379\n")
    etcd_conf_content.write("advertise-client-urls: http://%s:2379\n"%hostIP)
    etcd_conf_content.flush()
    etcd_conf_content.close()

def create_file_from_template(values_dict,Template_file_basedir,Template_file_name,Target_file_basedir,Target_file_name):
    print('Starting to create %s  to %s.\n'%(Target_file_name,Target_file_basedir))
    from jinja2 import Environment,FileSystemLoader
    template_file_path=Template_file_basedir+Template_file_name

    target_file_path=Target_file_basedir+Target_file_name
    target_dir_path=Path(Target_file_basedir)

    ##create dirs
    if not target_dir_path.exists():
        target_dir_path.mkdir(parents=True)

    ##initial the jinja2 templates
    Target_file_template_env = Environment(loader=FileSystemLoader(Template_file_basedir))
    Target_file_tepmlate = Target_file_template_env.get_template(Template_file_name)

    ##render  the file with jinja2 template
    with open(target_file_path,'w') as target_file:
        target_file.write(Target_file_tepmlate.render(values_dict))
    target_file.close()




if __name__ == '__main__':
##print parameterstarget_file
    arguments = argparse.ArgumentParser()
    arguments.add_argument("-c","--config",nargs="?",help="k8s deployment conf file",required=True)
    if len(sys.argv) ==1:
        arguments.print_help()
        sys.exit(1)
    args = arguments.parse_args()
    config_file=args.config


##process the config file

    config = configparser.ConfigParser()
    config_content=open(config_file)
    config.read_file(config_content)
    DEPLOY_MODE=config['main']['mode']
    POD_CIDR=config['main']['pod_CIDR']
    SVC_CIDR=config['main']['svc_CIDR']
    K8S_VER=config['main']['k8s_version']
    ETCD_VER=config['main']['etcd_version']
    DOCKER_ENGINE_VER=config['main']['docker_engine_ver']
    DOCKER_ENGINE_PROXY=config['main']['docker_engine_proxy']
    DOCKER_ENGINE_NOPROXY=config['main']['docker_engine_no_proxy']
    CLUSTER_DNS=config['main']['cluster_dns']
    CLUSTER_DOMAIN=config['main']['cluster_domain']
    TEMP_LOCAT_ROOT=config['main']['temp_local_root']+'/'
    K8S_DIR_ROOT=config['main']['k8s_dir_root']+'/'
    ETCD_DIR_ROOT=config['main']['etcd_dir_root']+'/'
    ADMIN_CONF=config['main']['admin-conf']
    KUBELET_CONF=config['main']['kubelet-conf']
    KUBE_PROXY_CONF=config['main']['kube-proxy-conf']
    CREATE_SELF_CA=config['main'].getboolean('create_self_ca')
    OPENSSL_APISERVERS_CONF=config['main']['openssl-apiservers-conf']
    OPENSSL_WORKERS_CONF=config['main']['openssl-workers-conf']
    config_content.close()


    ETCD_DATA_DIR=ETCD_DIR_ROOT+'data/'
    ETCD_CONF_DIR=ETCD_DIR_ROOT+'conf/'

    K8S_CONF_DIR=K8S_DIR_ROOT+'conf/'
    K8S_CERT_DIR=K8S_DIR_ROOT+'certs/'
    K8S_MANIFESTS_DIR=K8S_DIR_ROOT+'manifests/'
    K8S_SHELL_DIR=K8S_DIR_ROOT+'shell/'

    K8S_ADMIN_CONF=K8S_CONF_DIR+ADMIN_CONF
    K8S_KUBELET_CONF=K8S_CONF_DIR+KUBELET_CONF
    K8S_KUBE_PROXY_CONF=K8S_CONF_DIR+KUBE_PROXY_CONF

    TEMP_LOCAL_ETCD_CONF_DIR=TEMP_LOCAT_ROOT+('/').join(ETCD_CONF_DIR.split('/')[1:])
    TEMP_LOCAL_ETCD_DATA_DIR=TEMP_LOCAT_ROOT+('/').join(ETCD_DATA_DIR.split('/')[1:])

    TEMP_LOCAL_K8S_CONF_DIR=TEMP_LOCAT_ROOT+('/').join(K8S_CONF_DIR.split('/')[1:])
    TEMP_LOCAL_K8S_CERT_DIR=TEMP_LOCAT_ROOT+('/').join(K8S_CERT_DIR.split('/')[1:])
    TEMP_LOCAL_K8S_MANIFESTS_DIR=TEMP_LOCAT_ROOT+('/').join(K8S_MANIFESTS_DIR.split('/')[1:])
    TEMP_LOCAL_K8S_SHELL_DIR=TEMP_LOCAT_ROOT+('/').join(K8S_SHELL_DIR.split('/')[1:])

    TEMP_LOCAL_K8S_CONF_ADMIN=TEMP_LOCAL_K8S_CONF_DIR+ADMIN_CONF
    TEMP_LOCAL_K8S_CONF_KUBELET=TEMP_LOCAL_K8S_CONF_DIR+KUBELET_CONF
    TEMP_LOCAL_K8S_CONF_KUBE_PROXY=TEMP_LOCAL_K8S_CONF_DIR+KUBE_PROXY_CONF



##define global vars

    MASTER_NODES_ADDR=[]
    MASTER_NODES_DNS=[]

    LB_NODES_ADDR=[]
    LB_NODES_DNS=[]

    ALL_MASTER_NODES_ADDR=[]
    ALL_MASTER_NODES_DNS=[]


    WORKER_NODES_ADDR=[]
    WORKER_NODES_DNS=[]


    etcd_cluster_peer_endpoints=[]
    etcd_cluster_client_endpoints=[]
##create cluster conf

##ALL_MASTER_ITEMS including master IP and DNS dict items
    ALL_MASTER_ITEMS={}
    for key in config.options(DEPLOY_MODE):
        ALL_MASTER_ITEMS[key]=config.get(DEPLOY_MODE,key)

##extract the master nodes
    master_addr_re=re.compile(r'^master.*_addr$')
    master_dns_re=re.compile(r'^master.*_dns$')
    lb_addr_re=re.compile(r'^loadbalance.*addr$')
    lb_dns_re=re.compile(r'^loadbalance.*dns$')
    if DEPLOY_MODE =='multiple':
        for key in ALL_MASTER_ITEMS.keys():
            if master_addr_re.search(key):
                MASTER_NODES_ADDR.append(ALL_MASTER_ITEMS[key])
            elif master_dns_re.search(key):
                MASTER_NODES_DNS.append(ALL_MASTER_ITEMS[key])
            elif lb_addr_re.search(key):
                LB_NODES_ADDR.append(ALL_MASTER_ITEMS[key])
            elif lb_dns_re.search(key):
                LB_NODES_DNS.append(ALL_MASTER_ITEMS[key])
            else:
                continue
        ALL_MASTER_NODES_ADDR=MASTER_NODES_ADDR+LB_NODES_ADDR
        ALL_MASTER_NODES_DNS=MASTER_NODES_DNS+LB_NODES_DNS

    else:
        for key in ALL_MASTER_ITEMS.keys():
            if master_addr_re.search(key):
                MASTER_NODES_ADDR.append(ALL_MASTER_ITEMS[key])
            else:
                MASTER_NODES_DNS.append(ALL_MASTER_ITEMS[key])
        ALL_MASTER_NODES_ADDR=MASTER_NODES_ADDR
        ALL_MASTER_NODES_DNS=MASTER_NODES_DNS
##extract worker nodes
    ALL_WORKER_ITEMS={}
    for key in config.options('worker_nodes'):
        ALL_WORKER_ITEMS[key]=config.get('worker_nodes',key)

    worker_addr_re=re.compile(r'.*_addr$')
    worker_dns_re=re.compile(r'.*_dns$')

    for key in ALL_WORKER_ITEMS.keys():
        if worker_addr_re.search(key):
            WORKER_NODES_ADDR.append(ALL_WORKER_ITEMS[key])
        else:
            WORKER_NODES_DNS.append(ALL_WORKER_ITEMS[key])

##define etcd endpoints
    if DEPLOY_MODE =='multiple':
        for index,host in enumerate(MASTER_NODES_ADDR):
            etcd_cluster_peer_endpoints.append(''.join(['etcd',str(index),'=http://',host,':2380']))
            etcd_cluster_client_endpoints.append(''.join(['http://',host,':2379']))

    else:
        etcd_cluster_peer_endpoints=''.join(['default','=http://',MASTER_NODES_ADDR[0],':2380'])
        etcd_cluster_client_endpoints=''.join(['http://',MASTER_NODES_ADDR[0],':2379'])



        ##create both member and proxy conf
    if DEPLOY_MODE =='multiple':
        ##Create main etcd cluster conf
        print('This is multiple deployment, begin to creating etcd cluster conf.\n')
        for index,host in enumerate(MASTER_NODES_ADDR):
            print('Staring to create etcd cluster member (%s) conf \n'%host)
            etcd_cluster_conf=TEMP_LOCAT_ROOT+'/'+host+'/'+ETCD_CONF_DIR+'/etcd.conf'
            etcd_cluster_conf_path=Path(('/').join(etcd_cluster_conf.split('/')[:-1]))
            etcd_cluster_node_name='etcd'+str(index)
            if not etcd_cluster_conf_path.exists():
                etcd_cluster_conf_path.mkdir(parents=True)
            create_etcd_cluster_conf(host,etcd_cluster_node_name,ETCD_DIR_ROOT,etcd_cluster_peer_endpoints,etcd_cluster_conf)
    else:
        ##create single etcd conf
        print('This is single deployment, begin to creating etcd   conf.\n')
        print('Staring to create etcd conf for %s.\n'%MASTER_NODES_ADDR[0])
        for host in MASTER_NODES_ADDR:
            etcd_conf=TEMP_LOCAT_ROOT+'/'+host+'/'+ETCD_CONF_DIR+'/etcd.conf'
            etcd_conf_path=Path(('/').join(etcd_conf.split('/')[:-1]))
        if not etcd_conf_path.exists():
            etcd_conf_path.mkdir(parents=True)
        create_single_etcd_conf(host,ETCD_DIR_ROOT,etcd_conf)


### create openssl.conf in certs folder
    if MASTER_NODES_ADDR or MASTER_NODES_DNS:
        print('Starting to generate openssl conf  for signing apiservers.\n')
        SVC_IP=SVC_CIDR.split('/')[0].replace('0.0','0.1')
        APISERVERS_IPs=[SVC_IP]
        APISERVERS_DNSs=['kubernetes','kubernetes.default','kubernetes.default.svc','kubernetes.default.svc.'+CLUSTER_DOMAIN]

        APISERVERS_IPs.extend(MASTER_NODES_ADDR)
        APISERVERS_DNSs.extend(MASTER_NODES_DNS)

        openssl_conf_values_dict={'IPs':APISERVERS_IPs,'DNSs':APISERVERS_DNSs}

        Template_dir='./templates/certs/'
        Template_file='openssl.conf.jinja2'
        Target_dir=TEMP_LOCAL_K8S_CERT_DIR
        Target_file=OPENSSL_APISERVERS_CONF
        create_file_from_template(openssl_conf_values_dict,Template_dir,Template_file,Target_dir,Target_file)

    if WORKER_NODES_ADDR or WORKER_NODES_DNS:
        print('Starting to generate openssl conf  for signing worker nodes.\n')

        openssl_conf_values_dict={'IPs':WORKER_NODES_ADDR,'DNSs':WORKER_NODES_DNS}

        Template_dir='./templates/certs/'
        Template_file='openssl.conf.jinja2'
        Target_dir=TEMP_LOCAL_K8S_CERT_DIR
        Target_file=OPENSSL_WORKERS_CONF
        create_file_from_template(openssl_conf_values_dict,Template_dir,Template_file,Target_dir,Target_file)

### modify k8s pod files

    ##creating kube-apiserver.yaml
    print('Generating kube-apiserver.yaml.\n')
    Template_dir='./templates/manifests/'
    Template_file='kube-apiserver.yaml.jinja2'
    Target_dir=TEMP_LOCAL_K8S_MANIFESTS_DIR
    Target_file='kube-apiserver.yaml'
    apiserver_dict={'SVC_CIDR':SVC_CIDR,'K8S_VER':K8S_VER}
    create_file_from_template(apiserver_dict,Template_dir,Template_file,Target_dir,Target_file)

    ##creating kube-controller-manager.yaml
    print('Generating kube-controller-manager.yaml.\n')
    Template_dir='./templates/manifests/'
    Template_file='kube-controller-manager.yaml.jinja2'
    Target_dir=TEMP_LOCAL_K8S_MANIFESTS_DIR
    Target_file='kube-controller-manager.yaml'
    KUBECONFIG=K8S_ADMIN_CONF
    controller_manager_dict={'POD_CIDR':POD_CIDR,'K8S_VER':K8S_VER,'KUBECONFIG':KUBECONFIG}
    create_file_from_template(controller_manager_dict,Template_dir,Template_file,Target_dir,Target_file)

    ##creating kube-scheduler.yaml
    print('Generating kube-scheduler.yaml.\n')
    Template_dir='./templates/manifests/'
    Template_file='kube-scheduler.yaml.jinja2'
    Target_dir=TEMP_LOCAL_K8S_MANIFESTS_DIR
    Target_file='kube-scheduler.yaml'
    KUBECONFIG=K8S_ADMIN_CONF
    scheduler_dict={'POD_CIDR':POD_CIDR,'K8S_VER':K8S_VER,'KUBECONFIG':KUBECONFIG}
    create_file_from_template(scheduler_dict,Template_dir,Template_file,Target_dir,Target_file)

    ##creating kube-proxy.yaml
    print('Generating kube-proxy.yaml.\n')
    Template_dir='./templates/manifests/'
    Template_file='kube-proxy.yaml.jinja2'
    Target_dir=TEMP_LOCAL_K8S_MANIFESTS_DIR
    Target_file='kube-proxy.yaml'
    KUBECONFIG=K8S_KUBE_PROXY_CONF
    proxy_dict={'POD_CIDR':POD_CIDR,'KUBECONFIG':KUBECONFIG}
    create_file_from_template(proxy_dict,Template_dir,Template_file,Target_dir,Target_file)

    ##creating etcd.yaml
    print('Generating etcd.yaml.\n')
    Template_dir='./templates/manifests/'
    Template_file='etcd.yaml.jinja2'
    Target_dir=TEMP_LOCAL_K8S_MANIFESTS_DIR
    Target_file='etcd.yaml'
    ETCDE_CONF=ETCD_DIR_ROOT+'conf/etcd.conf'
    etcd_dict={'ETCD_VER':ETCD_VER,'ETCDE_CONF':ETCDE_CONF}
    create_file_from_template(etcd_dict,Template_dir,Template_file,Target_dir,Target_file)

    ##creating calico.yaml
    print('Generating calico.yaml.\n')
    Template_dir='./templates/manifests/'
    Template_file='calico.yaml.jinja2'
    Target_dir=TEMP_LOCAL_K8S_MANIFESTS_DIR
    Target_file='calico.yaml'
    ETCD_CLUSTER_CLIENT_ENDPOINTS=etcd_cluster_client_endpoints
    calico_dict={'ETCD_CLUSTER_CLIENT_ENDPOINTS':ETCD_CLUSTER_CLIENT_ENDPOINTS,'POD_CIDR':POD_CIDR}
    create_file_from_template(calico_dict,Template_dir,Template_file,Target_dir,Target_file)



    ##creating kube-dns.yaml
    print('Generating kube-dns.yaml.\n')
    Template_dir='./templates/manifests/'
    Template_file='kube-dns.yaml.jinja2'
    Target_dir=TEMP_LOCAL_K8S_MANIFESTS_DIR
    Target_file='kube-dns.yaml'
    kube_dns_dict={'CLUSTER_DNS':CLUSTER_DNS,'CLUSTER_DOMAIN':CLUSTER_DOMAIN}
    create_file_from_template(kube_dns_dict,Template_dir,Template_file,Target_dir,Target_file)




### modify kubelet.service
    print('Generating kubelet.service file.\n')
    Template_dir='./templates/init/'
    Template_file='kubelet.service.jinja2'
    Target_dir=TEMP_LOCAT_ROOT+'lib/systemd/system/'
    Target_file='kubelet.service'
    KUBECONFIG=K8S_KUBELET_CONF
    kubelet_service_dict={'CLUSTER_DNS':CLUSTER_DNS,'CLUSTER_DOMAIN':CLUSTER_DOMAIN,'KUBECONFIG':KUBECONFIG}
    create_file_from_template(kubelet_service_dict,Template_dir,Template_file,Target_dir,Target_file)




    print('Generating docker.service.\n')
    Template_dir='./templates/init/'
    Template_file='docker.service.jinja2'
    Target_dir=TEMP_LOCAT_ROOT+'lib/systemd/system/'
    Target_file='docker.service'
    docker_service_dict={'DOCKER_ENGINE_PROXY':DOCKER_ENGINE_PROXY,'DOCKER_ENGINE_NOPROXY':DOCKER_ENGINE_NOPROXY}
    create_file_from_template(docker_service_dict,Template_dir,Template_file,Target_dir,Target_file)



###modify shell scripts

    print('generating get_k8s_server_bin.sh.\n')
    Template_dir='./templates/shell/'
    Template_file='get_k8s_server_bin.sh.jinja2'
    Target_dir=TEMP_LOCAL_K8S_SHELL_DIR
    Target_file='get_k8s_server_bin.sh'
    shell_get_k8s_server_bin_dict={'K8S_VER':K8S_VER}
    create_file_from_template(shell_get_k8s_server_bin_dict,Template_dir,Template_file,Target_dir,Target_file)

    print('generating k8s_install_docker_engine.\n')
    Template_dir='./templates/shell/'
    Template_file='k8s_install_docker_engine.sh.jinja2'
    Target_dir=TEMP_LOCAL_K8S_SHELL_DIR
    Target_file='k8s_install_docker_engine.sh'
    shell_install_docker_engine_dict={'DOCKER_ENGINE_VER':DOCKER_ENGINE_VER}
    create_file_from_template(shell_install_docker_engine_dict,Template_dir,Template_file,Target_dir,Target_file)



    if DEPLOY_MODE =='multiple':
        print('This is multiple deployment, begin to generate loadbalance nginx conf.\n')
        Template_dir='./templates/conf/'
        Template_file='nginx.conf.jinja2'
        Target_dir=TEMP_LOCAT_ROOT+'etc/ningx/'
        Target_file='nginx.conf'
        nginx_conf_dict={'INCLUDE':'include /etc/nginx/sites_tcp_conf.d/*;'}
        create_file_from_template(nginx_conf_dict,Template_dir,Template_file,Target_dir,Target_file)

        print('Generating apiserver-proxy.conf, which will be placed at /etc/nginx/sites_tcp_conf.d/* on %s.\n'%LB_NODES_ADDR)
        Template_dir='./templates/conf/'
        Template_file='apiserver-proxy.conf.jinja2'
        Target_dir=TEMP_LOCAT_ROOT+'etc/ningx/sites_tcp_conf.d/'
        Target_file='nginx.conf'
        apiserver_proxy_conf_template={'INCLUDE':'include /etc/nginx/sites_tcp_conf.d/*;'}
        create_file_from_template(apiserver_proxy_conf_template,Template_dir,Template_file,Target_dir,Target_file)


    if CREATE_SELF_CA:
        print('Begin to generate self sing CA keys .\n')


        print('Generating ssl keys in %s.\n'%TEMP_LOCAL_K8S_CERT_DIR)

        print('Creating self CA key in %s.\n'%TEMP_LOCAL_K8S_CERT_DIR)
        CMD_CREATE_CA_KEY='openssl genrsa -out ca-key.pem 2048'
        print(bytes.decode(subprocess.Popen(CMD_CREATE_CA_KEY, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,cwd=TEMP_LOCAL_K8S_CERT_DIR).communicate()[0]))

        print('creating CA self-signed cert in %s.\n'%TEMP_LOCAL_K8S_CERT_DIR)
        CMD_CREATE_SELF_CA_CERT='openssl req -x509 -new -nodes -key ca-key.pem -days 10000 -out ca.pem -subj "/CN=k8s-ca"'
        print(bytes.decode(subprocess.Popen(CMD_CREATE_SELF_CA_CERT, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,cwd=TEMP_LOCAL_K8S_CERT_DIR).communicate()[0]))

        print('creating apiserver priviate key in %s.\n'%TEMP_LOCAL_K8S_CERT_DIR)
        CMD_CREATE_APISERVER_KEY='openssl genrsa -out apiserver-key.pem 2048'
        print(bytes.decode(subprocess.Popen(CMD_CREATE_APISERVER_KEY, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,cwd=TEMP_LOCAL_K8S_CERT_DIR).communicate()[0]))

        print('creating apiserver sign request in %s.\n'%TEMP_LOCAL_K8S_CERT_DIR)
        CMD_CREATE_APISERVER_SIGN_REQ='openssl req -new -key apiserver-key.pem -out apiserver.csr -subj "/CN=k8s-master" -config '+OPENSSL_APISERVERS_CONF
        print(bytes.decode(subprocess.Popen(CMD_CREATE_APISERVER_SIGN_REQ, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,cwd=TEMP_LOCAL_K8S_CERT_DIR).communicate()[0]))

        print('creating apiserver self-sign cert in %s.\n'%TEMP_LOCAL_K8S_CERT_DIR)
        CMD_CREATE_APISERVER_CERT='openssl x509 -req -in apiserver.csr -CA ca.pem -CAkey ca-key.pem -CAcreateserial -out apiserver.pem -days 365  -extfile '+OPENSSL_APISERVERS_CONF
        print(bytes.decode(subprocess.Popen(CMD_CREATE_APISERVER_CERT, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,cwd=TEMP_LOCAL_K8S_CERT_DIR).communicate()[0]))

        print('Creating admin ssl keys in %s.\n'%TEMP_LOCAL_K8S_CERT_DIR)

        print('Creating admin keys in %s.\n'%TEMP_LOCAL_K8S_CERT_DIR)
        CMD_CREATE_ADMIN_KEY='openssl genrsa -out admin-key.pem 2048'
        print(bytes.decode(subprocess.Popen(CMD_CREATE_ADMIN_KEY, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,cwd=TEMP_LOCAL_K8S_CERT_DIR).communicate()[0]))

        print('Creating admin sign request in %s.\n'%TEMP_LOCAL_K8S_CERT_DIR)
        CMD_CREATE_ADMIN_REQ='openssl req -new -key admin-key.pem -out admin.csr -subj "/O=system:masters/CN=admin"'
        print(bytes.decode(subprocess.Popen(CMD_CREATE_ADMIN_REQ, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,cwd=TEMP_LOCAL_K8S_CERT_DIR).communicate()[0]))

        print('creating admin self-sign cert in %s.\n'%TEMP_LOCAL_K8S_CERT_DIR)
        CMD_CREATE_APISERVER_CERT='openssl x509 -req -in admin.csr -CA ca.pem -CAkey ca-key.pem -CAcreateserial -out admin.pem -days 365'
        print(bytes.decode(subprocess.Popen(CMD_CREATE_APISERVER_CERT, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,cwd=TEMP_LOCAL_K8S_CERT_DIR).communicate()[0]))


        print('Creating kubelet ssl keys in %s.\n'%TEMP_LOCAL_K8S_CERT_DIR)

        print('Creating kubelet keys in %s.\n'%TEMP_LOCAL_K8S_CERT_DIR)
        CMD_CREATE_ADMIN_KEY='openssl genrsa -out kubelet-key.pem 2048'
        print(bytes.decode(subprocess.Popen(CMD_CREATE_ADMIN_KEY, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,cwd=TEMP_LOCAL_K8S_CERT_DIR).communicate()[0]))

        print('Creating kubelet sign request in %s.\n'%TEMP_LOCAL_K8S_CERT_DIR)
        CMD_CREATE_ADMIN_REQ='openssl req -new -key kubelet-key.pem -out kubelet.csr -subj "/CN=kubelet" -config '+OPENSSL_APISERVERS_CONF
        print(bytes.decode(subprocess.Popen(CMD_CREATE_ADMIN_REQ, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,cwd=TEMP_LOCAL_K8S_CERT_DIR).communicate()[0]))

        print('creating kubelet self-sign cert in %s.\n'%TEMP_LOCAL_K8S_CERT_DIR)
        CMD_CREATE_APISERVER_CERT='openssl x509 -req -in kubelet.csr -CA ca.pem -CAkey ca-key.pem -CAcreateserial -out kubelet.pem -days 365 -extfile '+OPENSSL_APISERVERS_CONF
        print(bytes.decode(subprocess.Popen(CMD_CREATE_APISERVER_CERT, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,cwd=TEMP_LOCAL_K8S_CERT_DIR).communicate()[0]))

        print('Creating kube-proxy ssl keys in %s.\n'%TEMP_LOCAL_K8S_CERT_DIR)

        print('Creating kube-proxy keys in %s.\n'%TEMP_LOCAL_K8S_CERT_DIR)
        CMD_CREATE_ADMIN_KEY='openssl genrsa -out kube-proxy-key.pem 2048'
        print(bytes.decode(subprocess.Popen(CMD_CREATE_ADMIN_KEY, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,cwd=TEMP_LOCAL_K8S_CERT_DIR).communicate()[0]))

        print('Creating kube-proxy sign request in %s.\n'%TEMP_LOCAL_K8S_CERT_DIR)
        CMD_CREATE_ADMIN_REQ='openssl req -new -key kube-proxy-key.pem -out kube-proxy.csr -subj "/CN=kube-proxy" -config '+OPENSSL_APISERVERS_CONF
        print(bytes.decode(subprocess.Popen(CMD_CREATE_ADMIN_REQ, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,cwd=TEMP_LOCAL_K8S_CERT_DIR).communicate()[0]))

        print('creating kube-proxy self-sign cert in %s.\n'%TEMP_LOCAL_K8S_CERT_DIR)
        CMD_CREATE_APISERVER_CERT='openssl x509 -req -in kube-proxy.csr -CA ca.pem -CAkey ca-key.pem -CAcreateserial -out kube-proxy.pem -days 365 -extfile '+OPENSSL_APISERVERS_CONF
        print(bytes.decode(subprocess.Popen(CMD_CREATE_APISERVER_CERT, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,cwd=TEMP_LOCAL_K8S_CERT_DIR).communicate()[0]))

        print('creating basic auth file  in %s.\n'%TEMP_LOCAL_K8S_CERT_DIR)
        CMD_CREATE_BASIC_AUTH= 'echo  "kubernetes,admin,admin,system:masters" > basic_auth.csv'
        print(bytes.decode(subprocess.Popen(CMD_CREATE_BASIC_AUTH, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,cwd=TEMP_LOCAL_K8S_CERT_DIR).communicate()[0]))

        print('creating token auth file  in %s.\n'%TEMP_LOCAL_K8S_CERT_DIR)
        CMD_CREATE_TOKEN_AUTH= 'TOKEN=$(dd if=/dev/urandom bs=128 count=1 2>/dev/null | base64 | tr -d "=+/" | dd bs=32 count=1 2>/dev/null);echo  "${TOKEN},admin,admin,system:masters" > tokens.csv'
        print(bytes.decode(subprocess.Popen(CMD_CREATE_TOKEN_AUTH, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,cwd=TEMP_LOCAL_K8S_CERT_DIR).communicate()[0]))

        if WORKER_NODES_ADDR or WORKER_NODES_DNS:


            print('creating woker ssl key in %s.\n'%TEMP_LOCAL_K8S_CERT_DIR)

            print('creating woker priviate key in %s.\n'%TEMP_LOCAL_K8S_CERT_DIR)
            CMD_CREATE_WORKER_KEY='openssl genrsa -out worker-key.pem 2048'
            print(bytes.decode(subprocess.Popen(CMD_CREATE_WORKER_KEY, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,cwd=TEMP_LOCAL_K8S_CERT_DIR).communicate()[0]))

            print('creating worker sign request in %s.\n'%TEMP_LOCAL_K8S_CERT_DIR)
            CMD_CREATE_WORKER_SIGN_REQ='openssl req -new -key worker-key.pem -out worker.csr -subj "/CN=k8s-worker" -config '+OPENSSL_WORKERS_CONF
            print(bytes.decode(subprocess.Popen(CMD_CREATE_WORKER_SIGN_REQ, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,cwd=TEMP_LOCAL_K8S_CERT_DIR).communicate()[0]))

            print('creating worker self-sign cert in %s.\n'%TEMP_LOCAL_K8S_CERT_DIR)
            CMD_CREATE_WORKER_CERT='openssl x509 -req -in worker.csr -CA ca.pem -CAkey ca-key.pem -CAcreateserial -out worker.pem -days 365 -extensions v3_req -extfile '+OPENSSL_WORKERS_CONF
            print(bytes.decode(subprocess.Popen(CMD_CREATE_WORKER_CERT, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,cwd=TEMP_LOCAL_K8S_CERT_DIR).communicate()[0]))
    else:


        print('Will not use self-signed keys, just create all sign request now in %s.\n'%TEMP_LOCAL_K8S_CERT_DIR)
        print('Begin to generate self sing CA keys .\n')

        print('creating apiserver priviate key in %s.\n'%TEMP_LOCAL_K8S_CERT_DIR)
        CMD_CREATE_APISERVER_KEY='openssl genrsa -out apiserver-key.pem 2048'
        print(bytes.decode(subprocess.Popen(CMD_CREATE_APISERVER_KEY, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,cwd=TEMP_LOCAL_K8S_CERT_DIR).communicate()[0]))

        print('creating apiserver sign request in %s.\n'%TEMP_LOCAL_K8S_CERT_DIR)
        CMD_CREATE_APISERVER_SIGN_REQ='openssl req -new -key apiserver-key.pem -out apiserver.csr -subj "/CN=k8s-master" -config '+OPENSSL_APISERVERS_CONF
        print(bytes.decode(subprocess.Popen(CMD_CREATE_APISERVER_SIGN_REQ, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,cwd=TEMP_LOCAL_K8S_CERT_DIR).communicate()[0]))


        print('Creating admin priviate keys in %s.\n'%TEMP_LOCAL_K8S_CERT_DIR)
        CMD_CREATE_ADMIN_KEY='openssl genrsa -out admin-key.pem 2048'
        print(bytes.decode(subprocess.Popen(CMD_CREATE_ADMIN_KEY, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,cwd=TEMP_LOCAL_K8S_CERT_DIR).communicate()[0]))

        print('Creating admin sign request in %s.\n'%TEMP_LOCAL_K8S_CERT_DIR)
        CMD_CREATE_ADMIN_REQ='openssl req -new -key admin-key.pem -out admin.csr -subj "/O=system:masters/CN=admin"'
        print(bytes.decode(subprocess.Popen(CMD_CREATE_ADMIN_REQ, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,cwd=TEMP_LOCAL_K8S_CERT_DIR).communicate()[0]))


        print('Creating kubelet priviate keys in %s.\n'%TEMP_LOCAL_K8S_CERT_DIR)
        CMD_CREATE_ADMIN_KEY='openssl genrsa -out kubelet-key.pem 2048'
        print(bytes.decode(subprocess.Popen(CMD_CREATE_ADMIN_KEY, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,cwd=TEMP_LOCAL_K8S_CERT_DIR).communicate()[0]))

        print('Creating kubelet sign request in %s.\n'%TEMP_LOCAL_K8S_CERT_DIR)
        CMD_CREATE_ADMIN_REQ='openssl req -new -key kubelet-key.pem -out kubelet.csr -subj "/CN=kubelet" -config '+OPENSSL_APISERVERS_CONF
        print(bytes.decode(subprocess.Popen(CMD_CREATE_ADMIN_REQ, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,cwd=TEMP_LOCAL_K8S_CERT_DIR).communicate()[0]))


        print('Creating kube-proxy  priviate keys in %s.\n'%TEMP_LOCAL_K8S_CERT_DIR)
        CMD_CREATE_ADMIN_KEY='openssl genrsa -out kube-proxy-key.pem 2048'
        print(bytes.decode(subprocess.Popen(CMD_CREATE_ADMIN_KEY, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,cwd=TEMP_LOCAL_K8S_CERT_DIR).communicate()[0]))

        print('Creating kube-proxy sign request in %s.\n'%TEMP_LOCAL_K8S_CERT_DIR)
        CMD_CREATE_ADMIN_REQ='openssl req -new -key kube-proxy-key.pem -out kube-proxy.csr -subj "/CN=kube-proxy" -config '+OPENSSL_APISERVERS_CONF
        print(bytes.decode(subprocess.Popen(CMD_CREATE_ADMIN_REQ, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,cwd=TEMP_LOCAL_K8S_CERT_DIR).communicate()[0]))

        print('creating basic auth file  in %s.\n'%TEMP_LOCAL_K8S_CERT_DIR)
        CMD_CREATE_BASIC_AUTH= 'echo  "kubernetes,admin,admin,system:masters" > basic_auth.csv'
        print(bytes.decode(subprocess.Popen(CMD_CREATE_BASIC_AUTH, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,cwd=TEMP_LOCAL_K8S_CERT_DIR).communicate()[0]))

        print('creating token auth file  in %s.\n'%TEMP_LOCAL_K8S_CERT_DIR)
        CMD_CREATE_TOKEN_AUTH= 'TOKEN=$(dd if=/dev/urandom bs=128 count=1 2>/dev/null | base64 | tr -d "=+/" | dd bs=32 count=1 2>/dev/null);echo  "${TOKEN},admin,admin,system:masters" > tokens.csv'
        print(bytes.decode(subprocess.Popen(CMD_CREATE_TOKEN_AUTH, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,cwd=TEMP_LOCAL_K8S_CERT_DIR).communicate()[0]))

        if WORKER_NODES_ADDR or WORKER_NODES_DNS:
            print('creating woker ssl key and sign request in %s.\n'%TEMP_LOCAL_K8S_CERT_DIR)


            print('creating woker priviate key in %s.\n'%TEMP_LOCAL_K8S_CERT_DIR)
            CMD_CREATE_WORKER_KEY='openssl genrsa -out worker-key.pem 2048'
            print(bytes.decode(subprocess.Popen(CMD_CREATE_WORKER_KEY, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,cwd=TEMP_LOCAL_K8S_CERT_DIR).communicate()[0]))

            print('creating worker sign request in %s.\n'%TEMP_LOCAL_K8S_CERT_DIR)
            CMD_CREATE_WORKER_SIGN_REQ='openssl req -new -key worker-key.pem -out worker.csr -subj "/CN=k8s-worker" -config '+OPENSSL_WORKERS_CONF
            print(bytes.decode(subprocess.Popen(CMD_CREATE_WORKER_SIGN_REQ, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,cwd=TEMP_LOCAL_K8S_CERT_DIR).communicate()[0]))

    print('generating various kubeconfig files in %s.\n'%TEMP_LOCAL_K8S_CONF_DIR)

    K8S_CA_CERT=K8S_CERT_DIR+'ca.pem'
    K8S_API_CERT=K8S_CERT_DIR+'apiserver.pem'
    K8S_API_KEY=K8S_CERT_DIR+'apiserver-key.pem'

    K8S_ADMIN_CERT=K8S_CERT_DIR+'admin.pem'
    K8S_ADMIN_KEY=K8S_CERT_DIR+'admin-key.pem'

    K8S_KUBELET_CERT=K8S_CERT_DIR+'kubelet.pem'
    K8S_KUBELET_KEY=K8S_CERT_DIR+'kubelet-key.pem'

    K8S_KUBE_PROXY_CERT=K8S_CERT_DIR+'kube-proxy.pem'
    K8S_KUBE_PROXY_KEY=K8S_CERT_DIR+'kube-proxy-key.pem'



    if DEPLOY_MODE =='multiple':
      print('This is multiple deployment, ')
    else:
      if not Path(TEMP_LOCAL_K8S_CONF_DIR).exists():
        Path(TEMP_LOCAL_K8S_CONF_DIR).mkdir(parents=True)
      SINGLE_APISERVER_ENDPOINT='https://'+ALL_MASTER_NODES_ADDR[0]+':6443'

      print('Generating  kubeconfig for admin: admin.conf in %s.\n'%TEMP_LOCAL_K8S_CONF_DIR)

      CMD_CREATE_ADMIN_KUBECONFIG_1='kubectl config set-cluster devosp-k8s --certificate-authority='+K8S_CA_CERT+' --server='+SINGLE_APISERVER_ENDPOINT+' --kubeconfig='+ADMIN_CONF
      CMD_CREATE_ADMIN_KUBECONFIG_2='kubectl config set-credentials admin  --client-certificate='+K8S_ADMIN_CERT+' --client-key='+K8S_ADMIN_KEY+' --kubeconfig='+ADMIN_CONF
      CMD_CREATE_ADMIN_KUBECONFIG_3='kubectl config set-context admin@devosp-k8s --cluster=devosp-k8s --user=admin  --kubeconfig='+ADMIN_CONF
      CMD_CREATE_ADMIN_KUBECONFIG_4='kubectl config use-context admin@devosp-k8s  --kubeconfig='+ADMIN_CONF
      for CMD in [CMD_CREATE_ADMIN_KUBECONFIG_1,CMD_CREATE_ADMIN_KUBECONFIG_2,CMD_CREATE_ADMIN_KUBECONFIG_3,CMD_CREATE_ADMIN_KUBECONFIG_4]:
        print(bytes.decode(subprocess.Popen(CMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,cwd=TEMP_LOCAL_K8S_CONF_DIR).communicate()[0]))

      print('Generating  kubeconfig for kubelet: kubelet.conf in %s.\n'%TEMP_LOCAL_K8S_CONF_DIR)
      CMD_CREATE_KUBELET_KUBECONFIG_1='kubectl config set-cluster devosp-k8s --certificate-authority='+K8S_CA_CERT+' --server='+SINGLE_APISERVER_ENDPOINT+' --kubeconfig='+KUBELET_CONF
      CMD_CREATE_KUBELET_KUBECONFIG_2='kubectl config set-credentials kubelet  --client-certificate='+K8S_KUBELET_CERT+' --client-key='+K8S_KUBELET_KEY+' --kubeconfig='+KUBELET_CONF
      CMD_CREATE_KUBELET_KUBECONFIG_3='kubectl config set-context kubelet@devosp-k8s --cluster=devosp-k8s --user=admin  --kubeconfig='+KUBELET_CONF
      CMD_CREATE_KUBELET_KUBECONFIG_4='kubectl config use-context kubelet@devosp-k8s  --kubeconfig='+KUBELET_CONF
      for CMD in [CMD_CREATE_KUBELET_KUBECONFIG_1,CMD_CREATE_KUBELET_KUBECONFIG_2,CMD_CREATE_KUBELET_KUBECONFIG_3,CMD_CREATE_KUBELET_KUBECONFIG_4]:
        print(bytes.decode(subprocess.Popen(CMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,cwd=TEMP_LOCAL_K8S_CONF_DIR).communicate()[0]))

      print('Generating  kubeconfig for kube-proxy: kube-proxy.conf in %s.\n'%TEMP_LOCAL_K8S_CONF_DIR)
      CMD_CREATE_KUBE_PROXY_KUBECONFIG_1='kubectl config set-cluster devosp-k8s --certificate-authority='+K8S_CA_CERT+' --server='+SINGLE_APISERVER_ENDPOINT+' --kubeconfig='+KUBE_PROXY_CONF
      CMD_CREATE_KUBE_PROXY_KUBECONFIG_2='kubectl config set-credentials kube-proxy  --client-certificate='+K8S_KUBE_PROXY_CERT+' --client-key='+K8S_KUBE_PROXY_KEY+' --kubeconfig='+KUBE_PROXY_CONF
      CMD_CREATE_KUBE_PROXY_KUBECONFIG_3='kubectl config set-context kube-proxy@devosp-k8s --cluster=devosp-k8s --user=admin  --kubeconfig='+KUBE_PROXY_CONF
      CMD_CREATE_KUBE_PROXY_KUBECONFIG_4='kubectl config use-context kube-proxy@devosp-k8s  --kubeconfig='+KUBE_PROXY_CONF
      for CMD in [CMD_CREATE_KUBE_PROXY_KUBECONFIG_1,CMD_CREATE_KUBE_PROXY_KUBECONFIG_2,CMD_CREATE_KUBE_PROXY_KUBECONFIG_3,CMD_CREATE_KUBE_PROXY_KUBECONFIG_4]:
        print(bytes.decode(subprocess.Popen(CMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,cwd=TEMP_LOCAL_K8S_CONF_DIR).communicate()[0]))
