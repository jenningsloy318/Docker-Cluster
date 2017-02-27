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
    etcd_conf_content.write("data-dir: /data/etcd/")
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


def create_single_etcd_conf(hostIP,conf):
    etcd_conf_content=open(conf,'w')
    etcd_conf_content.write("name: 'default'\n")
    etcd_conf_content.write("data-dir: /data/etcd/")
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
    DOCKER_ENGINE_VER=config['main']['docker_engine_ver']
    DOCKER_ENGINE_PROXY=config['main']['docker_engine_proxy']
    CLUSTER_DNS=config['main']['cluster_dns']
    config_content.close()

    
##define global vars    
    master_hosts=[]
    lb_host=''
    
    MASTER_NODES=[]
    LB_NODES=[]
    ALL_MASTER_NODES=[]
    WORKER_NODES=[]
    etcd_cluster_peer_endpoints=[]
    etcd_cluster_client_endpoints=[]
##create cluster conf 

    ALL_MASTER_ITEMS={}
    for key in config.options(DEPLOY_MODE):
        ALL_MASTER_ITEMS[key]=config.get(DEPLOY_MODE,key)
       
##extract the master nodes
    master_addr_re=re.compile(r'^master.*_addr$')
    lb_addr_re=re.compile(r'^loadbalance.*addr$')
    if DEPLOY_MODE =='multiple':
        for key in ALL_MASTER_ITEMS.keys():
            if master_addr_re.search(key):
                MASTER_NODES.append(ALL_MASTER_ITEMS[key])
            elif lb_addr_re.search(key):
                LB_NODES.append(ALL_MASTER_ITEMS[key])
            else:
                continue
        ALL_MASTER_NODES=MASTER_NODES+LB_NODES
    else:
        for key in ALL_MASTER_ITEMS.keys():
            if master_addr_re.search(key):
                MASTER_NODES.append(ALL_MASTER_ITEMS[key])
        ALL_MASTER_NODES=MASTER_NODES
        
##extract worker nodes
    ALL_WORKER_ITEMS={} 
    for key in config.options('worker_nodes'):
        ALL_WORKER_ITEMS[key]=config.get('worker_nodes',key)
    
    worker_addr_re=re.compile(r'.*_addr$')
    
    for key in ALL_WORKER_ITEMS.keys():
        if worker_addr_re.search(key):
            WORKER_NODES.append(ALL_WORKER_ITEMS[key])
        
##define etcd endpoints
    if DEPLOY_MODE =='multiple':
        for index,host in enumerate(MASTER_NODES):
            etcd_cluster_peer_endpoints.append(''.join(['etcd',str(index),'=http://',host,':2380']))
            etcd_cluster_client_endpoints.append(''.join(['http://',host,':2379']))

    else:
        etcd_cluster_peer_endpoints=''.join(['default','=http://',MASTER_NODES[0],':2380'])
        etcd_cluster_client_endpoints=''.join(['http://',MASTER_NODES[0],':2379'])
            


        ##create both member and proxy conf
    if DEPLOY_MODE =='multiple':
        ##Create main etcd cluster conf
        for index,host in enumerate(MASTER_NODES): 
            print('Staring to create etcd cluster member (%s) conf \n'%host)
            etcd_cluster_conf=host+'/data/kubernetes/conf/etcd.conf'
            etcd_cluster_conf_path=Path(('/').join(etcd_cluster_conf.split('/')[:-1]))
            etcd_cluster_node_name='etcd'+str(index)
            if not etcd_cluster_conf_path.exists():
                etcd_cluster_conf_path.mkdir(parents=True)
            create_etcd_cluster_conf(host,etcd_cluster_node_name,etcd_cluster_peer_endpoints,etcd_cluster_conf)
        
        ##Create etcd proxy conf
        for host in LB_NODES:
            print('Starting to create etcd cluster proxy (%s) conf \n'%host)
            etcd_cluster_proxy_conf=host+'/data/kubernetes/conf/etcd.conf'
            etcd_cluster_proxy_conf_path=Path(('/').join(etcd_cluster_proxy_conf.split('/')[:-1]))
            if not etcd_cluster_proxy_conf_path.exists():
                etcd_cluster_proxy_conf_path.mkdir(parents=True)
            create_etcd_cluster_proxy_conf(etcd_cluster_peer_endpoints,etcd_cluster_proxy_conf)
            
    else:
        ##create single etcd conf
        print('Staring to create etcd cluster member (%s) conf \n'%MASTER_NODES[0])
        for host in MASTER_NODES:
            etcd_conf=host+'/data/kubernetes/conf/etcd.conf'
            etcd_conf_path=Path(('/').join(etcd_conf.split('/')[:-1]))
        if not etcd_conf_path.exists():
            etcd_conf_path.mkdir(parents=True)
        create_single_etcd_conf(host,etcd_conf)

        
