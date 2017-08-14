#!/usr/bin/python
#-*- coding:utf-8 -*-

# author:fanquanqing
# collect ucloud uhost price
from sdk import UcloudApiClient
from config import *
from collections import Iterable
import sys
import json


#host_list = []

# 收集uhost信息
def collect_uhost_info(Regions_list,ProjectId):
    '''
    包含 hostname, ip, region, cpu, mem, diskspace, chargetype, count, ImageId, osname.
    '''
    host_info_list = []
    for Region in Regions_list:
        ApiClient = UcloudApiClient(base_url, public_key, private_key)
        Parameters={
        "Action":"DescribeUHostInstance",
        "Region":Region,
        "ProjectId":ProjectId,
        "Limit":"1000"
        }
        response = ApiClient.get("/", Parameters);
        length = response['TotalCount']
        for i in range(length):
            host_info = {}
            #ImageId = response["UHostSet"][i]["BasicImageId"].encode("utf-8")
            ChargeType = response["UHostSet"][i]["ChargeType"].encode("utf-8")
            #host_info["Action"] = "GetUHostInstancePrice"
            host_info["Region"] = Region
            host_info["ImageId"] = "uimage-kg0w4u"
            host_info["Hostname"] = response["UHostSet"][i]["Name"]
            host_info["CPU"] = response["UHostSet"][i]["CPU"]
            host_info["Memory"] = response["UHostSet"][i]["Memory"]

            if len(response["UHostSet"][i]["DiskSet"]) > 1:
                host_info["DiskSpace"] = response["UHostSet"][i]["DiskSet"][1]["Size"]
            else:
                host_info["DiskSpace"]=0
            host_info["Count"] = 1
            host_info["ChargeType"] = ChargeType
            host_info["OsName"] = response["UHostSet"][i]["OsName"].split()[0]
            host_info["loaclIP"] = response["UHostSet"][i]["IPSet"][0]["IP"]
            if len(response["UHostSet"][i]["IPSet"])>1:
                host_info["EIP"]=response["UHostSet"][i]["IPSet"][1]["IP"]
            else:
                host_info["EIP"]="none"

            host_info_list.append(host_info)
    #print host_info_list
    return host_info_list


#通过机器配置得到某一台机器价格
def get_uhost_price(host_instance_info):
    ApiClient = UcloudApiClient(base_url, public_key, private_key)
    Parameters= host_instance_info
    response = ApiClient.get("/", Parameters );
#    print json.dumps(response, sort_keys=True, indent=4, separators=(',', ': '))
    price = float(response["PriceSet"][0].values()[0])
    return price

#通过机器配置信息得到所有机器价格
def get_all_uhost_price(host_info_list):

    for host_info in host_info_list:
        host_params={}
        host_params["Action"]="GetUHostInstancePrice"
        host_params["ImageId"]=host_info["ImageId"]
        host_params["CPU"]=host_info["CPU"]
        host_params["Memory"]=host_info["Memory"]
        host_params["Count"]=host_info["Count"]
        host_params["DiskSpace"]=host_info["DiskSpace"]
        host_params["Region"]="cn-bj2"
        host_params["ChargeType"]=host_info["ChargeType"]
        if host_params["ChargeType"]=="Year":
            price = get_uhost_price(host_params)
        elif host_params["ChargeType"]=="Month":
            price = get_uhost_price(host_params)*12
        else:
            price=0
            print "有临时机器请排查。"
        host_info["Price"]=price

    return host_info_list

def collect_uhost_price(setting_info):

    host_info_total = []
    for Projectname in setting_info:
        for ProjectId in setting_info[Projectname]:
            Regions_list = setting_info[Projectname][ProjectId]
            host_info_list = collect_uhost_info(Regions_list,ProjectId)
            project_host_list = get_all_uhost_price(host_info_list)
            host_info_total.extend(project_host_list)
    return host_info_total



if __name__ == '__main__':
    host_info_list = collect_uhost_info(['cn-bj2','hk'],"org-oddm1w")
    host_price_list = get_all_uhost_price(host_info_list)
    #print host_price_list

