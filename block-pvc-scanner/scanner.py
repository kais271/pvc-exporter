import re
import time

import psutil
from prometheus_client import start_http_server, Gauge

g = Gauge('pvc_usage', "fetching pvc usage matched by k8s csi", ['volumename'])
# set metrics
start_http_server(8848)

supported_pvc_re = re.compile('^.+(kubernetes.io/flexvolume|kubernetes.io~csi|kubernetes.io/gce-pd/mounts).*$')
pvc_re = re.compile('^pvc')
gke_data_re = re.compile('^gke-data')


def filter_supported_pvcs(partition):
    if supported_pvc_re.match(partition.mountpoint):
        return True
    return False


old_labels = set()

while 1:
    labels = set()
    all_mount_points = list(map(lambda p: p.mountpoint, filter(filter_supported_pvcs, psutil.disk_partitions())))
    if len(all_mount_points) == 0:
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
              "Warning: Not found block storage pvc.")
    for mount_point in all_mount_points:
        # get pvc name
        mount_point_parts = mount_point.split('/')
        volume = mount_point_parts[-1]
        for gke_pvc in mount_point_parts:
            if pvc_re.match(gke_pvc):
                volume = gke_pvc
            elif gke_data_re.match(gke_pvc):
                volume = 'pvc' + gke_pvc.split('pvc')[-1]

        pvc_usage = psutil.disk_usage(mount_point).percent
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), volume, pvc_usage)
        g.labels(volume).set(pvc_usage)
        labels.add(volume)

    g.remove(old_labels - labels)
    old_labels = labels

    time.sleep(15)
