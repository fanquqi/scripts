#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sdk import UcloudApiClient
from config import *
import sys
import json
import urllib2
import time
#from op_tools import falcon

#实例化 API 句柄
localtime = time.asctime( time.localtime(time.time()) )

def get_eip_info():
    '''
    获取EIP对应的主机名，以及EIP信息返回
    '''
    arg_length = len(sys.argv)
    ApiClient = UcloudApiClient(base_url, public_key, private_key)
    Parameters={"Action":"DescribeEIP", "Region":"cn-bj2"}
    response = ApiClient.get("/", Parameters );
    eip_info_list = response['EIPSet']
    eip_dic = {}
    for eip_info in eip_info_list:
        # EIP绑定主机名
        eip_host = eip_info['Resource']['ResourceName']
        eip_ip = eip_info['EIPAddr'][0]['IP'].encode('utf-8')
        eip_id = eip_info['EIPId']
        dic = {}
        dic[eip_ip] = eip_id
        #print "eip_host:%s,dic:%s" % (eip_host,dic)
        eip_dic[eip_host] = dic
    #print len(eip_dic)
    eip_dic['nginx-online1'] = {'106.75.28.177': u'eip-00gv0l'}
    return eip_dic

def get_eip_usage(eip_dic):
    '''
    获取每个EIP的实时用量(要求EIPid),
    return list:[{ip:usage}...]
    '''
    eip_usage_dic = {}
    for eip_host in eip_dic:
        #eip_useage_dic = {}
        eip_id=eip_dic[eip_host].values()[0].encode("utf-8")
        #print eip_id
        ApiClient = UcloudApiClient(base_url, public_key, private_key)
        Parameters={
                    "Action":"DescribeBandwidthUsage",
                    "Region":"cn-bj2",
                    "EIPIds.1":eip_id,
                }
        response = ApiClient.get("/", Parameters);
        #print json.dumps(response, sort_keys=True, indent=4, separators=(',', ': '))
        #print response
        eip_usage = response['EIPSet'][0]['CurBandwidth']
        eip_usage_dic[eip_host]=eip_usage
        #eip_usage_list.append(eip_useage_dic)
    return eip_usage_dic

def sendto_falcon(eip_usage_list):
    '''
    报警发送到falcon
    '''
    collect_step = 60
    counter_type = falcon.CounterType.GAUGE
    metric = "bandwidthusage"
    for eip_usage in eip_usage_list:
        tags="host=" + eip_usage.keys()[0]
        value=eip_usage.values()[0]
        #print value

def get_sharebw_info():
    '''
    获取共享带宽的带宽大小，以及所包含的EIP,
    return list:[{'eiplist':[ip1,ip1],'bandwidth':20}...]
    '''

    ApiClient = UcloudApiClient(base_url, public_key, private_key)
    Parameters={"Action":"DescribeShareBandwidth", "Region":"cn-bj2"}
    response = ApiClient.get("/", Parameters );
    #print json.dumps(response, sort_keys=True, indent=4, separators=(',', ': '))
    share_bw_list = response['DataSet']
    share_bw_info = []
    for share_bw in share_bw_list:
        share_bw_dic = {}
        bandwidth = share_bw['ShareBandwidth']
        eip_list = []
        for eip_dic in share_bw['EIPSet']:
            ip = eip_dic['EIPAddr'][0]['IP']
            eip_list.append(ip)
        share_bw_dic['bandwidth']=bandwidth
        share_bw_dic['eiplist']=eip_list
        share_bw_info.append(share_bw_dic)
    return share_bw_info

def sum():
    eip_dic = get_eip_info()
    #print eip_dic
    eip_to_host = {}
    # 通过eip_dic获取IP-host对此应关系dic
    for host in eip_dic:
        eip = eip_dic[host].keys()[0]
        eip_to_host[eip]=host
    #print eip_to_host
    eip_usage_dic = get_eip_usage(eip_dic)
    #print eip_usage_dic
    share_bw_info = get_sharebw_info()
    #print share_bw_info
    #各带宽和与带宽比值
    ratios = {}
    for share_bandwidth in share_bw_info:
        bandwidth = share_bandwidth['bandwidth']
        sum = 0
        for eip in share_bandwidth['eiplist']:
            host = eip_to_host[eip]
            usage = eip_usage_dic[host]
            sum += usage
        #带宽用量与带宽的比值
        ratio = sum/bandwidth
        parts = [str(bandwidth),str(sum),str(ratio)]
        log =localtime + ' ' + ','.join(parts) + '\n'
        with open('/var/log/ubandwidth.log','a') as f:
            f.write(log)
            f.close()

        ratios[bandwidth]=ratio

    return ratios


def send_to_dingtalk(content):

    url = "https://oapi.dingtalk.com/robot/send?access_token=17cf865229a63452ff411243b53d64949d5a54b1ee8774e20e1ec7d4c5d60f43"
    #con={"msgtype":"text","text":{"content":content},"isAtAll": "true"}
    con={"msgtype":"markdown","markdown":{"title":"ucloud共享带宽报警","text":content},"isAtAll": "ture"}
    jd=json.dumps(con)
    req=urllib2.Request(url,jd)
    req.add_header('Content-Type', 'application/json')
    response=urllib2.urlopen(req)

if __name__ == '__main__':
    ratios=sum()
    localtime = time.asctime( time.localtime(time.time()) )
    for bw in ratios:
        if ratios[bw] > 0.8:
            content = u"# **ucloud共享带宽报警** - %d兆那个。。。\n\n - 用量超过百分之80 \n - **值**:%f \n > [请排查...](https://console.ucloud.cn/unet/sharebandwidth)" % (bw,ratios[bw])
            send_to_dingtalk(content)
