#!/usr/bin/env python
# -*- set coding:utf-8 -*-
'''
Created on 2014��3��27��

@author: Administrator
'''

import sys
import PyLogin 
import os
import getpass

    
def mainhelp():
    print '''
Usage: 
    %s <Server IP>        logining to server as common user
    
    %s -s <Server IP>     logining to server as super user(root)
    
    %s -c <Server IP>     scp file to remote server
            remotedir         destination server's direction
            localfile         local server's file
        
    %s -b <Server IP>     scp file from remote server
            remotefile        remote server's files
            localdir          local server's destination
        
    %s -l                 Menu list
    
    %s -h                 help
    ''' % (sys.argv[0],sys.argv[0],sys.argv[0],sys.argv[0],sys.argv[0],sys.argv[0])
    exit()
    
try:
    
        if len(sys.argv)<2 or sys.argv[1].lower() == '-h':
            mainhelp()
    
        User = raw_input('Your name: ')
        Passwd = getpass.getpass()
        
        if PyLogin.check_ip(sys.argv[1]):
            value={'Execfile':sys.argv[0],'User':User,'Passwd':Passwd,'TargetIP':sys.argv[1],'ForkCmd':0}
        
        elif sys.argv[1].lower() in ('-s','-p','-c','-b') and PyLogin.check_ip(sys.argv[2]):
            value={'Execfile':sys.argv[0],'User':User,'Passwd':Passwd,'TargetIP':sys.argv[2],'ForkCmd':sys.argv[1].lower()}
        
        elif sys.argv[1].lower() == '-l':
            value={'Execfile':sys.argv[0],'User':User,'Passwd':Passwd,'TargetIP':0,'ForkCmd':sys.argv[1].lower()}
        
        else:
            print '''
wrong IP or command wrong
        '''
            exit()
        
        PyLogin.Init(value)

except (KeyboardInterrupt,EOFError,IndexError):
        exit()