import os
import re
import time
import logging
import traceback
from kubernetes import client, config
from prometheus_client import start_http_server, Gauge

EXPORTER_SERVER_PORT=int(os.getenv('EXPORTER_SERVER_PORT'))
SCAN_INTERVAL=float(os.getenv('SCAN_INTERVAL'))
HOST_IP=os.getenv('HOST_IP')

#start metrics server
start_http_server(EXPORTER_SERVER_PORT)

#Provide 2 metric: pvc_usage, pvc_mapping
metric_pvc_usage=Gauge('pvc_usage','The value is PVC usage percent that equal to pvc_used_MB/pvc_requested_size_MB',
['persistentvolumeclaim','persistentvolume','pvc_namespace','pvc_used_MB','pvc_requested_size_MB','pvc_requested_size_human','pvc_type'])
metric_pvc_mapping=Gauge('pvc_mapping','Fetching the mapping between pvc and pod',
['persistentvolumeclaim','persistentvolume','mountedby','pod_namespace','host_ip'])

#Initialize the logging
formatter=logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger=logging.getLogger('pvc-exporter')
logger.setLevel(logging.DEBUG)
print_log=logging.StreamHandler()
print_log.setFormatter(formatter)
logger.addHandler(print_log)


def get_items(obj):
  #format api response
  format=obj.to_dict()
  items=format['items']
  return items
  
def get_pvc_info(pvc):
  name=pvc['metadata']['name']
  ns=pvc['metadata']['namespace']
  pv=pvc['spec']['volume_name']
  size=pvc['spec']['resources']['requests']['storage']
  return name,ns,pv,size

def unit_conversion(size):
  units=['B','K','M','G','T','P']
  rex=r'^[0-9]+(\.?[0-9]+)?%s'%(units)
  try:
    get_size=re.match(rex,size).group()
    if get_size:
      unit=get_size[-1]
      num=get_size.split(unit)[0]
      if unit=='M':
        MB_size=round(float(num),2)
      else:
        n=units.index(unit)-2
        MB_size=round(float(num)*pow(1024,n),2)
      if len(num) > 3:
        exp=len(num)//3
        human_num=round(float(num)/pow(1024,exp),2)
        human_unti=units[units.index(unit)+exp]
        human_size=str(human_num)+human_unti
      else:
        human_num=num
        human_unti=unit
        human_size=str(human_num)+human_unti
      return human_size,MB_size
    else:
      logger.warning(f'Not found expected info for this string: {size}')
  except:
    traceback.print_exc()
    logger.warning(f'Not found expected info for this string: {size}')


def calculate_size(fs_path,total_MB_size,pvc_type):
  if pvc_type == 'block':
    pv_st=os.statvfs(fs_path)
    pvc_used=str((pv_st.f_blocks - pv_st.f_bfree) * pv_st.f_frsize)+'B'
    human_size,MB_size=unit_conversion(pvc_used)
    pvc_used=MB_size
    pvc_used_percent=round(float((pv_st.f_blocks - pv_st.f_bfree) * pv_st.f_frsize) / (pv_st.f_blocks * pv_st.f_frsize),2) + 0.01
    #+0.01 to amend 
  else:
    get_pvc_used="du -sm %s"%(fs_path)
    pvc_used=os.popen(get_pvc_used).readlines()[0].split('\t')[0]
    pvc_used_percent=round(float(pvc_used) / total_MB_size,2) + 0.01
    #+0.01 to amend 
  return pvc_used,pvc_used_percent

def get_pvc_used(pv_info,total_MB_size):
  '''
  Get pvc usage.
  The method is to mount the host path to the container, and then get the information.
  '''
  pv_name=pv_info.metadata.name
  if pv_info.spec.nfs:
    #Get nfs pvc
    pvc_type='nfs'
    nfs_pv_path=pv_info.spec.nfs.path
    cmd="df|grep /host|grep %s"%(pv_name)
    fs_info=os.popen(cmd).readlines()
    if len(fs_info)==1:
      fs_path=(fs_info[0].split(' ')[-1]).rstrip()
    pvc_used,pvc_used_percent=calculate_size(fs_path,total_MB_size,pvc_type)
  elif pv_info.spec.host_path:
    #Get hostpat pvc
    pvc_type='hostpath'
    host_pv_path=pv_info.spec.host_path.path
    fs_path=('/host'+host_pv_path).rstrip()
    pvc_used,pvc_used_percent=calculate_size(fs_path,total_MB_size,pvc_type)
  else:
    #Get block PVC
    pvc_type='block'
    block_pvc_rex=re.compile(r'kubernetes.io/flexvolume|kubernetes.io~csi|kubernetes.io/gce-pd/mounts')
    try:
      mtab=open('/etc/mtab','r')
      read_mtab=mtab.readlines()
      mtab.close()
      check_block=[]
      for mp in read_mtab:
        if pv_name in mp and block_pvc_rex.search(mp):
          check_block.append(mp)
      if len(check_block) != 1:
        raise
      else:
        fs_path=((check_block[0]).split(' ')[1]).rstrip()
        total_MB_size
        pvc_used,pvc_used_percent=calculate_size(fs_path,total_MB_size,pvc_type)
    except:
      logger.error(f'Cannot resovle this pv {pv_name}')
      traceback.print_exc()
  return pvc_used,pvc_used_percent,pvc_type

