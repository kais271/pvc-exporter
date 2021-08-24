import logging
import re
import time

import psutil
from prometheus_client import start_http_server, Gauge

logger = logging.getLogger('block_pvc_scanner')

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
        logger.warning("No mounted PVC found.")
    for mount_point in all_mount_points:
        # get pvc name
        mount_point_parts = mount_point.split('/')
        volume = mount_point_parts[-1]
        for possible_pvc in mount_point_parts:
            if pvc_re.match(possible_pvc):
                volume = possible_pvc
            elif gke_data_re.match(possible_pvc):
                volume = 'pvc' + possible_pvc.split('pvc')[-1]

        pvc_usage = psutil.disk_usage(mount_point).percent
        logger.info(f'VOLUME: {volume}, USAGE: {pvc_usage}')
        g.labels(volume).set(pvc_usage)
        labels.add(volume)

    for label in old_labels - labels:
        g.remove(label)
    old_labels = labels

    time.sleep(15)
