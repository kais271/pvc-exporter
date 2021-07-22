from kubernetes import client, config
from prometheus_client import start_http_server, Gauge
from time import sleep
import argparse, os, re, time

# Parse commandline arguments
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--debug", action='store_true')
parser.add_argument("-s", "--scanner", action='store_true')
parser.add_argument("-m", "--mapper", action='store_true')
parser.add_argument("-p", "--port", type=int, default=8089, help="Port to expose prometheus metrics")
parser.add_argument("-i", "--interval", type=int, default=10, help="Interval for pulling host system")
args = parser.parse_args()

#
# Main Program
#
def main():
  # Check args valid
  if not args.scanner and not args.mapper:
    print("You must define at least the scanner or mapper argument")
    exit(1)

  # Execute scanner task
  if args.scanner:
    _debug("Starting scanner task")
    g=Gauge('pvc_usage','fetching usge matched by k8s csi',['volumename'])
    start_http_server(args.port)
    while 1:
      _debug("Get mounts by command")
      get_pvc=os.popen("df -h|grep -E 'kubernetes.io/flexvolume|kubernetes.io~csi|kubernetes.io/gce-pd/mounts'")
      pvcs=get_pvc.readlines()
      for i in pvcs:
        _debug("Process line: %s" % i)
        il=i.split(' ')
        volume=il[-1].split('/')[-1]
        for v in il[-1].split('/'):
          if re.match("^pvc",v):
            volume=v
          elif re.match("^gke-data",v):
            volume='pvc'+v.split('pvc')[-1]
        for u in il:
          if re.match("^[0-9]*\%",u):
            usage=float(u.strip('%'))/100.0
            #pvc_usage[volume]=usage
            _debug("Volume: %s, Usage: %s" % (volume,usage))
            g.labels(volume).set(usage)
      sleep(args.interval)

  # Execute mapping task
  if args.mapper:
    _debug("Starting scanner task")
    start_http_server(args.port)
    g=Gauge('pvc_mapping','fetching the mapping between pod and pvc',['persistentvolumeclaim','volumename','mountedby'])
    pool={}
    def get_items(obj):
      format=obj.to_dict()
      items=format['items']
      return items
    while 1:
      config.load_incluster_config()
      k8s_api_obj = client.CoreV1Api()
      nss=get_items(k8s_api_obj.list_namespace())
      for i in nss:
        ns=i['metadata']['name']
        pods=get_items(k8s_api_obj.list_namespaced_pod(ns))
        pvcs=get_items(k8s_api_obj.list_namespaced_persistent_volume_claim(ns))
        _debug("Process %s pods in namespace %s" % (len(pods), i))
        for p in pods:
          for vc in p['spec']['volumes']:
            if vc['persistent_volume_claim']:
              pvc=vc['persistent_volume_claim']['claim_name']
              for v in pvcs:
                if v['metadata']['name'] == pvc:
                  vol=v['spec']['volume_name']
              pod=p['metadata']['name']
              _debug("PVC: %s, VOLUME: %s, POD: %s" % (pvc,vol,pod))
              if pvc in pool.keys():
                g.remove(pvc,pool[pvc][0],pool[pvc][1])
                g.labels(pvc,vol,pod)
                pool[pvc]=[vol,pod]
              else:
                g.labels(pvc,vol,pod)
                pool[pvc]=[vol,pod]
      sleep(args.interval)

#
# Helpers
#
def _debug(msg):
  if args.debug == True:
    print('DEBUG - ' + time.strftime("%H:%M:%S") + ': ' + str(msg))

# Main
if __name__ == "__main__":
    main()
