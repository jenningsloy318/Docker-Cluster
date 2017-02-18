#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Jennings Liu@ 2017-02-18 11:58:44

import argparse
import sys
import configparser
import re
from pathlib import Path
import subprocess


def create_etcd_cluster_conf(hostIP,name,endpoints,conf):
    etcd_conf_content=open(conf,'w')
    etcd_conf_content.write("name: '%s'\n"%name)
    etcd_conf_content.write("initial-cluster: %s\n"%','.join(endpoints))
    etcd_conf_content.write("initial-advertise-peer-urls: http://%s:2380\n"%hostIP)
    etcd_conf_content.write("initial-cluster-token: etcd-cluster\n")
    etcd_conf_content.write("initial-cluster-state: new\n")
    etcd_conf_content.write("listen-peer-urls: http://%s:2380\n"%hostIP)
    etcd_conf_content.write("listen-client-urls: http://0.0.0.0:2379\n")
    etcd_conf_content.write("advertise-client-urls: http://%s:2379\n"%hostIP)
    etcd_conf_content.flush()
    etcd_conf_content.close()

def create_etcd_cluster_proxy_conf(hostIP,name,endpoints,conf):
    etcd_proxy_conf_content=open(conf,'w')
    etcd_proxy_conf_content.write("proxy: 'on'\n")
    etcd_proxy_conf_content.write("listen-client-urls: http://0.0.0.0:2379\n")
    etcd_proxy_conf_content.write("initial-cluster: %s\n"%','.join(endpoints))
    etcd_proxy_conf_content.write("advertise-client-urls:  http://0.0.0.0:2379\n")
    etcd_proxy_conf_content.flush()
    etcd_proxy_conf_content.close()


def create_single_etcd_conf(hostIP,conf):
    etcd_conf_content=open(conf,'w')
    etcd_conf_content.write("name: 'default'\n")
    etcd_conf_content.write("initial-cluster: default=http://%s:2380\n"%hostIP)
    etcd_conf_content.write("initial-advertise-peer-urls: http://%s:2380\n"%hostIP)
    etcd_conf_content.write("initial-cluster-token: etcd-cluster\n")
    etcd_conf_content.write("initial-cluster-state: new\n")
    etcd_conf_content.write("listen-peer-urls: http://%s:2380\n"%hostIP)
    etcd_conf_content.write("listen-client-urls: http://0.0.0.0:2379\n")
    etcd_conf_content.write("advertise-client-urls: http://%s:2379\n"%hostIP)
    etcd_conf_content.flush()
    etcd_conf_content.close()




if __name__ == '__main__':
##print parameters
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
    CLUSTER_DNS=config['main']['cluster_dns']
    CLUSTER_PARAS=config[DEPLOY_MODE]
    config_content.close()

    master_hosts=[]
    lb_host=''
    etcd_cluster_peer_endpoints=[]
    etcd_cluster_client_endpoints=[]
