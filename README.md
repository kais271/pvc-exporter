# pvc-exporter
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Artifact Hub](https://img.shields.io/endpoint?url=https://artifacthub.io/badge/repository/pvc-exporter)](https://artifacthub.io/packages/search?repo=pvc-exporter)
![Docker Image Size (latest by date)](https://img.shields.io/docker/image-size/dockerid31415926/pvc-exporter?color=green&label=pvc-exporter)
![Docker Pulls](https://img.shields.io/docker/pulls/dockerid31415926/pvc-exporter?color=green)  

This project provides 2 metrics,one for monitoring mounted pvc usage named **"pvc_usage"**, and one for provides the mapping between pod and pvc named **"pvc_mapping"**.

# Note  
The hostpath pvc and nfs pvc will be supported starting with version 0.1.3.  
This exporter now supports 3 types of pvc: hostpath, nfs, blockstorage.  
For blockstorage just supported the pvc mounted as **"volumeMounts"**. Such as longgorn,trident,rook-ceph,etc..If your pv is block model and mounted as **"volumeDevices"** that not supported yet. 

**Architecture Change:**  
Previously, **"pvc_usage"** and **"pvc_mapping"** were divided into 2 images. Now, they have merged into one image.  
So if you want to upgrade to v0.1.3, we recommend that you uninstall old version then install new version.  

# Support list
The following storage provisioners has been tested..  
1.longgorn  
2.trident  
3.rook-ceph  
4.aliyun flexvolume  
5.iomesh  
6.nutanix-csi  
...  

The following architectures:  
1.x86_64  
2.ARM64  

 
# Usage
    helm repo add pvc-exporter https://kais271.github.io/pvc-exporter/helm3/charts/  
    kubectl create namespace pvc-exporter  
    helm install demo pvc-exporter/pvc-exporter --namespace pvc-exporter --version v0.1.2

# Promethesus & Grafana

You can use this expression **" (sum without (container,pod,service,namespace,job,instance,endpoint) (pvc_usage)) + on(volumename) group_left(persistentvolumeclaim,mountedby,pod_namespace)pvc_mapping*0 "** to grafana to monitor pvc usage.  
![grafana-1](./docs/grafana.png)
