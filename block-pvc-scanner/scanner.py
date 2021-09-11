import os
import re
import time
import logging

from prometheus_client import start_http_server, Gauge
g=Gauge('pvc_usage','fetching pvc usge matched by k8s csi',['volumename'])
#set metrics
start_http_server(8848)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('block_pvc_scanner')
logger.setLevel(logging.DEBUG)
print_log = logging.StreamHandler()
print_log.setFormatter(formatter)
logger.addHandler(print_log)

while 1:
  get_pvc=os.popen("df -h|grep -E 'kubernetes.io/flexvolume|kubernetes.io~csi|kubernetes.io/gce-pd/mounts'")
  all_pvcs=get_pvc.readlines()
  if(len(all_pvcs) == 0):
    logger.warning("Not block storage pvc found or not supported yet.")
  for pvc in all_pvcs:
    #get pvc name
    pvc_info=pvc.split(' ')
    volume=pvc_info[-1].split('/')[-1]
    for gke_pvc in pvc_info[-1].split('/'):
      if re.match("^pvc",gke_pvc):
        volume=gke_pvc
      elif re.match("^gke-data",gke_pvc):
        volume='pvc'+gke_pvc.split('pvc')[-1]
     
    for pvc_usage in pvc_info:
      #get pvc usgae
      if re.match("^[0-9]*\%",pvc_usage):
        pvc_usage=float(pvc_usage.strip('%'))/100.0
        logger.info(f'VOLUME: {volume}, USAGE: {pvc_usage}')
        g.labels(volume).set(pvc_usage)

  time.sleep(15)
