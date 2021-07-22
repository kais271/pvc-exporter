# PVC Exporter

This exporter provides 2 metrics, one for monitoring mounted pvc usage precent named pvc_usage, and one for provides the mapping between pod and pvc named pvc_mapping.

## Supported storage providers

Only used to monitor mounted pvc that provied by block storage provisioner.
The following storage provisioners has been confirmed to be working:

* longgorn  
* trident  
* rook-ceph  
* aliyun flexvolume  
* iomesh
* nutanix-csi

## Install

You can get the following files and run apply them.
kubectl apply -f namespace.yml -f rbac.yml -f deployment.yml -f daemonset.yml -f servicemonitor.yml

## Grafana

You can import the [pvc_usage-dashboard](./docs/pvc_usage-dashboard.json) to grafana for monitoring pvc usage.
![grafana-1](./docs/grafana-1.PNG)
The legend format is pod:pvc.
