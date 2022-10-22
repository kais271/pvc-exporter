# pvc-exporter
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Artifact Hub](https://img.shields.io/endpoint?url=https://artifacthub.io/badge/repository/pvc-exporter)](https://artifacthub.io/packages/search?repo=pvc-exporter)
![Docker Image Size (latest by date)](https://img.shields.io/docker/image-size/dockerid31415926/pvc-exporter?label=pvc-exporter)
![Docker Pulls](https://img.shields.io/docker/pulls/dockerid31415926/pvc-exporter)


This exporter provides 3 metrics to monitoring **block storage, hostpath and nfs** pvcs.  
1. **pvc_usage**: Provides the percentage of PVC usage.  
2. **pvc_mapping**: Provides the mapping between pod and pvc.  
3. **pvc_used_MB**: Provide the specific usage of PVC, the unit is MB.  

# Why choose pvc-exporter?
If you want to monitor pvc usage and the native mertics are not available. 

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
1.X86_64  
2.ARM64  

 
# Usage  
```
helm repo add pvc-exporter https://kais271.github.io/pvc-exporter/helm3/charts/  
kubectl create namespace pvc-exporter  
helm install demo pvc-exporter/pvc-exporter --namespace pvc-exporter --version v0.1.4-alpha  
```
# Metrics Examples  
**#pvc_usage**  
The value is pvc usage percent that equal pvc_used_MB/pvc_requested_MB. Some informations about pvc is also provided.  
`pvc_usage{container="pvc-exporter", endpoint="metrics", grafana_key="pvc-957af729-41e3-40cc-b90d-71ffab0ec149-web-3", instance="10.3.179.59:8848", job="demo-pvc-exporter", namespace="pvc-exporter", persistentvolume="pvc-957af729-41e3-40cc-b90d-71ffab0ec149", persistentvolumeclaim="www-web-3", pod="demo-pvc-exporter-phbmt", pvc_namespace="default", pvc_requested_size_MB="1024.0", pvc_requested_size_human="1G", pvc_type="block", pvc_used_MB="2.5", service="demo-pvc-exporter"} 0.01  `

**#pvc_mapping**  
This metrics provide mapping between pvc and pod.  
`pvc_mapping{container="pvc-exporter", endpoint="metrics", grafana_key="pvc-e555d811-c0b1-4e0b-b3ee-25c7cb1c66ee-web-0", host_ip="192.168.175.129", instance="10.3.179.59:8848", job="demo-pvc-exporter", mountedby="web-0", namespace="pvc-exporter", persistentvolume="pvc-e555d811-c0b1-4e0b-b3ee-25c7cb1c66ee", persistentvolumeclaim="www-web-0", pod="demo-pvc-exporter-phbmt", pod_namespace="default", service="demo-pvc-exporter"} 0`

# Promethesus & Grafana

You can use this expression **" sum without (grafana_key,container,pod,service,namespace,job,instance,endpoint,pvc_namespace,pvc_requested_size_MB) ( (pvc_usage) + on(grafana_key) group_left(persistentvolumeclaim,mountedby,pod_namespace)pvc_mapping*0) "** to grafana to monitoring pvc usage.  
**note!!!** You can see one pvc usage percent more than 1, that's a nfs pvc. As we know the nfs and hostpath pvc will exceed the requested size if the provisioner not support quota.  
**For dashboard, you can refer /docs/PVC-Dashboard.json**  

![grafana-1](./docs/grafana-1223.png)