### create openssl.conf in  ./certs
    print('Starting to generate openssl conf file in ./certs/.\n')
    from jinja2 import Environment,FileSystemLoader
    openssl_conf_dict={}
    SVC_IP=SVC_CIDR.split('/')[0].replace('0.0','0.1')
    IPs=[SVC_IP]
    DNSs=['kubernetes','kubernetes.default','kubernetes.default.svc','kubernetes.default.svc.cluster.local']
    for key in ALL_MASTER_ITEMS.keys():
        host_addr_re=re.compile(r'^.*_addr$')
        host_dns_re=re.compile(r'^.*dns$')
        if host_addr_re.search(key):
            IPs.append(ALL_MASTER_ITEMS[key])
        else:
            DNSs.append(ALL_MASTER_ITEMS[key])
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
    if DEPLOY_MODE =='multiple':
        ETCD_CLUSTER_CLIENT_ENDPOINTS=''.join(['http://',LB_NODES[0],':2379'])
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
    kubelet_service_master_file=init_dir+'/kubelet.service'
    kubelet_service_worker_file=init_dir+'/kubelet-worker.service'
    kubelet_service_dict={'CLUSTER_DNS':CLUSTER_DNS}
    if DEPLOY_MODE =='single':
        kubelet_service_master_template=init_env.get_template('kubelet-single-master.service.jinja2')
        kubelet_service_worker_template=init_env.get_template('kubelet-worker.service.jinja2')
    else:
        kubelet_service_master_template=init_env.get_template('kubelet-multi-master.service.jinja2')
        kubelet_service_worker_template=kubelet_service_master_template
    with open(kubelet_service_master_file,'w') as kubelet_service_master:
        kubelet_service_master.write(kubelet_service_master_template.render(kubelet_service_dict))
    with open(kubelet_service_worker_file,'w') as kubelet_service_worker:
        kubelet_service_worker.write(kubelet_service_worker_template.render(kubelet_service_dict))



    print('Generating kube-proxy.service.\n')
    kube_proxy_service_file=init_dir+'/kube-proxy.service'
    kube_proxy_service_dict={'POD_CIDR':POD_CIDR}
    kube_proxy_service_template=init_env.get_template('kube-proxy.service.jinja2')
    with open(kube_proxy_service_file,'w') as kube_proxy_service:
        kube_proxy_service.write(kube_proxy_service_template.render(kube_proxy_service_dict))


    print('Generating docker.service.\n')
    docker_service_file=init_dir+'/docker.service'
    docker_service_dict={'DOCKER_ENGINE_PROXY':DOCKER_ENGINE_PROXY}
    docker_service_template=init_env.get_template('docker.service.jinja2')
    with open(docker_service_file,'w') as docker_service:
        docker_service.write(docker_service_template.render(docker_service_dict))

###modify shell scripts 
    print('generating shell scripts')
    shell_dir='./shell'
    shell_path=Path(shell_dir)
    if not shell_path.exists():
        shell_path.mkdir(parents=True)
    shell_env = Environment(loader=FileSystemLoader('./templates/shell/'))


    print('generating get_k8s_server_bin.sh')
    shell_get_k8s_server_bin_file=shell_dir+'/get_k8s_server_bin.sh'
    shell_get_k8s_server_bin_dict={'K8S_VER':K8S_VER}
    shell_get_k8s_server_bin_template=shell_env.get_template('get_k8s_server_bin.sh.jinja2')
    with open(shell_get_k8s_server_bin_file,'w') as shell_get_k8s_server_bin:
        shell_get_k8s_server_bin.write(shell_get_k8s_server_bin_template.render(shell_get_k8s_server_bin_dict))


    print('generating k8s_install_docker_engine.sh')
    shell_install_docker_engine_file=shell_dir+'/k8s_install_docker_engine.sh'
    shell_install_docker_engine_dict={'DOCKER_ENGINE_VER':DOCKER_ENGINE_VER}
    shell_install_docker_engine_template=shell_env.get_template('k8s_install_docker_engine.sh.jinja2')
    with open(shell_install_docker_engine_file,'w') as shell_install_docker_engine:
        shell_install_docker_engine.write(shell_install_docker_engine_template.render(shell_install_docker_engine_dict))