##create cluster conf 

    ALL_HOSTS={}
    for key in config.options(DEPLOY_MODE):
        ALL_HOSTS[key]=config.get(DEPLOY_MODE,key)
       

    if DEPLOY_MODE =='multiple':
        master_addr_re=re.compile(r'^master.*_addr$')
        lb_addr_re=re.compile(r'^loadbalance.*addr$')
        
        ##generate initial-cluster string
    #     etcd_cluster_peer_endpoints=[]
    #     etcd_cluster_client_endpoints=[]
        for key in ALL_HOSTS.keys(): 
            if master_addr_re.search(key):
                etcd_cluster_host=ALL_HOSTS[key]
                etcd_cluster_peer_endpoints.append(''.join([key.split('_')[0].strip(),"=http://",etcd_cluster_host.strip(),":2380"]))
                etcd_cluster_client_endpoints.append(''.join(["http://",etcd_cluster_host.strip(),":2379"]))
                master_hosts.append(etcd_cluster_host.strip())


        ##create both member and proxy conf
        for key in ALL_HOSTS.keys(): 
            if master_addr_re.search(key):
                etcd_cluster_host=ALL_HOSTS[key]
                etcd_cluster_host_name=key.split('_')[0].strip()
                print('Staring to create etcd cluster member (%s) conf \n'%etcd_cluster_host)
                etcd_cluster_conf=etcd_cluster_host+'/kubernetes/conf/etcd.conf'
                etcd_cluster_conf_path=Path(('/').join(etcd_cluster_conf.split('/')[:-1]))
                if not etcd_cluster_conf_path.exists():
                    etcd_cluster_conf_path.mkdir(parents=True)
                create_etcd_cluster_conf(etcd_cluster_host,etcd_cluster_host_name,etcd_cluster_peer_endpoints,etcd_cluster_conf)
            elif lb_addr_re.search(key):
                etcd_cluster_proxy=ALL_HOSTS[key]
                lb_host=etcd_cluster_proxy
                etcd_cluster_proxy_name=key.split('_')[0].strip()
                print('Starting to create etcd cluster proxy (%s) conf \n'%ALL_HOSTS[key])
                etcd_cluster_proxy_conf=etcd_cluster_proxy+'/kubernetes/conf/etcd.conf'
                etcd_cluster_proxy_conf_path=Path(('/').join(etcd_cluster_proxy_conf.split('/')[:-1]))
                if not etcd_cluster_proxy_conf_path.exists():
                    etcd_cluster_proxy_conf_path.mkdir(parents=True)
                create_etcd_cluster_proxy_conf(etcd_cluster_proxy,etcd_cluster_proxy_name,etcd_cluster_peer_endpoints,etcd_cluster_proxy_conf)
            else:
                continue
    else:
        master_addr_re=re.compile(r'^master_addr$')
        for key in  ALL_HOSTS.keys():
            if master_addr_re.search(key):
                print('Starting to create single etcd   (%s) conf \n'%ALL_HOSTS[key])
                etcd_host=ALL_HOSTS[key]
            else:
                continue
        etcd_cluster_client_endpoints="http://"+etcd_host+":2379"
        master_hosts.append(etcd_host)
        ###create single etcd conf
        etcd_conf=etcd_host+'/kubernetes/conf/etcd.conf'
        etcd_conf_path=Path(('/').join(etcd_conf.split('/')[:-1]))
        if not etcd_conf_path.exists():
            etcd_conf_path.mkdir(parents=True)
        create_single_etcd_conf(etcd_host,etcd_conf)

        
### create openssl.conf in  ./certs
    print('Starting to generate openssl conf file in ./certs/.\n')
    from jinja2 import Environment,FileSystemLoader
    openssl_conf_dict={}
    SVC_IP=SVC_CIDR.split('/')[0].replace('0.0','0.1')
    IPs=[SVC_IP]
    DNSs=['kubernetes','kubernetes.default','kubernetes.default.svc','kubernetes.default.svc.cluster.local']
    for key in ALL_HOSTS.keys():
        host_addr_re=re.compile(r'^.*_addr$')
        host_dns_re=re.compile(r'^.*dns$')
        if host_addr_re.search(key):
            IPs.append(ALL_HOSTS[key])
        else:
            DNSs.append(ALL_HOSTS[key])
    openssl_conf_dict={'IPs':IPs,'DNSs':DNSs}
    openssl_conf_path=Path('./certs/')
    openssl_conf='./certs/openssl.conf'
    if not openssl_conf_path.exists():
        openssl_conf_path.mkdir(parents=True)
    openssl_env = Environment(loader=FileSystemLoader('./templates/certs/'))
    openssl_template = openssl_env.get_template('openssl.conf.jinja2')
    with open(openssl_conf,'w') as openssl_conf_file:
        openssl_conf_file.write(openssl_template.render(openssl_conf_dict))
    openssl_conf_file.close()

