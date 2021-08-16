from time import sleep

from kubernetes import client, config
from prometheus_client import start_http_server, Gauge

start_http_server(8849)
g = Gauge('pvc_mapping', 'fetching the mapping between pod and pvc',
          ['persistentvolumeclaim', 'volumename', 'mountedby'])

pool = {}


def get_items(obj):
    return obj.to_dict()['items']


while 1:
    config.load_incluster_config()
    k8s_api_obj = client.CoreV1Api()
    nss = get_items(k8s_api_obj.list_namespace())
    for i in nss:
        ns = i['metadata']['name']
        pods = get_items(k8s_api_obj.list_namespaced_pod(ns))
        pvcs = get_items(k8s_api_obj.list_namespaced_persistent_volume_claim(ns))
        for p in pods:
            for vc in p['spec']['volumes']:
                if vc['persistent_volume_claim']:
                    pvc = vc['persistent_volume_claim']['claim_name']
                    vol = None
                    for v in pvcs:
                        if v['metadata']['name'] == pvc:
                            vol = v['spec']['volume_name']
                    pod = p['metadata']['name']
                    if vol is not None:
                        print("PVC: %s, VOLUME: %s, POD: %s" % (pvc, vol, pod))
                    else:
                        print("PVC: %s, POD %s, VOLUME was undefined" % (pvc, pod))
                    if pvc in pool.keys():
                        g.remove(pvc, pool[pvc][0], pool[pvc][1])
                        g.labels(pvc, vol, pod)
                        pool[pvc] = [vol, pod]
                    else:
                        g.labels(pvc, vol, pod)
                        pool[pvc] = [vol, pod]
    sleep(15)
