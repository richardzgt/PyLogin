# -*- set coding:utf-8 -*-
'''
Created on 2014��5��20��

@author: Administrator
'''
import PyLogin
import sys
import time
import os
import getpass
import base64
import re
import binascii
import shelve
import MyLogger
import pxssh
import threading
import MyLogger

try:
    import pexpect
except ImportError:
    print 'no module named pexpect'

try:
    import MySQLdb
except ImportError:
    print 'no module named MySQLdb'
    
try:
    import termios,fcntl,struct,signal
except ImportError:
    print 'no module named termios,fcntl,struct,signal'

def help(rtn):
    if rtn == 0:
        print '''
Usage: 
    modify servers' password
    ''' 
    
    elif rtn == 1:
        print '''
wrong IP
        '''
        
    elif rtn == 2:
        print '''
Config file Syntax error
        '''
    
    elif rtn == 3:
        print '''
Please in put yourname and password
        '''

    elif rtn == 4:
        print '''
Please check user privilege
        '''
        
    elif rtn == 5:
        print '''
t_UserAuth duplicate data
        '''  
        
    elif rtn == 6:
        print '''
No servers or t_HostPasswd duplicate data 
        '''
    elif rtn == 7:
        print '''
username or passwd invalid
        ''' 
    elif rtn == 8:
        print '''
modify password failed
        ''' 
    elif rtn == 9:
        print '''
Not the supper user
        '''         
    elif rtn == 10:
        print '''
t_LoginUser miss user data
        '''
    elif rtn == 11:
        print '''
Localdir is not a directory
'''
    elif rtn == 12:
        print '''
Localfile is not exist or Remotedir permission denied
'''

def GetPass(ipaddr):
    try:
        conn = MySQLdb.connect(ConF['host'],ConF['user'],ConF['passwd'],ConF['db'],port=3306,charset='utf8')
        cursor = conn.cursor()  
    except Exception,e:
        print e
        sys.exit()

    cursor.execute('select * from t_HostPasswd where IP=\'%s\' ' % (ipaddr)) 
    thost = cursor.fetchall()
     
    if len(thost) == 1:
        Comuser = thost[0][1]
        Compass = thost[0][2]
        Spasswd = thost[0][3]
        
        return Comuser,Compass,Spasswd

    else:
        help(6)
        exit() 

def updateDB(PassF):
    try:
        conn = MySQLdb.connect(ConF['host'],ConF['user'],ConF['passwd'],ConF['db'],port=3306,charset='utf8')
        cursor = conn.cursor()
    except Exception,e:
        print e
        sys.exit()
    

    try:
        ipaddress = PassF[0]
        Comuser = PassF[1]
        Compass = PassF[2]
        Spasswd = PassF[3]
        SQL1 = 'select ip from  t_HostPasswd where ip=\'%s\'' % ipaddress
        cursor.execute(SQL1)
        if len(cursor.fetchall()) == 1:
            SQL2 = 'update t_HostPasswd set user=\'%s\',password=\'%s\',spassword=\'%s\' where ip=\'%s\'' % \
        (Comuser,PyLogin.MyCrypt('encode',Compass),PyLogin.MyCrypt('encode',Spasswd),ipaddress) 
            cursor.execute(SQL2)
            print '----DB update execute ok -----'
    except EOFError:
        exit()            

def Fork_2(*PassF):
    #登陆变慢，而且也不能知道
    AllInfo = GetPass(PassF[0]) #获取主机用户信息及root权限
    Comuser = AllInfo[0]
    Compass = PyLogin.MyCrypt('decode', AllInfo[1])
    Spasswd = PyLogin.MyCrypt('decode', AllInfo[2])
    
    
    Logger = MyLogger.MyLogger('ModPass.log','ModPass')
    
    try:
        if Comuser != 'root':
            ssh = pxssh.pxssh()
            ssh.login(PassF[0],Comuser,Compass,original_prompt='[\$#>?]')
            ssh.sendline('export LC_ALL=zh_CN.UTF-8')  #设置字符集
            ssh.prompt(timeout=5)
            ssh.sendline('su - root')
            ssh.prompt(timeout=5)
            ssh.sendline(Spasswd)
            ssh.prompt(timeout=3)
            ssh.sendline('echo "%s"|passwd %s --stdin' % (PassF[2],PassF[1]))
            ssh.sendline('echo "%s"|passwd root --stdin' % (PassF[3]))
            ssh.prompt(timeout=3)
            content = ssh.before
            Logger.Logger(content)
            updateDB(PassF)
            print '--- %s update password success ---' % PassF[0]
    except Exception,e:
        Logger.Logger(e)
        print '--- %s update password failure ---' % PassF[0]
        