### modify k8s pod files

    print('Generating k8s(apiserver controller-manager scheduler) pod file in ./manifests/.\n')
    manifests_dir='./manifests'
    manifests_path=Path(manifests_dir)
    if not manifests_path.exists():
        manifests_path.mkdir(parents=True)
    k8s_env=Environment(loader=FileSystemLoader('./templates/manifests/'))

    print('Generating kube-apiserver.yaml.\n')
    apiserver_pod_file=manifests_dir+'/kube-apiserver.yaml'
    apiserver_dict={'SVC_CIDR':SVC_CIDR,'K8S_VER':K8S_VER}
    apiserver_template=k8s_env.get_template('kube-apiserver.yaml.jinja2')

    with open(apiserver_pod_file,'w') as kube_apiserver_yaml:
        kube_apiserver_yaml.write(apiserver_template.render(apiserver_dict))



    print('Generating kube-apiserver.yaml.\n')
    apiserver_pod_file=manifests_dir+'/kube-apiserver.yaml'
    apiserver_dict={'SVC_CIDR':SVC_CIDR,'K8S_VER':K8S_VER}
    apiserver_template=k8s_env.get_template('kube-apiserver.yaml.jinja2')
    with open(apiserver_pod_file,'w') as kube_apiserver_yaml:
        kube_apiserver_yaml.write(apiserver_template.render(apiserver_dict))



    print('Generating kube-controller-manager.yaml.\n')
    controller_manager_pod_file=manifests_dir+'/kube-controller-manager.yaml'
    controller_manager_dict={'POD_CIDR':POD_CIDR,'K8S_VER':K8S_VER}
    controller_manager_template=k8s_env.get_template('kube-controller-manager.yaml.jinja2')
    with open(controller_manager_pod_file,'w') as kube_controller_manager_yaml:
        kube_controller_manager_yaml.write(controller_manager_template.render(controller_manager_dict))



    print('Generating kube-scheduler.yaml.\n')
    scheduler_pod_file=manifests_dir+'/kube-scheduler.yaml'
    scheduler_dict={'POD_CIDR':POD_CIDR,'K8S_VER':K8S_VER}
    scheduler_template=k8s_env.get_template('kube-scheduler.yaml.jinja2')
    with open(scheduler_pod_file,'w') as kube_scheduler_yaml:
        kube_scheduler_yaml.write(scheduler_template.render(scheduler_dict))



    print('Generating etcd.yaml.\n')
    etcd_pod_file=manifests_dir+'/etcd.yaml'
    etcd_dict={'ETCD_VER':ETCD_VER}
    etcd_template=k8s_env.get_template('etcd.yaml.jinja2')
    with open(etcd_pod_file,'w') as etcd_yaml:
        etcd_yaml.write(etcd_template.render(etcd_dict))



    print('Generating calico.yaml.\n')
    calico_pod_file=manifests_dir+'/calico.yaml'
    if isinstance(etcd_cluster_client_endpoints,list):
        ETCD_CLUSTER_CLIENT_ENDPOINTS=','.join(etcd_cluster_client_endpoints)
    else:
        ETCD_CLUSTER_CLIENT_ENDPOINTS=etcd_cluster_client_endpoints
    calico_dict={'ETCD_CLUSTER_CLIENT_ENDPOINTS':ETCD_CLUSTER_CLIENT_ENDPOINTS}
    calico_template=k8s_env.get_template('calico.yaml.jinja2')
    with open(calico_pod_file,'w') as calico_yaml:
        calico_yaml.write(calico_template.render(calico_dict))



    print('Generating kube-dns.yaml.\n')
    kube_dns_pod_file=manifests_dir+'/kube-dns.yaml'
    kube_dns_dict={'CLUSTER_DNS':CLUSTER_DNS}
    kube_dns_template=k8s_env.get_template('kube-dns.yaml.jinja2')
    with open(kube_dns_pod_file,'w') as kube_dns_yaml:
        kube_dns_yaml.write(kube_dns_template.render(kube_dns_dict))


### modify kubelet.service and kube-proxy.service 
    print('Generating kubelet.service kube-proxy.service  file in ./init/.')
    init_dir='./init'
    init_path=Path(init_dir)
    if not init_path.exists():
        init_path.mkdir(parents=True)
    init_env = Environment(loader=FileSystemLoader('./templates/init/'))

    print('Generating kubelet.service.\n')
    kubelet_service_file=init_dir+'/kubelet.service'
    kubelet_service_dict={'CLUSTER_DNS':CLUSTER_DNS}
    kubelet_service_template=init_env.get_template('kubelet.service.jinja2')
    with open(kubelet_service_file,'w') as kubelet_service:
        kubelet_service.write(kubelet_service_template.render(kubelet_service_dict))



    print('Generating kube-proxy.service.\n')
    kube_proxy_service_file=init_dir+'/kube-proxy.service'
    kube_proxy_service_dict={'POD_CIDR':POD_CIDR}
    kube_proxy_service_template=init_env.get_template('kube-proxy.service.jinja2')
    with open(kube_proxy_service_file,'w') as kube_proxy_service:
        kube_proxy_service.write(kube_proxy_service_template.render(kube_proxy_service_dict))


