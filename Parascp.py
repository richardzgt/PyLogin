# -*- set coding:utf-8 -*-
'''
Created on 2014��6��4��

@author: Administrator
'''

import datetime
import sys,os
import threading
import time
import Mycrypt


try:
    import PyLogin
except ImportError:
    print 'no module named PyLogin'

try:
    import MySQLdb
except ImportError:
    print 'no module named MySQLdb'


def GetPass(ipaddr,filename):
    try:
        conn = MySQLdb.connect(ConF['host'],ConF['user'],ConF['passwd'],ConF['db'],port=3306,charset='utf8')
        cursor = conn.cursor()  
    except Exception,e:
        print e
        sys.exit()

    cursor.execute('select * from t_HostPasswd where IP=\'%s\' ' % (ipaddr)) 
    thost = cursor.fetchall()
     
    if len(thost) == 1 and thost[0][0] is not '':
        Comuser = thost[0][1]
        Compass = PyLogin.MyCrypt('decode',thost[0][2])
        Spasswd = PyLogin.MyCrypt('decode',thost[0][3])
        Pexpect(ipaddr,Comuser,Compass)
        
    else:
        pass


def Pexpect(ip,Comuser,Compass):
    try:
        import pexpect
    except ImportError:
        print 'no module named pexpect'


    Cmd = 'scp SaltClient.sh %s@%s:/tmp' % (Comuser,ip)
    try:
        scp = pexpect.spawn(Cmd)
        i = scp.expect(['assword:', 'continue connecting (yes/no)?','\$'], timeout=None)
        if i == 0:
            scp.sendline(str(Compass))
        elif i == 1:
            scp.sendline('yes')
            scp.expect('assword:')
            scp.delaybeforesend = 0.05
            scp.sendline(str(Compass))
            
        data = scp.read()
        print data,
        scp.close()
            
    except (KeyboardInterrupt,EOFError,UnboundLocalError):
        exit()         
    except pexpect.EOF:
        print "Connect Error"
    except pexpect.TIMEOUT:
        print 'TIMEOUT'



def Commlist():
    threads=[]
    #状态检查

    file = 'ip_list.txt'
    filename = 'SaltClient.sh'
    if not os.path.isfile(file):
        print 'not found %s' % file
        sys.exit()
    
    try:
        with open(file,'r') as fobj:
            for eachline in fobj:
                if eachline.find('#') != 0:
                    GetPass(eachline.strip('\n'),filename)

        print "程序结束运行%s" % datetime.datetime.now()
        
    except KeyboardInterrupt:
        sys.exit()    
    
    
def Init():
    #配置文件及时间的变量
    global ConF
    global fname
    global commlistdir
    
    #配置文件
    Config = '/opt/PyLogin/.config.ini'
    ConF = {}
    
    fn = open(Config,'r')
    for i in fn.readlines():
        if i.find('DATABASE') == 0 :
            ConF['db'] = PyLogin.MyCrypt('decode',i.strip('\n').split(':')[1])
        if i.find('USER') == 0 :
            ConF['user'] = PyLogin.MyCrypt('decode',i.strip('\n').split(':')[1])
        if i.find('PASSWD') == 0:
            ConF['passwd'] = PyLogin.MyCrypt('decode',i.strip('\n').split(':')[1])
        if i.find('HOST') == 0:
            ConF['host'] = PyLogin.MyCrypt('decode',i.strip('\n').split(':')[1])
    
    try:     
        if ConF['db'] == '' or ConF['user'] == '' or ConF['passwd'] == '' or ConF['host'] == '' :
            help(2)
            exit()
    except (NameError,KeyError),e:
        help(2)
        
    fn.close()


if __name__ == '__main__':
    Init()
    Commlist()