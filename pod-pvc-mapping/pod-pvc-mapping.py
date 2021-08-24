from kubernetes import client, config
from prometheus_client import start_http_server, Gauge
import time
import logging
start_http_server(8849)
g=Gauge('pvc_mapping','fetching the mapping between pod and pvc',['persistentvolumeclaim','volumename','mountedby'])

pool={}

logger = logging.getLogger('pod_pvc_mapping')

def get_items(obj):
  format=obj.to_dict()
  items=format['items']
  return items

while 1:
  config.load_incluster_config()
  k8s_api_obj = client.CoreV1Api()
  nss=get_items(k8s_api_obj.list_namespace())
  for i in nss:
  #list all pods and pvcs
    ns=i['metadata']['name']
    pods=get_items(k8s_api_obj.list_namespaced_pod(ns))
    pvcs=get_items(k8s_api_obj.list_namespaced_persistent_volume_claim(ns))
    for po in pods:
      pod_name=po['metadata']['name']
      for vol in po['spec']['volumes']:
      #find pvc in pod
        if vol['persistent_volume_claim']:
          mounted_pvc=vol['persistent_volume_claim']['claim_name']
          for pvc in pvcs:
          #mapping pvc to pv
            if pvc['metadata']['name'] == mounted_pvc:
              vol_name=pvc['spec']['volume_name']
          #pod_name=po['metadata']['name']
          logger.info(f'Found --> NS: {ns}, PVC: {mounted_pvc}, VOLUME: {vol_name}, POD: {pod_name}')
          if mounted_pvc in pool.keys():
          #update mapping
            g.remove(mounted_pvc,pool[mounted_pvc][0],pool[mounted_pvc][1])
            g.labels(mounted_pvc,vol_name,pod_name)
            pool[mounted_pvc]=[vol_name,pod_name]
          else:
            g.labels(mounted_pvc,vol_name,pod_name)
            pool[mounted_pvc]=[vol_name,pod_name]
        else:
          logger.info(f'Not found mounted pvc on {pod_name} in namespace {ns}.')
  time.sleep(15)
