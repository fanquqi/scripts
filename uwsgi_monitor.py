# Do NOT modify this file by hand!
import socket
import json
import sys
from op_tools import falcon

project_or_socket = "medweb"

uwsgi_map = {}

uwsgi_map['medweb']='/home/.../uwsgi_stats.socket'
uwsgi_map['cmsapi']='/tmp/stats_cmsapi.socket'

addr = uwsgi_map.get(project_or_socket, project_or_socket)
data_type = "busy"

sfamily = socket.AF_UNIX
s = socket.socket(sfamily, socket.SOCK_STREAM)
s.connect(addr)

js = ""

while True:
    data = s.recv(4096)
    if len(data) < 1:
        break
    js += data.decode('utf8')

dd = json.loads(js)
workers = dd["workers"]
busy_count = 0
total_count = len(workers)

for worker in workers:
   if worker["status"] == "busy":
       busy_count += 1

busy_rate = busy_count/float(total_count or 1)


dic_count = {
    'busy_count' : busy_count,
    'busy_rate' : busy_rate,
    'total_count' : total_count,
    }

metric = "medweb_uwsgi_busy_worker"
collect_step = 60
counter_type = falcon.CounterType.GAUGE

for key  in dic_count:
    tag = "type=" + key

    value = dic_count.get(key)
    info = falcon.build_metric_info(metric, value, collect_step, counter_type, tags=tag)
    print info
    falcon.push_metric_info_list_to_falcon([info])
