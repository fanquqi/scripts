import os
from op_tools import falcon

def send_message_to_falcon():

    value = os.system("ping -c 1 baidu.com > /dev/null 2>&1")
    collect_step = 60
    counter_type = falcon.CounterType.GAUGE
    metric = "web_connect"
    tags = "ping"
    metric_info_list = []
    metric_info_list.append(falcon.build_metric_info(metric, value, collect_step, counter_type, tags=tags))
    falcon.push_metric_info_list_to_falcon(metric_info_list)

if __name__ == '__main__':
    send_message_to_falcon()
