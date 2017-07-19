#!/usr/bin/python
# -*- encoding:utf-8 -*-

""" Check Zookeeper Cluster
ZooKeeperServer Download from http://john88wang.blog.51cto.com/2165294/1745339
Modified by xiaxianzhi
zookeeper version should be newer than 3.4.x

# echo mntr|nc 127.0.0.1 2181
zk_version  3.4.6-1569965, built on 02/20/2014 09:09 GMT
zk_avg_latency  0
zk_max_latency  4
zk_min_latency  0
zk_packets_received 84467
zk_packets_sent 84466
zk_num_alive_connections    3
zk_outstanding_requests 0
zk_server_state follower
zk_znode_count  17159
zk_watch_count  2
zk_ephemerals_count 1
zk_approximate_data_size    6666471
zk_open_file_descriptor_count   29
zk_max_file_descriptor_count    102400

# echo ruok|nc 127.0.0.1 2181
imok

"""
import json
import sys
import os
import socket
import subprocess
from StringIO import StringIO

from kazoo.client import KazooClient
from op_tools import falcon

DASHBOARD_ZK_HOSTS = "zk_rpc_1:2181,zk_rpc_2:2181,zk_rpc_3:2181"
zoo_dashboard_nodes_path = "/zk/product/infra/services"
is_send_to_zabbix = 1

FNULL = open(os.devnull, 'w')


class ZookeeperServer(object):
    def __init__(self, hosts="127.0.0.1:2181", timeout=1):
        self._result = {}
        self.hosts = hosts
        self.zk = KazooClient(hosts=hosts, timeout=timeout)
        self.zk.start()

    def __del__(self):
        self.zk.stop()

    def clean_dashboard_node(self, cluster_name, hostname):
        path = "%s/zookeeper@%s/%s" % (zoo_dashboard_nodes_path, cluster_name, hostname)
        self.zk.delete(path, recursive=True)
        #self.zk.ensure_path(zoo_dashboard_nodes_path)

    def get_info(self, commands):
        result = {}
        for cmd in commands:
            data = self.zk.command(cmd)
            result.update(self._parse(data))
        return result

    def get_stats(self):
        """ Get ZooKeeper server stats as a map """
        self._result = self.get_info(['mntr'])
        data = self.zk.command('ruok')
        self._result.update(self._parse_ruok(data))
        if not self._result.has_key('zk_followers') and not self._result.has_key(
                'zk_synced_followers') and not self._result.has_key('zk_pending_syncs'):
            # the tree metrics only exposed on leader role zookeeper server, we just set the followers' to 0
            leader_only = {'zk_followers': 0, 'zk_synced_followers': 0, 'zk_pending_syncs': 0}
            self._result.update(leader_only)
        return self._result



    def _parse(self, data):
        """ Parse the output from the 'mntr' 4letter word command """
        result = {}
        if not data:
            return result
        h = StringIO(data)
        for line in h.readlines():
            try:
                key, value = self._parse_line(line)
                result[key] = value
            except ValueError:
                pass  # ignore broken lines

        return result

    def _parse_ruok(self, data):
        """ Parse the output from the 'ruok' 4letter word command """

        result = {'zk_server_ruok': ''}
        if not data:
            return result
        h = StringIO(data)
        ruok = h.readline()
        result['zk_server_ruok_status'] = 0
        if ruok:
            result['zk_server_ruok'] = ruok

            result['zk_server_ruok_status'] = 1
            return result
        else:

            return result

    def _parse_line(self, line):
        try:
            key, value = map(unicode.strip, line.split('\t'))
        except ValueError:
            key, value = map(unicode.strip, line.split('='))
        except ValueError:
            raise ValueError('Found invalid line: %s' % line)

        if not key:
            raise ValueError('The key is mandatory and should not be empty')

        try:
            value = int(value)
        except (TypeError, ValueError):
            pass

        return key, value

    def add_dashboard_node(self, cluster_name, hostname, stats):
        path = "%s/zookeeper@%s/%s" % (zoo_dashboard_nodes_path, cluster_name, hostname)
        self.zk.ensure_path(path)
        self.zk.set(path, json.dumps(stats))


if __name__ == '__main__':

    collect_step = 60
    counter_type = falcon.CounterType.GAUGE


    try:
        cluster_name = sys.argv[1]
        zk_hostname = sys.argv[2] if len(sys.argv) > 2 else ''
        zk_server = ZookeeperServer()
        stats = zk_server.get_stats()
        dashboard_server = ZookeeperServer(DASHBOARD_ZK_HOSTS)
        hostname = socket.gethostname()
        dashboard_server.clean_dashboard_node(cluster_name, hostname)

        metric_info_list = []
        for key, value in stats.iteritems():
            metric = "zookeeper_status"
            tags = "type=" + key + ",cluster_name=" + cluster_name
            metric_info_list.append(falcon.build_metric_info(metric, value, collect_step, counter_type, tags=tags))

        # 发送指标到falcon
        falcon.push_metric_info_list_to_falcon(metric_info_list)
        # 发送信息到rpc_dashboard
        result = zk_server.get_info(['conf', 'envi'])
        result["zk_server_state"] = stats["zk_server_state"]
        result["zk_server_ruok"] = stats["zk_server_ruok"]
        result["zk_hostname"] = zk_hostname
        result["cluster_name"] = cluster_name
        dashboard_server.add_dashboard_node(cluster_name, hostname, result)
    except:
        metric = "zookeeper_monitor"
        value = 0
        tags = "type=scripts_status"
        info = falcon.build_metric_info(metric, value, collect_step, counter_type, tags=tags)
        falcon.push_metric_info_list_to_falcon([info])