### modify apiserver-proxy.conf and nginx.conf
    if DEPLOY_MODE =='multiple':
        conf_dir=lb_host+'/kubernetes/conf'
        conf_path=Path(conf_dir)
        if not conf_path.exists():
            conf_path.mkdir(parents=True)
        conf_env = Environment(loader=FileSystemLoader('./templates/conf/'))
        print('Generating apiserver-proxy.conf, which will be placed at /etc/nginx/sites_tcp_conf.d/* on %s.\n'%lb_host)
        apiserver_proxy_conf_file=conf_dir+'/apiserver-proxy.conf'
        apiserver_proxy_conf_dict={'MASTER_HOSTS':master_hosts}
        apiserver_proxy_conf_template=conf_env.get_template('apiserver-proxy.conf.jinja2')
        with open(apiserver_proxy_conf_file,'w') as apiserver_proxy_conf:
            apiserver_proxy_conf.write(apiserver_proxy_conf_template.render(apiserver_proxy_conf_dict))

        print('Generating nginx.conf.\n')
        nginx_conf_file=conf_dir+'/nginx.conf'
        nginx_conf_dict={'INCLUDE':'include /etc/nginx/sites_tcp_conf.d/*;'}
        nginx_conf_template=conf_env.get_template('nginx.conf.jinja2')
        with open(nginx_conf_file,'w') as nginx_conf:
            nginx_conf.write(nginx_conf_template.render(nginx_conf_dict))



### create apiserver certs 
    print("creating SSL certs \n")
    shell_create_cert='sh ../templates/shell/k8s_generate_ssl_certs.sh openssl.conf '
    print(bytes.decode(subprocess.Popen(shell_create_cert, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,cwd='./certs/').communicate()[0]))
	
##categorize files
    print("copy templates/manifests/kubernetes-dashboard.yaml to ./manifests .\n")
    cp_command1='cp templates/manifests/kubernetes-dashboard.yaml ./manifests/'
    print(bytes.decode(subprocess.Popen(cp_command1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]))


    print("copy certs/ and init/ to each host folder.\n")
    master_hosts.append(lb_host)
    for host in master_hosts:
        cp_command2=''.join(['cp -r certs init ',host,'/kubernetes'])
        print(bytes.decode(subprocess.Popen(cp_command2, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]))

    print("copy manifests/ to each host folder.\n")
    if DEPLOY_MODE =='multiple':
        for host in master_hosts:
            cp_command3=''.join(['cp -r manifests ',host,'/kubernetes/'])
            print(bytes.decode(subprocess.Popen(cp_command3, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]))
        cp_command4=''.join(['cp templates/init/etcd.service ',lb_host,'/kubernetes/init/'])
        print(bytes.decode(subprocess.Popen(cp_command4, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]))
         
    else:
        cp_command5=''.join(['cp -r manifests ',master_hosts[0],'/kubernetes'])
        print(bytes.decode(subprocess.Popen(cp_command5, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]))

            
    print("create kubeconfig.\n")
    if DEPLOY_MODE =='multiple':
        shell_kubeconfig_command=''.join(['sh templates/shell/gen_kubeconfig.sh ',lb_host,'  .'])
        print(bytes.decode(subprocess.Popen(shell_kubeconfig_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]))
         
    else:
        shell_kubeconfig_command=''.join(['sh templates/shell/gen_kubeconfig.sh ',master_hosts[0],'  .'])
        print(bytes.decode(subprocess.Popen(shell_kubeconfig_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]))



    print('copy kubeconfig to each host folder')
    for host in master_hosts:
        cp_command6=''.join(['cp kubeconfig ',host,'/kubernetes'])
        print(bytes.decode(subprocess.Popen(cp_command6, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]))

            
