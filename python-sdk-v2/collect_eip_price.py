#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:fanquanqing
# collect ucloud eip price
from sdk import UcloudApiClient
from config import *
import sys
import json

# 得到所有的EIP实例信息
def get_eip_instance(Regions_list,ProjectId):
	eip_all = []
	for Region in Regions_list:
		ApiClient = UcloudApiClient(base_url, public_key, private_key)
		Parameters={"Action":"DescribeEIP", "Region":Region, "ProjectId":ProjectId}
		response = ApiClient.get("/", Parameters );
		for eip in response['EIPSet']:
			eip_instance = {}
    		# 地域
			eip_instance['Region']=Region
    		# IP
			eip_instance['IP']=eip['EIPAddr'][0]['IP']

    		# 运营商线路
			eip_instance['OperatorName']=eip['EIPAddr'][0]['OperatorName'].encode('utf-8')
    		# 带宽
			eip_instance['Bandwidth']=eip['Bandwidth']
    		# 付费周期
			eip_instance['ChargeType']=eip['ChargeType'].encode('utf-8')
    		# 付费方式(是否绑定共享带宽)
			eip_instance['PayMode']=eip['PayMode'].encode('utf-8')
			eip_all.append(eip_instance)

	return eip_all
    #print json.dumps(response, sort_keys=True, indent=4, separators=(',', ': '))




# 查看单个EIP实例价格
def get_eip_price(eip):
	ApiClient = UcloudApiClient(base_url, public_key, private_key)
	Parameters=eip
	response = ApiClient.get("/", Parameters );
	#print response
	price = response['PriceSet'][0]['Price']
	return price


# 获取所有EIP价格
def get_all_eip_price(eip_all):

	for eip_info in eip_all:
		eip_params={}
		eip_params['Action']="GetEIPPrice"
		eip_params['Region']=eip_info['Region']
		eip_params['OperatorName']=eip_info['OperatorName']
		eip_params['Bandwidth']=eip_info['Bandwidth']
		eip_params['ChargeType']=eip_info['ChargeType']
		eip_params['PayMode']=eip_info['PayMode']
		if eip_params['ChargeType']=="Year":
			price = get_eip_price(eip_params)
		elif eip_params['ChargeType']=="Month":
			price = get_eip_price(eip_params)*12
		else:
			price=0
			print "有临时EIP请排查"
		eip_info["Price"]=price
	return eip_all


def collect_eip_price(setting_info):
	eip_info_total = []
	for Projectname in setting_info:
		for ProjectId in setting_info[Projectname]:
			Regions_list = setting_info[Projectname][ProjectId]
			eip_all=get_eip_instance(Regions_list,ProjectId)
			price_all=get_all_eip_price(eip_all)
			eip_info_total.extend(price_all)
	#print eip_info_total
	return eip_info_total

if __name__ == '__main__':
	collect_eip_price({"chunyu":{"org-oddm1w":['cn-bj2','hk']}, "uhs":{"org-shbbct":["cn-bj2"]}})


