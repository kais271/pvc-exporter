# PVC Exporter

[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg)](https://conventionalcommits.org)
[![Semantic Release](https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--release-e10079.svg)](https://github.com/semantic-release/semantic-release)
[![Docker Image](https://github.com/Mario-F/pvc-exporter/actions/workflows/docker.yml/badge.svg?branch=main)](https://github.com/Mario-F/pvc-exporter/pkgs/container/pvc-exporter)

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

## Usage

Using the helm chart simply with this commands:

```shell
helm repo add mariof-charts https://mario-f.github.io/helm-charts/
helm install kubevis mariof-charts/pve-exporter
```

## Grafana

You can import the [pvc_usage-dashboard](./docs/pvc_usage-dashboard.json) to grafana for monitoring pvc usage.
![grafana-1](./docs/grafana-1.PNG)
The legend format is pod:pvc.
