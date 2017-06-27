# -*- set coding:utf-8 -*-
'''
Created on 2014��5��22��

@author: Administrator
'''

import urllib  
import urllib2  
import logging
import logging.handlers
import os,sys

def Logger(msg):
    LOG_FILE = '/var/log/.PyLogin/AuthCode.log'
    if not os.access('/var/log/.PyLogin',os.W_OK):
        print '''/var/log/.PyLogin can't be access '''
        sys.exit()
        
    handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes = 1024*1024) # 实例化handler 
    fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s'
    
    formatter = logging.Formatter(fmt)   # 实例化formatter
    handler.setFormatter(formatter)      # 为handler添加formatter
    
    logger = logging.getLogger('AuthCode')
    logger.addHandler(handler)           # 为logger添加handler
    logger.setLevel(logging.DEBUG)
    logger.info(msg)
    logger.removeHandler(handler)   #如果不加，就有重复的记录到日志里,但是单次执行却没有问题，我认为是重复加载handle造成
   

def AuthCode(phone,flag=1,code=0):
    posturl = "http://192.168.104.203:7911/ecp-sb/authCode"

    if flag:
        data = {'type':'102', 'a':phone, 'c':'Q9DO', 'channel':'4'}
    else:
        data = {'type':'101', 'a':phone, 'c':code, 'channel':'4'}

    req = urllib2.Request(posturl)
    data = urllib.urlencode(data)
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
    response = opener.open(req,data)
    Res = response.read()
    
    Logger('phone：'+ str(phone) + ' ' +Res)   #注意Logger里面只能传str类型
    
    if Res.find('I0002') > -1 or Res.find('I0003') > -1:
        return True
    else:
        return False

if __name__ == '__main__':
    print AuthCode('15305713256')
#    AuthCode('15305713256',0,'1632')