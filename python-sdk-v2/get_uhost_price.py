#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sdk import UcloudApiClient
from config import *
import sys
import json

#实例化 API 句柄


if __name__=='__main__':
    arg_length = len(sys.argv)
    ApiClient = UcloudApiClient(base_url, public_key, private_key, )
    #Parameters={"Region":"cn-bj2","ImageId":"uimage-3gzxij","CPU":"2","Memory":"2048","Action":"GetUHostInstancePrice","Count":"1","ChargeType":"Month"}
    Parameters = {'Count': 1, 'Region': 'cn-bj2', 'ImageId': 'uimage-3gzxij', 'Memory': 2048, 'Action': 'GetUHostInstancePrice', 'CPU': 2}
    response = ApiClient.get("/", Parameters );
    print response
    print json.dumps(response, sort_keys=True, indent=4, separators=(',', ': '))
    price = response["PriceSet"]
    print price


