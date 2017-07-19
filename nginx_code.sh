#!/bin/bash

codes="302 400 401 403 404 500 502 503"

for code in $codes;do

  ts=`date +%s`;
  t=`LC_ALL=en_US.UTF-8 date '+%d/%b/%Y:%H:%M' -d "-1 minute"`
  valus=`tail -1000000 /usr/local/nginx/logs/access.log | grep -v 'tvdoctor' | grep $t | awk '{print $9}' | grep $code | wc -l`
  curl -X POST -d "[{\"metric\": \"nginx_code\", \"endpoint\": \"nginx-online1\", \"timestamp\": $ts,\"step\": 60,\"value\": $valus,\"counterType\": \"GAUGE\",\"tags\": \"code=$code\"}]" http://127.0.0.1:1988/v1/push


done
