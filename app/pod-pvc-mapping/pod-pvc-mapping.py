from kubernetes import client, config
from prometheus_client import start_http_server, Gauge
import time
import logging
import traceback

start_http_server(8849)
g=Gauge('pvc_mapping','fetching the mapping between pod and pvc',['persistentvolumeclaim','volumename','mountedby','pod_namespace'])

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('pod_pvc_mapping')
logger.setLevel(logging.DEBUG)
print_log = logging.StreamHandler()
print_log.setFormatter(formatter)
logger.addHandler(print_log)

pool={}

def get_items(obj):
  format=obj.to_dict()
  items=format['items']
  return items
  
def get_name_ns_pv(item):
  name=item['metadata']['name']
  ns=item['metadata']['namespace']
  pv=item['spec']['volume_name']
  return name,ns,pv


while 1:
  config.load_incluster_config()
  k8s_api_obj = client.CoreV1Api()
  all_pvc=get_items(k8s_api_obj.list_persistent_volume_claim_for_all_namespaces())
  if len(all_pvc)==0:
    logger.warning("No pvc found in this cluster.")
  else:
    pool_pvc={}
    for pvc in all_pvc:
    #pvc_ns as key,list all pvc per ns
      pvc_name,pvc_ns,pvc_pv=get_name_ns_pv(pvc)
      try:
        len(pool_pvc[pvc_ns])
      except KeyError:
        pool_pvc[pvc_ns]=[{pvc_name:pvc_pv}]
      except:
        traceback.print_exc()
      else:
        pool_pvc[pvc_ns].append({pvc_name:pvc_pv})
    for ns in pool_pvc.keys():
    #query pod spec for ns that have pvc
      pods=get_items(k8s_api_obj.list_namespaced_pod(ns))
      for po in pods:
        pod_name=po['metadata']['name']
        try:
          for vol in po['spec']['volumes']:
          #find pvc in pod
            if vol['persistent_volume_claim']:
              mounted_pvc=vol['persistent_volume_claim']['claim_name']
              for pvc in pool_pvc[ns]:
              #mapping pvc to pv
                if mounted_pvc in pvc.keys():
                  pv_name=pvc[mounted_pvc]
              logger.info(f'Found --> NS: {ns}, PVC: {mounted_pvc}, VOLUME: {pv_name}, POD: {pod_name}')
              id_key=mounted_pvc+'-'+ns
              if id_key in pool.keys():
              #update mapping
                g.remove(pool[id_key][0],pool[id_key][1],pool[id_key][2],pool[id_key][3])
                g.labels(mounted_pvc,pv_name,pod_name,ns)
                pool[id_key]=[mounted_pvc,pv_name,pod_name,ns]
              else:
                g.labels(mounted_pvc,pv_name,pod_name,ns)
                pool[id_key]=[mounted_pvc,pv_name,pod_name,ns]
        except:
          logger.error(f'Cannot resolve the spec for this pod: {pod_name}')
          traceback.print_exc()
  logger.info("Will sleep 15s...")
  time.sleep(15)