def Fork(*PassF):
    AllInfo = GetPass(PassF[0]) #获取主机用户信息及root权限
    Comuser = AllInfo[0]
    Compass = PyLogin.MyCrypt('decode', AllInfo[1])
    Spasswd = PyLogin.MyCrypt('decode', AllInfo[2])
    Logger = MyLogger.MyLogger('ModPass.log','ModPass')
    if Comuser != 'root': 
        ssh = pexpect.spawn('ssh %s@%s' % (Comuser,PassF[0]))
        try:
            i = ssh.expect(['assword:', 'continue connecting (yes/no)?','\$'], timeout=5)
            if i == 0:
                ssh.delaybeforesend = 0.05
                ssh.sendline(str(Compass))
                ssh.sendline('export LC_ALL=zh_CN.UTF-8')  #设置字符集
                i2 = ssh.expect(['\$',pexpect.EOF],timeout=15)
                if i2 == 0:
                        ssh.sendline('su - root')
                        ssh.expect(['word:','：'],timeout=15)
                        ssh.delaybeforesend = 0.05
                        ssh.sendline(str(Spasswd))
    
            elif i == 1:
                ssh.sendline('yes')
                ssh.expect('assword:')
                ssh.delaybeforesend = 0.05
                ssh.sendline(str(Compass))
                ssh.sendline('export LC_ALL=zh_CN.UTF-8')
                i2 = ssh.expect(['\$',pexpect.EOF],timeout=15)
                if i2 == 0:
                        ssh.sendline('su - root')
                        ssh.expect(['word:','：'],timeout=15)
                        ssh.delaybeforesend = 0.05
                        ssh.sendline(str(Spasswd))
            
            elif i == 2:
                ssh.sendline('export LC_ALL=zh_CN.UTF-8')
                ssh.sendline('su - root')
                ssh.expect(['word:','：'],timeout=15)
                ssh.delaybeforesend = 0.05
                ssh.sendline(str(Spasswd))
                
                
            try:
                ssh.sendline('echo "%s"|passwd %s --stdin' % (PassF[2],PassF[1]))
                ssh.sendline('echo "%s"|passwd root --stdin' % (PassF[3]))
                ssh.delaybeforesend = 0.5
                content = ssh.before
                Logger.Logger(content)
                updateDB(PassF)
                print '--- %s update password exec ok ---' % PassF[0]
            except:
                sys.exit()
            
        except (KeyboardInterrupt,EOFError):
            print '--- %s update password failure ---' % PassF[0]
            exit()          
        except pexpect.EOF:
            print "Connect Error"
            print '--- %s update password failure ---' % PassF[0]
            ssh.close()
        except pexpect.TIMEOUT:
            print 'TIMEOUT'
            print '--- %s update password failure ---' % PassF[0]
            ssh.close()
            

                
    else:
        print 'comuser == root'
        ssh = pexpect.spawn('ssh %s@%s' % (Comuser,PassF[0]))
        try:
            i = ssh.expect(['assword:', 'continue connecting (yes/no)?','\$'], timeout=5)
            if i == 0:
                ssh.delaybeforesend = 0.05
                ssh.sendline(str(Compass))
                ssh.sendline('export LC_ALL=zh_CN.UTF-8')  #设置字符集
    
            elif i == 1:
                ssh.sendline('yes')
                ssh.expect('assword:')
                ssh.delaybeforesend = 0.05
                ssh.sendline(str(Compass))
                ssh.sendline('export LC_ALL=zh_CN.UTF-8')
            elif i == 2:
                ssh.sendline('export LC_ALL=zh_CN.UTF-8')
                
                
            try:
                ssh.sendline('useradd "%s";echo "%s"|passwd "%s" --stdin ' % (PassF[1],PassF[2],PassF[1]))
                ssh.sendline('echo "%s"|passwd root --stdin' % (PassF[3]))
                updateDB(PassF)
                print '--- %s update password exec ok ---' % PassF[0]
            except:
                print '--- %s update password failure ---' % PassF[0]
                sys.exit()
                
        except (KeyboardInterrupt,EOFError):
            print '--- %s update password failure ---' % PassF[0]
            exit()          
        except pexpect.EOF:
            print "Connect Error"
            print '--- %s update password failure ---' % PassF[0]
            ssh.close()
        except pexpect.TIMEOUT:
            print 'TIMEOUT'
            print '--- %s update password failure ---' % PassF[0]
            ssh.close()
    


def Init():
    #配置文件及时间的变量
    global ConF
    global fname
    
    #配置文件
    Config = '/opt/PyLogin/.config.ini'
    ConF = {}
    threads = []
    
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

    
    PassFile = raw_input('PassFile:')
    with open(PassFile) as fobj:
        for eachline in fobj:
            work_thread = threading.Thread(target=Fork,args=eachline.split())
            work_thread.start()
            threads.append(work_thread)
            time.sleep(1)

if __name__ == '__main__':
    Init()