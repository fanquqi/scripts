#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sdk import UcloudApiClient
from config import *
import sys
import json

#实例化 API 句柄

if __name__=='__main__':
    arg_length = len(sys.argv)
    ApiClient = UcloudApiClient(base_url, public_key, private_key)
    Parameters={
            "TimeRange":"2592000",
            "Action":"GetMetric",
            "Region":"cn-bj2",
            "MetricName.0":"BandOut",
            "ResourceType":"sharebandwidth",
            "ResourceId":"",
            "Period":"300"
            }
    response = ApiClient.get("/", Parameters );
    print json.dumps(response, sort_keys=True, indent=4, separators=(',', ': '))
