#!/usr/bin/env python
# -*- coding:utf-8 -*-

# author: fanquanqing
#import datatime
from collect_eip_price import collect_eip_price
from collect_uhost_price import collect_uhost_price
from collect_sharebandwidth_price import collect_sharebandwidth_price
from collect_udisk_price import collect_udisk_price
from op_tools.api_influxdb import write_data_to_influxdb

def get_price(setting_info):
	'''
	各个实例price求和,并把实例信息发送到influxdb
	'''
	eip_price=0
	uhost_price=0
	sharebw_price=0
	udisk_price=0
	eip_price_info_list = collect_eip_price(setting_info)
	for eip_info in eip_price_info_list:
		eip_headers = eip_info.keys()
		eip_rows = []
		eip_rows.append(eip_info.values())
		#print eip_headers, eip_rows
		# 发送EIP数据到influxdb
		write_data_to_influxdb('EIP_info_daliy', eip_headers, eip_rows, ['IP', 'OperatorName', 'ChargeType'])
		eip_price += round(eip_info['Price'])

	uhost_price_info_list = collect_uhost_price(setting_info)
	for uhost_info in uhost_price_info_list:
		uhost_headers=uhost_info.keys()
		uhost_rows=[]
		uhost_rows.append(uhost_info.values())
		#print uhost_headers, uhost_rows
		# 发送云主机信息到influxdb
		write_data_to_influxdb('Uhost_info_daliy', uhost_headers, uhost_rows, ['Hostname','ChargeType'])
		uhost_price += round(uhost_info['Price'])

	sharebandwidth_info_list = collect_sharebandwidth_price(setting_info)
	for sharebandwidth_info in sharebandwidth_info_list:
		sharebw_headers=sharebandwidth_info.keys()
		sharebw_rows=[]
		sharebw_rows.append(sharebandwidth_info.values())
		#print sharebw_headers, sharebw_rows
		# 发送共享带宽信息到influxdb
		write_data_to_influxdb('ShareBandwidth_info_daliy',sharebw_headers,sharebw_rows,[])
		sharebw_price += round(sharebandwidth_info['Price'])

	udisk_info_list=collect_udisk_price(setting_info)
	for udisk_info in udisk_info_list:
		udisk_headers=udisk_info.keys()
		udisk_rows=[]
		udisk_rows.append(udisk_info.values())
		#print udisk_headers, udisk_rows
		write_data_to_influxdb('Udisk_info_daliy', udisk_headers,udisk_rows,['UHostName','Region'])
		udisk_price += round(udisk_info['Price'])
	# 托管机房价格
	physical_price = get_physical_host_price()
	total_price=eip_price+uhost_price+sharebw_price+udisk_price+physical_price
	# 价格列表
	price_list=[eip_price,uhost_price,sharebw_price,udisk_price,total_price]
	price_headers=['eip_price','uhost_price','sharebw_price','udisk_price','total_price']
	price_rows=[]
	price_rows.append(price_list)
	write_data_to_influxdb('Ucloud_price_total_daliy',price_headers,price_rows,[])

	#print uhost_price
	return uhost_price

# 托管机器价格(两个机柜一个10M外网)
def get_physical_host_price():
	host_price = 9000*2*12
	tg_cloud_switch_port_price = (288*2+217)*12
	tg_bandwidth_price = 10*90*12
	physical_price = host_price+tg_bandwidth_price+tg_cloud_switch_port_price
	return physical_price

if __name__ == '__main__':
	# 可用区列表
	#Regions_list = ['cn-bj2','hk']
	# 项目ID列表
	#Project_Id_list = ['org-shbbct','org-oddm1w']
	# 项目ID对应关系
	setting_info = {"chunyu":{"org-oddm1w":['cn-bj2','hk']}, "uhs":{"org-shbbct":["cn-bj2"]}}
	get_price(setting_info)


#print 493370.4+64432.8
