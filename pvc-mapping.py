from kubernetes import client
from prometheus_client import start_http_server, Gauge
from time import sleep
start_http_server(8849)
g=Gauge('pvc_mapping','fetching the mapping between pod and pvc',['persistentvolumeclaim','mountedby'])
while 1:
    ApiToken = "kubeconfig-user-ngbzm.c-twwkt:wsq5bjl8fjd6hd45fh4p5ldbls2lplpl6m4zdqw84cw6529nxtwbwb"
    configuration = client.Configuration()
    setattr(configuration, 'verify_ssl', False)
    client.Configuration.set_default(configuration)
    configuration.host = "https://rancher.ks.com/k8s/clusters/c-twwkt"
    configuration.verify_ssl = False
    configuration.debug = True
    configuration.api_key = {"authorization": "Bearer " + ApiToken}
    client.Configuration.set_default(configuration)
    k8s_api_obj  = client.CoreV1Api(client.ApiClient(configuration))
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
                    g.labels(pvc,pod).set(1)
    sleep(30)

