#!/bin/env python
# -*- coding:utf-8 -*-
"""
    代码来源: https://github.com/iambocai/falcon-monit-scripts/tree/master/redis
"""
import glob

__author__ = 'iambocai'

import json
import time
import socket
import os
import re
import sys
import commands
import urllib2


class RedisStats:
    # 如果你是自己编译部署到redis，请将下面的值替换为你到redis-cli路径
    _redis_clis = ["/usr/local/bin/redis-cli", '/usr/bin/redis-cli']
    _redis_cli = None

    _stat_regex = re.compile(ur'(\w+):([0-9]+\.?[0-9]*)\r')

    def __init__(self, port='6379', passwd=None, host='127.0.0.1'):

        for redis in self._redis_clis:
            if os.path.exists(redis):
                self._redis_cli = redis
                break

        if passwd not in ['', None]:
            self._cmd = "%s -h %s -p %s -a %s info" % (self._redis_cli, host, port, passwd)
        else:
            self._cmd = '%s -h %s -p %s info' % (self._redis_cli, host, port)

    def stats(self):
        ' Return a dict containing redis stats '
        info = commands.getoutput(self._cmd)
        return dict(self._stat_regex.findall(info))


def main():
    ip = socket.gethostname()
    timestamp = int(time.time())
    step = 60
    # inst_list中保存了redis配置文件列表，程序将从这些配置中读取port和password，建议使用动态发现的方法获得，如：
    # inst_list = [ i for i in commands.getoutput("find  /etc/ -name 'redis*.conf'" ).split('\n') ]

    # 假定存在目录:
    #
    pattern = "/home/chunyu/redis/*redis*.conf"
    insts_list = glob.glob(pattern)

    p = []

    monit_keys = [
        ('connected_clients', 'GAUGE'),
        ('blocked_clients', 'GAUGE'),
        ('used_memory', 'GAUGE'),
        ('used_memory_rss', 'GAUGE'),
        ('mem_fragmentation_ratio', 'GAUGE'),
        ('total_commands_processed', 'COUNTER'),
        ('rejected_connections', 'COUNTER'),
        ('expired_keys', 'COUNTER'),
        ('evicted_keys', 'COUNTER'),
        ('keyspace_hits', 'COUNTER'),
        ('keyspace_misses', 'COUNTER'),
        ('keyspace_hit_ratio', 'GAUGE'),
    ]

    for inst in insts_list:
        # 对于每一个实例， 从配置文件中读取端口，密码等信息
        port = commands.getoutput("sed -n 's/^port *\([0-9]\{4,5\}\)/\\1/p' %s" % inst)
        passwd = commands.getoutput("sed -n 's/^requirepass *\([^ ]*\)/\\1/p' %s" % inst)
        metric = "redis"
        endpoint = ip
        redis_name = inst.split("/")[4].split("_")[0]
        tags = 'port=%s,name=%s' % (port,redis_name)

        try:
            conn = RedisStats(port, passwd)
            stats = conn.stats()
        except Exception, e:
            continue

        for key, vtype in monit_keys:
            if key == 'keyspace_hit_ratio':
                try:
                    value = float(stats['keyspace_hits']) / (
                        int(stats['keyspace_hits']) + int(stats['keyspace_misses']))
                except ZeroDivisionError:
                    value = 0
            elif key == 'mem_fragmentation_ratio':
                value = float(stats[key])
            else:
                try:
                    value = int(stats[key])
                except:
                    continue

            i = {
                'Metric': '%s.%s' % (metric, key),
                'Endpoint': endpoint,
                'Timestamp': timestamp,
                'Step': step,
                'Value': value,
                'CounterType': vtype,
                'TAGS': tags
            }
            p.append(i)

    print json.dumps(p, sort_keys=True, indent=4)
    method = "POST"
    handler = urllib2.HTTPHandler()
    opener = urllib2.build_opener(handler)
    url = 'http://127.0.0.1:1988/v1/push'
    request = urllib2.Request(url, data=json.dumps(p))
    request.add_header("Content-Type", 'application/json')
    request.get_method = lambda: method
    try:
        connection = opener.open(request)
    except urllib2.HTTPError, e:
        connection = e

    # check. Substitute with appropriate HTTP code.
    if connection.code == 200:
        print connection.read()
    else:
        print '{"err":1,"msg":"%s"}' % connection


if __name__ == '__main__':
    proc = commands.getoutput(' ps -ef|grep %s|grep -v grep|wc -l ' % os.path.basename(sys.argv[0]))
    if int(proc) < 5:
        main()
