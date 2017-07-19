# -*- coding: utf-8 -*-
#!/usr/bin/env python

import urllib2
import json
import sys
import redis
import time


class weChat:

    def __init__(self,url,Corpid,Secret):
        url = '%s/cgi-bin/gettoken?corpid=%s&corpsecret=%s' % (url,Corpid,Secret)
        res = self.url_req(url)
        self.token = res['access_token']

    def url_req(self,url,method='get',data={}):
        if method == 'get':
            req = urllib2.Request(url)
            res = json.loads(urllib2.urlopen(req).read())
        elif method == 'post':
            req = urllib2.Request(url,data)
            res = json.loads(urllib2.urlopen(req).read())
        else:
            print 'error request method...exit'
            sys.exit()
        return res



# 发送weixin 消息
    def send_message(self,userlist,content,agentid=0):
        self.userlist = userlist
        self.content = content
        url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=%s' % self.token
        data = {
                      "touser": "",
                      "toparty": "1",
                      "totag": "",
                      "msgtype": "text",
                      "agentid": "",
                      "text": {
                          "content": ""
                      },
                      "safe":"0"
                   }
        data['touser'] = userlist
        data['agentid'] = agentid
        data['text']['content'] = content
        data = json.dumps(data,ensure_ascii=False)
    #   print data
        res = self.url_req(url,method='post',data=data)
        if res['errmsg'] == 'ok':
            print 'send sucessed!!!'
        else:
            print 'send failed!!'
# 发送邮件
    def send_mail(self,content):
        from op_tools.email import send_email
        try:

            emails = [
                "example@domain.com"
            ]
            title = "open-falcon 报警"
            message = content

            send_email(title, message, emails, html_message=message)

        except:
            print "send mail failed!"

#发送短信
    def send_sms(self,phone_num,content):
        from op_tools.sms import send_sms
        try:
            self.phone_num = phone_num
            cellphones = phone_num.split(',')
            message = content
            send_sms(cellphones, message)
            print "send_sms ok"
        except:
            print "send sms failed!"
# 发送钉钉
    def send_dingtalk(self,content):
        url = "https://oapi.dingtalk.com/robot/send?access_token="
        con={"msgtype":"text","text":{"content":content},"isAtAll": "true"}
        jd=json.dumps(con)
        req=urllib2.Request(url,jd)
        req.add_header('Content-Type', 'application/json')
        response=urllib2.urlopen(req)

if __name__ == '__main__':
    """
    用于open-falcon 发送报警
    """

    pool = redis.ConnectionPool(host='127.0.0.1', port=6379)
    r = redis.Redis(connection_pool=pool)

#    sms_key = r.keys("*sms")
#    l_sms = r.lrange(sms_key[0], 0, 10)

    while True:

        ls = r.lrange("/sms", 0, 0)
        l_sms = r.lpop("/sms")

	if 0 == len( ls ):
            time.sleep(2)
        else:
        #切割报警信息
	    info = json.loads(l_sms)
	    phone_num = info['tos']
	    con = info['content']
	    level = con.split("[")[1].split("]")[0]
	    status = con.split("[")[2].split("]")[0]
	    hosts = con.split("[")[3].split("]")[0]
	    contents = con.split("[")[5].split("]")[0].split(" ")[0]
            contents = unicode(contents)

	    value = con.split("[")[5].split("]")[0].split(" ")[4].split("\\")[0]
	    times = con.split("[")[6].split("]")[0]
	    content_all = u"状态:%s [%s],[%s],内容:%s, 值:%s" % (status, hosts, level, contents, value)
            c1 = content_all.encode('utf-8')


	    userlist = "fanquanqing"
	    content = c1
	    Corpid = ""
	    Secret = ""
	    url = "https://qyapi.weixin.qq.com"
            #默认所有报警都发送到微信
            try:
                wechat = weChat(url,Corpid,Secret)
	        wechat.send_message(userlist,content)
            except:
                print "send wechat failed"
	    #如果报警级别<3 发送邮件并且发送短信
            if int(level[1]) < 3:
                wechat.send_sms(phone_num,content)
                wechat.send_mail(content)
                if int(level[1]) < 2:
                    wechat.send_dingtalk(content)
                else:
                    pass
            #如果报警级别>=3只发送邮件
            else:
                wechat.send_mail(content)
            time.sleep(1)


    print "send all ok"
