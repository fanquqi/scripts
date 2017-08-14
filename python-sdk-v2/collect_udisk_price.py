#!/usr/bin/env python
# -*- coding:utf-8 -*-

# author: fanquanqing
# 收集ucloud云硬盘信息 及价格

from sdk import UcloudApiClient
from config import *
import sys
import json

# 获取udisk 信息
def get_udisk_info(Regions_list,ProjectId):
	udisk_list = []
	for Region in Regions_list:
		ApiClient = UcloudApiClient(base_url, public_key, private_key)
		Parameters={"Action":"DescribeUDisk", "Region":Region, "ProjectId":ProjectId}
		response = ApiClient.get("/", Parameters );
		for udisk in response['DataSet']:
			udisk_dic = {}
			udisk_dic['Region'] = Region
			#udisk_dic['Action'] = "DescribeUDiskPrice"
			udisk_dic['Size'] = udisk['Size']
			udisk_dic['ChargeType'] = udisk['ChargeType'].encode('utf-8')
			udisk_dic['UHostName'] = udisk['UHostName']
			udisk_dic['Quantity'] = 1
			udisk_dic['Zone'] = "cn-bj2-02"
			udisk_list.append(udisk_dic)
	return udisk_list

# 通过udisk信息获取价格
def get_udisk_price(udisk_list):
	for udisk in udisk_list:
		ApiClient = UcloudApiClient(base_url, public_key, private_key)
		udisk_params={}
		udisk_params['Action']="DescribeUDiskPrice"
		udisk_params['Region']=udisk['Region']
		udisk_params['Size']=udisk['Size']
		udisk_params['ChargeType']=udisk['ChargeType']
		udisk_params['Quantity']=udisk['Quantity']
		udisk_params['Zone']=udisk['Zone']
		Parameters = udisk_params
		response = ApiClient.get("/", Parameters );
		if udisk_params['ChargeType']=="Year":
			price = response['DataSet'][0]['Price']/100
		elif udisk_params['ChargeType']=="Month":
			price = response['DataSet'][0]['Price']/10
		else:
			print "有付费方式异常的云硬盘，请排查。"
		udisk["Price"]=price
	return udisk_list

# 通过付费周期获取udisk价格
def collect_udisk_price(setting_info):
	udisk_price_info = []
	for Projectname in setting_info:
		for ProjectId in setting_info[Projectname]:
			Regions_list = setting_info[Projectname][ProjectId]
			udisk_list = get_udisk_info(Regions_list,ProjectId)
			udisk_price_info.extend(get_udisk_price(udisk_list))
	return udisk_price_info



if __name__ == '__main__':
	collect_udisk_price({"chunyu":{"org-oddm1w":['cn-bj2','hk']}, "uhs":{"org-shbbct":["cn-bj2"]}})