pool={}
'''
Maintain a resource pool that for update the mapping between pvc and pod.
PVC --> POD:
  One-to-One
  One-to-Many
  Many-to-One
  Many-to-Many
'''

while 1:
  config.load_incluster_config()
  k8s_api_obj=client.CoreV1Api()
  all_pvc=get_items(k8s_api_obj.list_persistent_volume_claim_for_all_namespaces())
  if len(all_pvc)==0:
    logger.warning("No pvc found in this cluster.")
  else:
    pool_pvc={}
    for pvc in all_pvc:
    #pvc_ns as key,list all pvc per ns
      pvc_name,pvc_ns,pvc_pv,pvc_size=get_pvc_info(pvc)
      try:
        len(pool_pvc[pvc_ns])
      except KeyError:
        pool_pvc[pvc_ns]=[{pvc_name:[pvc_pv,pvc_size]}]
      except:
        traceback.print_exc()
      else:
        pool_pvc[pvc_ns].append({pvc_name:[pvc_pv,pvc_size]})
    for ns in pool_pvc.keys():
    #query pod spec for ns that have pvc
      pods=get_items(k8s_api_obj.list_namespaced_pod(ns))
      for po in pods:
        pod_name=po['metadata']['name']
        pod_host_ip=k8s_api_obj.read_namespaced_pod(pod_name,ns).status.host_ip
        if pod_host_ip == HOST_IP:
          #if this pod on current host, then try to get pod info
          try:
            for vol in po['spec']['volumes']:
            #find pvc in pod
              if vol['persistent_volume_claim']:
                mounted_pvc=vol['persistent_volume_claim']['claim_name']
                for pvc in pool_pvc[ns]:
                #mapping pvc to pv
                  if mounted_pvc in pvc.keys():
                    #Confirm pvc again
                    pv_name=pvc[mounted_pvc][0]
                    size=pvc[mounted_pvc][1]
                    pvc_requested_size_human,pvc_requested_size_MB=unit_conversion(size)
                    host_ip=k8s_api_obj.read_namespaced_pod(pod_name,ns).status.host_ip
                    pv_info=k8s_api_obj.read_persistent_volume(pv_name)
                    pvc_used_MB,pvc_used_percent,pvc_type=get_pvc_used(pv_info,pvc_requested_size_MB)
                    logger.info(f'Found --> NS: {ns}, PVC: {mounted_pvc}, PV: {pv_name}, PVC_TYPE: {pvc_type}, POD: {pod_name}, HOST_IP: {host_ip}, SIZE: {pvc_requested_size_MB}, USED: {pvc_used_MB}, PERCENT: {pvc_used_percent}')
                    '''
                    Start to set metrics values and updating the mapping.
                    Index for pool:
                      0-mounted_pvc
                      1-pv_name
                      2-pvc_requested_size_MB
                      3-pvc_requested_size_human
                      4-pvc_used_MB
                      5-pvc_used_percent
                      6-pvc_type
                      7-pod_name
                      8-ns
                      9-host_ip
                    '''
                    id_key=mounted_pvc+'-'+ns
                    if id_key in pool.keys():
                      metric_pvc_usage.remove(pool[id_key][0],pool[id_key][1],pool[id_key][8],pool[id_key][4],pool[id_key][2],pool[id_key][3],pool[id_key][6])
                      metric_pvc_usage.labels(mounted_pvc,pv_name,ns,pvc_used_MB,pvc_requested_size_MB,pvc_requested_size_human,pvc_type).set(pvc_used_percent)
                      metric_pvc_mapping.remove(pool[id_key][0],pool[id_key][1],pool[id_key][7],pool[id_key][8],pool[id_key][9])
                      metric_pvc_mapping.labels(mounted_pvc,pv_name,pod_name,ns,host_ip)
                      pool[id_key]=[mounted_pvc,pv_name,pvc_requested_size_MB,pvc_requested_size_human,pvc_used_MB,pvc_used_percent,pvc_type,pod_name,ns,host_ip]
                    else:
                      metric_pvc_usage.labels(mounted_pvc,pv_name,ns,pvc_used_MB,pvc_requested_size_MB,pvc_requested_size_human,pvc_type).set(pvc_used_percent)
                      metric_pvc_mapping.labels(mounted_pvc,pv_name,pod_name,ns,host_ip)
                      pool[id_key]=[mounted_pvc,pv_name,pvc_requested_size_MB,pvc_requested_size_human,pvc_used_MB,pvc_used_percent,pvc_type,pod_name,ns,host_ip]

          except:
            logger.error(f'Cannot resolve the spec for this pod: {pod_name}')
            traceback.print_exc()
  logger.info("Will sleep ...")
  time.sleep(SCAN_INTERVAL)