### modify apiserver-proxy.conf and nginx.conf
    if DEPLOY_MODE =='multiple':
        for host in LB_NODES:
            apiserver_proxy_conf_dir=host+'/etc/nginx/sites_tcp_conf.d'
            apiserver_proxy_conf_root_dir=host+'/etc/nginx'
            conf_path=Path(apiserver_proxy_conf_dir)
            if not conf_path.exists():
                conf_path.mkdir(parents=True)
            apiserver_proxy_conf_env = Environment(loader=FileSystemLoader('./templates/conf/'))
            print('Generating apiserver-proxy.conf, which will be placed at /etc/nginx/sites_tcp_conf.d/* on %s.\n'%lb_host)
            apiserver_proxy_conf_file=apiserver_proxy_conf_dir+'/apiserver-proxy.conf'
            apiserver_proxy_conf_dict={'MASTER_HOSTS':MASTER_NODES}
            apiserver_proxy_conf_template=apiserver_proxy_conf_env.get_template('apiserver-proxy.conf.jinja2')
            with open(apiserver_proxy_conf_file,'w') as apiserver_proxy_conf:
                apiserver_proxy_conf.write(apiserver_proxy_conf_template.render(apiserver_proxy_conf_dict))

            print('Generating nginx.conf.\n')
            nginx_conf_file=apiserver_proxy_conf_root_dir+'/nginx.conf'
            nginx_conf_dict={'INCLUDE':'include /etc/nginx/sites_tcp_conf.d/*;'}
            nginx_conf_template=apiserver_proxy_conf_env.get_template('nginx.conf.jinja2')
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


    print("copy certs/ and init/ to each master host folder.\n")
    for host in ALL_MASTER_NODES:
        host_certs_dir=host+'/data/kubernetes/certs/'
        host_init_dir=host+'/lib/systemd/system/'
        host_certs_path=Path(host_certs_dir)
        host_init_path=Path(host_init_dir)
        if not host_certs_path.exists():
            host_certs_path.mkdir(parents=True)
        if not host_init_path.exists():
            host_init_path.mkdir(parents=True)
        certs_cp_command=''.join(['cp -r certs/apiserver-key.pem certs/apiserver.pem certs/apiserver-pub.pem certs/basic_auth.csv certs/ca-key.pem certs/ca.pem certs/ca-pub.pem ',host_certs_dir])
        init_cp_command=''.join(['cp -r init/docker.service  init/kubelet.service  init/kube-proxy.service ',host_init_dir])
        print(bytes.decode(subprocess.Popen(certs_cp_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]))
        print(bytes.decode(subprocess.Popen(init_cp_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]))

    print("copy manifests/ to each master host folder.\n")
    if DEPLOY_MODE =='multiple':
        for host in MASTER_NODES:
            host_manifests_dir=host+'/data/kubernetes/manifests/'
            host_manifests_path=Path(host_manifests_dir)
            if not host_manifests_path.exists():
                host_manifests_path.mkdir(parents=True)
            manifests_cp_command=''.join(['cp -r manifests/* ',host_manifests_dir])
            print(bytes.decode(subprocess.Popen(manifests_cp_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]))
        etcd_proxy_init_cp_command=''.join(['cp templates/init/etcd-proxy.service ',LB_NODES[0],'/lib/systemd/system/'])
        print(bytes.decode(subprocess.Popen(etcd_proxy_init_cp_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]))
         
    else:
        host_manifests_dir=MASTER_NODES[0]+'/data/kubernetes/manifests/'
        host_manifests_path=Path(host_manifests_dir)
        if not host_manifests_path.exists():
           host_manifests_path.mkdir(parents=True)
        manifests_cp_command=''.join(['cp -r manifests/* ',host_manifests_dir])
        print(bytes.decode(subprocess.Popen(manifests_cp_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]))

            
    print("create kubeconfig.\n")
    if DEPLOY_MODE =='multiple':
        shell_kubeconfig_command=''.join(['sh templates/shell/gen_kubeconfig.sh ',LB_NODES[0],'  .'])
        print(bytes.decode(subprocess.Popen(shell_kubeconfig_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]))
         
    else:
        shell_kubeconfig_command=''.join(['sh templates/shell/gen_kubeconfig.sh ',MASTER_NODES[0],'  .'])
        print(bytes.decode(subprocess.Popen(shell_kubeconfig_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]))



    print('copy kubeconfig to each host folder')
    for host in ALL_MASTER_NODES:
        kubeconfig_cp_command=''.join(['cp kubeconfig ',host,'/data/kubernetes'])
        print(bytes.decode(subprocess.Popen(kubeconfig_cp_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]))

   
    print('copy shell/ to each host folder')
    for host in ALL_MASTER_NODES:
        templates_cp_command=''.join(['cp -r shell ',host,'/data/kubernetes'])
        print(bytes.decode(subprocess.Popen(templates_cp_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]))
    

    print('copy files to worker node foler')
    for host in WORKER_NODES:
        host_certs_dir=host+'/data/kubernetes/certs/'
        host_init_dir=host+'/lib/systemd/system/'
        host_certs_path=Path(host_certs_dir)
        host_init_path=Path(host_init_dir)
        if not host_certs_path.exists():
            host_certs_path.mkdir(parents=True)
        if not host_init_path.exists():
            host_init_path.mkdir(parents=True)
        kubeconfig_cp_command=''.join(['cp kubeconfig ',host,'/data/kubernetes'])
        print(bytes.decode(subprocess.Popen(kubeconfig_cp_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]))
        certs_cp_command=''.join(['cp -r certs/ca.pem certs/apiserver.pem certs/apiserver-key.pem certs/basic_auth.csv ',host_certs_dir])
        print('Processing on %s\n'%host)
        print(bytes.decode(subprocess.Popen(certs_cp_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]))
        init_cp_command=''.join(['cp -r init/docker.service  init/kubelet-worker.service  init/kube-proxy.service ',host_init_dir])
        print(bytes.decode(subprocess.Popen(init_cp_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]))
        templates_cp_command=''.join(['cp -r shell ',host,'/data/kubernetes'])
        print(bytes.decode(subprocess.Popen(templates_cp_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]))


    print('cleaning the files\n')
    clean_command=''.join(['rm -rf init certs manifests shell kubeconfig'])
