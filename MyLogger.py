# -*- set coding:utf-8 -*-
'''
Created on 2014��4��16��

@author: zgt
'''

import logging
import logging.handlers
class MyLogger(object):
    def __init__(self,LOG_FILE,LOG_NAME):
        self.LOG_FILE = LOG_FILE
        self.LOG_NAME = LOG_NAME
        
    def Logger(self,msg):
        self.msg = msg
        handler = logging.handlers.RotatingFileHandler(self.LOG_FILE, maxBytes = 1024*1024) # 实例化handler 
        fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s'
        
        formatter = logging.Formatter(fmt)   # 实例化formatter
        handler.setFormatter(formatter)      # 为handler添加formatter
        
        logger = logging.getLogger(self.LOG_NAME)    # 获取名为tst的logger
        logger.addHandler(handler)           # 为logger添加handler
        logger.setLevel(logging.DEBUG)
        logger.info(msg)
        logger.removeHandler(handler)   #如果不加，就有重复的记录到日志里,但是单次执行却没有问题，我认为是重复加载handle造成
        
if __name__ == '__main__':
    Logger = MyLogger('MyLoger.log','MyLoger')
    for i in range(200):
        Logger.Logger('1234+%s' % i)
    
    