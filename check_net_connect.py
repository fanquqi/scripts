#!/usr/bin/python
from op_tools import falcon
import commands

ALL_CONNECT=commands.getoutput("netstat -an | grep 'tcp\|udp' | wc -l")
ESTABLISHED=commands.getoutput("netstat -an | grep ESTABLISHED  | awk '/^tcp/ {++S[$NF]} END {for(a in S) print S[a]}'")

SYN_SENT=commands.getoutput("netstat -an | grep SYN_SENT  | awk '/^tcp/ {++S[$NF]} END {for(a in S) print S[a]}'")

TIME_WAIT=commands.getoutput("netstat -an | grep TIME_WAIT | awk '/^tcp/ {++S[$NF]} END {for(a in S) print S[a]}'")

SOCKET_OPEN=commands.getoutput("head -n 1 /proc/net/sockstat  | awk '{print $3}'")

FD_OP=commands.getoutput("ls -l /proc/*/fd | wc -l")
FD_OP_NUM=FD_OP.split("\n")[-1]

collect_step = 600
counter_type = falcon.CounterType.GAUGE
metric = "connect_status"

metric_get_func = {
        'ALL_CONNECT': ALL_CONNECT,
        'ESTABLISHED_CONNECT': ESTABLISHED,
        'SYN_SENT_CONNECT': SYN_SENT,
        'TIME_WAIT_CONNECT': TIME_WAIT,
        'SOCKET_OPEN': SOCKET_OPEN,
        'FD_OPEN_NUM': FD_OP_NUM,
        }

info_list=[]

for key in metric_get_func:
    tag = "type=" + key
    value = metric_get_func.get(key)
    info_list.append(falcon.build_metric_info(metric, value, collect_step, counter_type, tags=tag))

falcon.push_metric_info_list_to_falcon(info_list)
