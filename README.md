# pvc-exporter
Only used to monitor mounted pvc that provied by block storage provisioner. Such as longgorn,trident,rook-ceph,etc..
This app will be create the following resoucres,and will be provide 2 metrics for mounted pvc, pvc_usage and pvc_mapping respectively.
  deployment
  daemonset
  serviceaccount
  clusterrole
  clusterrolebinding
  servicemonitor
  
# Install
kubectl apply -f namespace.yml -f rbac.yml -f deployment.yml -f daemonset.yml -f servicemonitor.yml

# Grafana

You can import the pvc_usage-dashboard to grafana to monitor pvc usage.
