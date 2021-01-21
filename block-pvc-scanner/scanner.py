import os,re,time
from prometheus_client import start_http_server, Gauge
g=Gauge('pvc_usage','fetching usge matched by k8s csi',['volumename'])
start_http_server(8848)
while 1:
  get_pvc=os.popen("df -h|grep -E 'kubernetes.io/flexvolume|kubernetes.io~csi'")
  pvcs=get_pvc.readlines()
  for i in pvcs:
    il=i.split(' ')
    volume=il[-1].split('/')[-1]
    for v in il[-1].split('/'):
      if re.match("^pvc",v):
        volume=v
    for u in il:
      if re.match("^[0-9]*\%",u):
        usage=float(u.strip('%'))/100.0
        #pvc_usage[volume]=usage
        print(volume,usage)
        g.labels(volume).set(usage)

  time.sleep(15)
