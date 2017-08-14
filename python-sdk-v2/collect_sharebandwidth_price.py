#!/usr/bin/python
# -*- coding: utf-8 -*-
#author fanquanqing
#收集共享带宽信息获取每年消费情况
from sdk import UcloudApiClient
from config import *
import sys
import json

def get_bandwidth_info(Regions_list,ProjectId):
	bandwidth = []
	for Region in Regions_list:

		ApiClient = UcloudApiClient(base_url, public_key, private_key)
		Parameters={"Action":"DescribeShareBandwidth","Region":Region,"ProjectId":ProjectId}
		response = ApiClient.get("/", Parameters );
		#print response
		for bw in response['DataSet']:
			bw_instance = {}
			bw_instance['ShareBandwidth'] =  bw['ShareBandwidth']
			bw_instance['ChargeType'] = bw['ChargeType']
			bw_instance['Name']=bw['Name']
			bandwidth.append(bw_instance)
	return bandwidth
#	print json.dumps(response, sort_keys=True, indent=4, separators=(',', ': '))

def get_price(bandwidth):
	'''
	价格计算说明:ucloud没有提供API查询共享带宽价格，所有的共享带宽价格都是90/M/月 月付*12,年付*10
	'''
	price_list = []
	for bw in bandwidth:
		if bw['ChargeType']=="Month":
			price = bw['ShareBandwidth']*90*12
			bw["Price"]=price
		else:
			price = bw['ShareBandwidrh']
			bw["Price"]=price
	return bandwidth

def collect_sharebandwidth_price(setting_info):
    bw_price_info = []
    for Projectname in setting_info:
        for ProjectId in setting_info[Projectname]:
            Regions_list = setting_info[Projectname][ProjectId]
            bw_info = get_bandwidth_info(Regions_list,ProjectId)
            bw_price_info.extend(get_price(bw_info))
    #print bw_price_info
    return bw_price_info


if __name__ == '__main__':
	collect_sharebandwidth_price({"chunyu":{"org-oddm1w":['cn-bj2','hk']}, "uhs":{"org-shbbct":["cn-bj2"]}})
