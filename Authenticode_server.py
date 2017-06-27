# -*- set coding:utf-8 -*-
'''
Created on 2014��5��20��

@author: Administrator
'''

import httplib,urllib
import re
import random

class RandCode(object):
    
    
    
    def __init__(self):
        self.posturl = '115.239.133.245:8082/ecp-sb/authCode'
         = "http://192.168.104.203:7911/ecp-sb/authCode"
    
    def Code(self):
        code = random.randrange(10000,1000000)
        
    
    def SendSms(self,num):
        content = '456天天'
        
    if flag:
        data = {'type':'102', 'a':phone, 'c':'Q9DO', 'channel':'4'}
    else:
        data = {'type':'101', 'a':phone, 'c':code, 'channel':'4'}

    req = urllib2.Request(posturl)
    data = urllib.urlencode(data)
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
    response = opener.open(req,data)
    Res = response.read()
    
    Logger('phone'+Res)


if __name__ == '__main__':
    r = RandCode()
    r.SendSms('15305713256')