from kubernetes import client, config
from prometheus_client import start_http_server, Gauge
from time import sleep
start_http_server(8849)
g=Gauge('pvc_mapping','fetching the mapping between pod and pvc',['persistentvolumeclaim','mountedby'])
pool={}
while 1:
    config.load_incluster_config()
    k8s_api_obj = client.CoreV1Api()
    ret=k8s_api_obj.list_namespace()
    ret=ret.to_dict()
    ret=ret['items']
    for i in ret:
        na=i['metadata']['name']
        print(na)
        pods=k8s_api_obj.list_namespaced_pod(na)
        pods=pods.to_dict()
        pods=pods['items']
        for p in pods:
            for v in p['spec']['volumes']:
                if v['persistent_volume_claim']:
                    pvc=v['persistent_volume_claim']['claim_name']
                    pod=p['metadata']['name']
                    print(pvc,pod)
                    #g.labels(pvc,pod).set(1)
                    if pvc in pool.keys():
                        g.remove(pvc,pool[pvc])
                        g.labels(pvc,pod)
                        pool[pvc]=pod
                    else:
                        g.labels(pvc,pod)
                        pool[pvc]=pod
    sleep(30)

