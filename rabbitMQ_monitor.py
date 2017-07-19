#-*- utf-8 -*-
#!/usr/bin/python
#author:fanquanqing
#used to monitor rabbitmq

import json
import socket
import urllib2
import requests
from op_tools import falcon



class RabbitMQApi(object):
    """
    class for rabbitmq management api
    """
    def __init__(self,username='guest', password='768768cyTX', protocol='http', port=15672, host_name='10.215.33.21'):
        self.username = username
        self.password = password
        self.protocol = protocol
        self.port = port
        self.host_name = host_name or socket.gethostname()
    def call_api(self,path):
        url = '{0}://{1}:{2}/api/{3}'.format(self.protocol, self.host_name, self.port, path)
        response = requests.get(url, auth=(self.username, self.password))
        response_list = response.json()
        return response_list

if __name__ == '__main__':
    api = RabbitMQApi(username='guest', password='768768cyTX',protocol='http',
                      port=15672, host_name='10.215.33.21')
    item_list = ['messages_ready','messages_unacknowledged','memory']
    vhost_list = ['medweb','pedometer','robot','file_upload']
    node_list = ['rabbit@rd1','rabbit@rd2']
    queue_select_list = []
    collect_step = 60
    counter_type = falcon.CounterType.GAUGE
    metric_info_list = []

    for queue in api.call_api('queues'):
        if queue.get('node') in node_list:
            if queue.get('vhost') in vhost_list:

                queue_select_list.append(queue)
    all_count=0
    for vhost in vhost_list:
        for item in item_list:
            for queue_select in queue_select_list:
                if "celeryev" not in queue_select["name"]:
                    metric = "rabbitMQ.%s" % item
                    tags = "queuenames=%s" % queue_select["name"]
                    value = queue_select.get(item)
                    metric_info_list.append(falcon.build_metric_info(metric, value, collect_step, counter_type, tags=tags))
                    if item=="messages_ready":
                        all_count = all_count + value
    all_queue_tag = u"all_queue_sum"
    metric_info_list.append(falcon.build_metric_info("rabbitMQ_messages_ready_all", all_count, collect_step, counter_type, tags=all_queue_tag))
    print all_count
    print metric_info_list
    falcon.push_metric_info_list_to_falcon(metric_info_list)
