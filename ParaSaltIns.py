# -*- set coding:utf-8 -*-
'''
Created on 2014��6��4��

@author: Administrator
'''

import datetime
import sys,os
import threading
import time
import DBsql
import logging
import logging.handlers

try:
    import paramiko
except ImportError:
    print 'no module named paramiko'

try:
    import PyLogin
except ImportError:
    print 'no module named PyLogin'

try:
    import MySQLdb
except ImportError:
    print 'no module named MySQLdb'


def GetPass(ipaddr):
    try:
        
        omdb = DBsql.DBsql()
        omdb.setoptions(Type='mysql',host=ConF['host'],pwd=ConF['passwd'],user=ConF['user'],db=ConF['db'],port=3306)
        omdb.start()

    except Exception,e:
        print e
        sys.exit()

    thost=omdb.one_query('''select ip,user,password,spassword from t_HostPasswd where IP='%s'; ''' % ipaddr) 
    
    if thost:
        return thost
    else:
        return 0


def sshCmd(ip):
    AllInfo = GetPass(ip) #获取主机用户信息及root权限
    if AllInfo:
        Comuser = AllInfo[1]
        Compass = PyLogin.MyCrypt('decode', AllInfo[2])
        Spasswd = PyLogin.MyCrypt('decode', AllInfo[3])
    else:
        return 'SERVER: %s CAN\'T FOUND' % ip
    
    
    try:
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        paramiko.util.log_to_file('syslogin.log')
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ip, 22, Comuser, Compass, timeout=5)
    except Exception,e:
        return '%s\t 运行失败,失败原因 \n%s' % (ip, e)
        
        
    #传输文件
    file = '/opt/zgt/SaltClient.sh'
    rfile = '/tmp/SaltClient.sh'
    try:
        
        sftp = client.open_sftp()
        sftp.put(file,rfile)        
        sftp.close()
    except Exception,e:
        return 'Error sftp: %s' % str(e)
            
    #调用命令
    reslog = os.getcwd()+'/response.log'
    fa = open(reslog,'a')
    channel = client.invoke_shell() #创建会话，开启命令调用
    channel.settimeout(10)
    
    buff=''
    resp=''
    channel.send('export LC_ALL=zh_CN.UTF-8\n')
    channel.send('su - root\n')
    while not buff.endswith('\'s password:') and not buff.endswith('口令：') and not buff.endswith('密码：'):
        try:
            resp = channel.recv(9999)
        except Exception,e:
            return 'Error channel: %s' % str(e)
            channel.close()
            client.close()
            sys.exit()
        buff += resp
    fa.write(buff)
        
    channel.send(Spasswd+'\n')
    time.sleep(1)
    
    buff=''
    while not buff.endswith(']# '):
        resp = channel.recv(9999)
        buff += resp
    fa.write(buff)
    
    
    cmdlist = ['cd /tmp','ls','sh SaltClient.sh']
    for cmd in cmdlist:
        buff=''
        channel.send(cmd+'\n')
        while buff.find(']# ')==-1: 
            try:
                resp=channel.recv(9999)
                buff+=resp
                     
            except Exception,e:
                return 'Error cmd: %s' % str(e)
        fa.write(buff)
        
    channel.close()
    client.close()

def Commlist(iplist):
    
    with open(iplist,'r') as fobj:
        for eachline in fobj:
            if eachline.find('#') != 0:
                #if putfile(eachline.strip('\n')):
                sshCmd(eachline.strip('\n'))
        
    print "程序结束运行%s" % datetime.datetime.now()

    
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
    Commlist('iplist.txt')