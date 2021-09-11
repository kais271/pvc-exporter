import os
import re
import time
import logging

from prometheus_client import start_http_server, Gauge
g=Gauge('pv_usage','fetching pvc usge matched by k8s csi',['volumename'])
#set metrics
start_http_server(8848)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('block_pvc_scanner')
logger.setLevel(logging.DEBUG)
print_log = logging.StreamHandler()
print_log.setFormatter(formatter)
logger.addHandler(print_log)

def get_pv_usage(pvc_info):
  for pv_usage in pvc_info:
    #get pvc usgae
    if re.match("^[0-9]*\%",pv_usage):
      pv_usage=float(pv_usage.strip('%'))/100.0
      logger.info(f'VOLUME: {pv}, USAGE: {pv_usage}')
      g.labels(pv).set(pv_usage)
  return 

while 1:
  get_pvc=os.popen("df -h|grep -E 'kubernetes.io/flexvolume|kubernetes.io~csi|kubernetes.io/gce-pd/mounts'")
  all_pvcs=get_pvc.readlines()
  if(len(all_pvcs) == 0):
    logger.warning("No block storage pvc found or not supported yet.")
  else:
    for pvc in all_pvcs:
      #get pvc name
      pvc_info=pvc.split(' ')
      volume=pvc_info[-1].split('/')[-1]
      if re.match("^pvc",volume):
        pv=volume
        get_pv_usage(pvc_info)
      elif re.match("^gke-data",volume):
        pv='pvc'+volume.split('pvc')[-1]
        get_pv_usage(pvc_info)
      else:
        logger.error(f'Canot match this volume: {volume}')
  logger.info("Will sleep 15s...")
  time.sleep(15)