#    print(bytes.decode(subprocess.Popen(clean_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]))

    print('Proceed the installing on remote hosts\n')

    for host in MASTER_NODES:
        print('Processing on %s\n'%host)
        print('Cleaning old conf on %s\n'%host)
        remote_cmd1=''.join(['ssh root@',host,' "systemctl stop kubelet;systemctl stop kubelet-worker;systemctl disable kubelet-worker ;[[ \$(docker ps | grep -v \"CONTAINER\">/dev/null )  ]] && docker rm -f \$(docker ps -a -q)  >/dev/null ; rm -rf /data/{kubelet,kubernetes}"'])
        print(bytes.decode(subprocess.Popen(remote_cmd1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]))
        print('syncing file to %s\n'%host)
        remote_cmd2=''.join(['rsync -av ',host,'/ root@',host,':/'])
        print(bytes.decode(subprocess.Popen(remote_cmd2, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]))
        remote_cmd3=''.join(['ssh root@',host,' "/data/kubernetes/shell/get_k8s_server_bin.sh"'])
        print('Installing k8s binaries if needed on %s\n'%host)
        print(bytes.decode(subprocess.Popen(remote_cmd3, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]))
        remote_cmd4=''.join(['ssh root@',host,' "/data/kubernetes/shell/k8s_install_docker_engine.sh"'])
        print('Installing docker engine if needed on %s\n'%host)
        print(bytes.decode(subprocess.Popen(remote_cmd4, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]))
        remote_cmd5=''.join(['ssh root@',host,' "[ ! -d /data/log ] && mkdir /data/log"'])
        print('Creating neccessary folders on %s\n'%host)
        print(bytes.decode(subprocess.Popen(remote_cmd5, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]))
        remote_cmd6=''.join(['ssh root@',host,' "[ ! -d /data/etcd ] && mkdir /data/etcd"'])
        print(bytes.decode(subprocess.Popen(remote_cmd6, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]))
        print('Restarting services on %s\n'%host)
        remote_cmd7=''.join(['ssh root@',host,' "systemctl daemon-reload ;systemctl restart docker;systemctl restart kubelet;systemctl restart kube-proxy;systemctl enable docker;systemctl enable kubelet;systemctl enable kube-proxy"'])
        print(bytes.decode(subprocess.Popen(remote_cmd7, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]))
    
    if DEPLOY_MODE =='multiple':
        print('installing on lb nodes\n')
        for host in LB_NODES:
            print('Processing on %s\n'%host)
            remote_cmd1=''.join(['ssh root@',host,' "systemctl stop kubelet;systemctl stop kubelet-worker;systemctl disable kubelet-worker ;[[ \$(docker ps | grep -v \"CONTAINER\">/dev/null )  ]] && docker rm -f \$(docker ps -a -q)  >/dev/null ; rm -rf /data/{kubelet,kubernetes}"'])
            print('Cleaning old conf on %s\n'%host)   
            print(bytes.decode(subprocess.Popen(remote_cmd1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]))
            remote_cmd2=''.join(['rsync -av ',host,'/ root@',host,':/'])
            print('syncing file to %s\n'%host)
            print(bytes.decode(subprocess.Popen(remote_cmd2, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]))
            remote_cmd3=''.join(['ssh root@',host,' "/data/kubernetes/shell/get_k8s_server_bin.sh"'])
            print('Installing k8s binaries if needed on %s\n'%host)
            print(bytes.decode(subprocess.Popen(remote_cmd3, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]))
            remote_cmd4=''.join(['ssh root@',host,' "/data/kubernetes/shell/k8s_install_docker_engine.sh"'])
            print('Installing docker engine if needed on %s\n'%host)
            print(bytes.decode(subprocess.Popen(remote_cmd4, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]))
            remote_cmd5=''.join(['ssh root@',host,' "[ ! -f /usr/sbin/nginx ] && apt-get install nginx -y"'])
            print('Installing nginx if needed on %s\n'%host)
            print(bytes.decode(subprocess.Popen(remote_cmd5, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]))
            remote_cmd6=''.join(['ssh root@',host,' "systemctl daemon-reload ;systemctl restart docker;systemctl restart kubelet;systemctl restart kube-proxy;systemctl enable docker;systemctl enable kubelet;systemctl enable kube-proxy;systemctl restart etcd-proxy;systemctl enable etcd-proxy"'])
            print('Restarting services on %s\n'%host)
            print(bytes.decode(subprocess.Popen(remote_cmd6, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]))
            remote_cmd7=''.join(['ssh root@',host,' "systemctl restart nginx&&systemctl enable nginx"'])
            print(bytes.decode(subprocess.Popen(remote_cmd7, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]))
    




    print('installing on worker nodes\n')
    for host in WORKER_NODES:
        print('Processing on %s\n'%host)
        remote_cmd1=''.join(['ssh root@',host,' "systemctl stop kubelet ;systemctl stop kubelet-worker;systemctl stop kubelet-worker;[[ \$(docker ps | grep -v \"CONTAINER\">/dev/null )  ]] && docker rm -f \$(docker ps -a -q)  >/dev/null ; rm -rf /data/{kubelet,kubernetes}"'])
        print('Cleaning old conf on %s\n'%host)       
        print(bytes.decode(subprocess.Popen(remote_cmd1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]))
        remote_cmd2=''.join(['rsync -a ',host,'/ root@',host,':/'])
        print('syncing file to %s\n'%host)
        print(bytes.decode(subprocess.Popen(remote_cmd2, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]))
        remote_cmd3=''.join(['ssh root@',host,' "/data/kubernetes/shell/get_k8s_server_bin.sh"'])
        print('Installing k8s binaries if needed on %s\n'%host)
        print(bytes.decode(subprocess.Popen(remote_cmd3, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]))
        remote_cmd4=''.join(['ssh root@',host,' "/data/kubernetes/shell/k8s_install_docker_engine.sh"'])
        print('Installing docker engine if needed on %s\n'%host)
        print(bytes.decode(subprocess.Popen(remote_cmd4, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]))
        remote_cmd5=''.join(['ssh root@',host,' "systemctl daemon-reload ;systemctl restart docker;systemctl restart kubelet-worker;systemctl restart kube-proxy;systemctl enable docker;systemctl enable kubelet-worker;systemctl enable kube-proxy"'])
        print('Restarting services on %s\n'%host)
        print(bytes.decode(subprocess.Popen(remote_cmd5, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]))
