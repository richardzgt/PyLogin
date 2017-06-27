# -*- set coding:utf-8 -*-
'''
Created on 2015��4��16��

@author: Administrator
'''
#reload(sys)
#sys.setdefaultencoding('utf-8')
from  optparse import OptionParser


def foo_callback(option, opt, value, parser):
  setattr(parser.values, option.dest, value.split(','))

def opt():
    global parser
    parser = OptionParser()
    parser.add_option('-f', '--foo',
                      type='string',
                      action='callback',
                      callback=foo_callback)
    # parser.add_option("-f", "--file",dest="filename",help="write report to FILE", metavar="FILE")
    parser.add_option("-q", "--quiet",
                      action="store_false", 
                      dest="verbose", 
                      default=True,
                      help="don't print status messages to stdout")



    (options, args) = parser.parse_args()
    print options,args




