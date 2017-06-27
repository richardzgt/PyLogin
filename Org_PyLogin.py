#!/usr/bin/env python
# -*- set coding:utf-8 -*-
'''
Created on 2014��3��23��

@author: richardzgt
'''


#===============================================================================
# 实现用户的一键登陆，加密服务器密码，记录会话
#2.通过配置字符集解决GBK 导致的expect无法匹配问题
#
#===============================================================================


import sys
import time
import os
import getpass
import base64
import re
import binascii
import shelve

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

try:
    import getHostname
except ImportError:
    print 'no module named getHostname'

def help(rtn):
    if rtn == 0:
        print '''
Usage: 
    %s <Server IP> 
    OR
    %s <Server IP> Command 
    ''' % (Value['Execfile'],Value['Execfile'])
    
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

# --exeTime
def exeTime(func):
    def newFunc(*args, **args2):
        t0 = time.time()
        print "@%s, {%s} start" % (time.strftime("%X", time.localtime()), func.__name__)
        back = func(*args, **args2)
        print "@%s, {%s} end" % (time.strftime("%X", time.localtime()), func.__name__)
        print "@%.3fs taken for {%s}" % (time.time() - t0, func.__name__)
        return back
    return newFunc
# --end of exeTime

def check_ip(ipaddr):
    '''
    addr = ipaddr.strip().split('.')
    if len(addr) != 4:
        return 0
    for i in range(4):
        try:
            addr[i] = int(addr[i])
        except:
            return 0
        if addr[i] <= 255 and addr[i] >=0:         
            pass
        else:
            return 0
        i+=1
        
    return 1
    '''
    # 校验ip地址及主机名，正确就返回ip地址，主机名不能是一个正常的ip地址
    # 主机名查询om数据库，匹配主机名，主机名不能重复
    q = ipaddr.split('.')
    if  len(filter(lambda x: x >= 0 and x <= 255, map(int, filter(lambda x: x.isdigit(), q)))) == 4:
        return ipaddr
    elif getHostname.Init(ipaddr):
        return getHostname.Init(ipaddr)
    else:
        return False
    
    
def Menu():
    Menu0 = {'1':'查询登陆权限','2':'用户修改密码','3':'其他','4':'退出'}
    global username
    
    while True:
        keys = sorted(Menu0.keys())
        for key in keys:
            print key,Menu0[key]
            
        choice0 = raw_input('>').strip()
        
        if choice0 == '1':
            username = raw_input('Username: ')
            QryAuth = UpdateDB('QryAuth',username)
            print 'IP                      root?(1/0)'
            for i in QryAuth:
                print '%s                %s' % (i[0],i[1])
            print '''
-------------------------------------------
'''
            continue    
        
        if choice0 == '2':
            New1 = getpass.getpass('输入新密码[数字和小写字母至少6位]:')
            New2 = getpass.getpass('再次输入新密码:')
            if New1 == New2 and re.search('[0-9]',New1) and re.search('[a-z]',New1) and len(New1)>5:
                UpdateDB(cmd='ModPass',DBValue=New1)
                print '修改密码成功'
            else:
                help(8)
            continue              
        
        if choice0 == '3':
            pass
                        
        if choice0 == '4':
            exit()

def MyCrypt(cmd,Orpass):
    if cmd == 'encode' and Orpass:
        try:
            s1 = base64.encodestring(Orpass)
            s2 = s1 + 'zgt'
            s3 = base64.encodestring(s2)
            return s3.strip('\n')
        except binascii.Error:
            print 'MyCrypt can\'t encode'
            exit()
        
    if cmd == 'decode' and Orpass:
        try:
            s1 = base64.decodestring(Orpass)
            s2 = base64.decodestring(s1[0:-3:])
            return s2.strip('\n')
        except binascii.Error:
            print 'MyCrypt can\'t decode'
            exit()

def UpdateDB(cmd,DBValue=0):
    global LastID
    
    try:
        conn = MySQLdb.connect(ConF['host'],ConF['user'],ConF['passwd'],ConF['db'],port=3306,charset='utf8')
        cursor = conn.cursor()  
    except Exception,e:
        print 'Mysql-server:',e
        sys.exit()
    
    if cmd == 'tty':
        tty = os.popen('tty|cut -d/ -f 3-')
        TTY = tty.readline().strip('\n')
        cursor.execute('insert into t_LoginLog (Username,Target_IP,Time,TTY)values(\'%s\',\'%s\',\'%s\',\'%s\')' % (Value['User'],Value['TargetIP'],now,TTY))
        cursor.execute('SELECT LAST_INSERT_ID()')  #获取auto_incr 的lastID
        LastID = cursor.fetchall()[0][0]

                
    if cmd == 'Utty':
        Now = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
        cursor.execute('update t_LoginLog set Levtime=\'%s\' where QueLogin=\'%s\'' % (Now,LastID))
    

    if cmd == 'QryAuth':
        SQL='''select b.IP,a.IPiroot from  t_UserAuth a,t_HostPasswd b,t_LoginUser c where 
        c.UserID=a.UserID and b.ID=a.HPID and c.LoginName='%s' ''' % MyCrypt('encode',DBValue)
        cursor.execute(SQL)
        try:
            QryAuth = cursor.fetchall()
            return QryAuth
        except IndexError,e:
            help(10)
        
    if cmd == 'ModPass':
        SQL='update t_LoginUser set Passwd=\'%s\' where LoginName=\'%s\'' % (MyCrypt('encode',DBValue),MyCrypt('encode',Value['User']))
        cursor.execute(SQL)
    conn.commit()

def GetUserAndPri():
    global IPriroot
    
    if Value['User'] and Value['Passwd']:
        try:
            conn = MySQLdb.connect(ConF['host'],ConF['user'],ConF['passwd'],ConF['db'],port=3306,charset='utf8')
        except Exception,e:
            #20140902添加为了防止数据库链接不上报错
            if str(e).find("2003")>-1:
                print "can not connect GODB"
            else:
                print 'GO-Mysql-server:',e
            
            sys.exit()
        
        cursor = conn.cursor()
        SQL1= '''select userid,LoginName,Passwd from t_LoginUser where LoginName='%s' and Passwd='%s' ''' % (MyCrypt('encode',Value['User']),MyCrypt('encode',Value['Passwd']))
        cursor.execute(SQL1)

        uinfo = cursor.fetchall()

        if len(uinfo) == 1 and len(uinfo[0]) == 3:
            UserID = uinfo[0][0]
            if Value['TargetIP']:
                cursor.execute('select ip,user,password,spassword,ID from t_HostPasswd where IP=\'%s\' ' % (Value['TargetIP']))

                thost = cursor.fetchall()
            
                if len(thost) == 1:
                    Comuser = thost[0][1]
                    Compass = thost[0][2]
                    Spasswd = thost[0][3]
                    hostID = thost[0][4]
       
                    cursor.execute('select IPiroot from t_UserAuth where UserID=\'%s\' and HPID=\'%s\'' % (UserID,hostID))
                    auth = cursor.fetchall()
                    
                    if len(auth) == 1:
                        IPriroot = auth[0][0]                   
                    
                    elif len(auth) == 0:
                        help(4)
                        exit()
                    
                    elif len(auth) > 1:
                        help(5)
                        exit()
                else:
                    help(6)
                    exit() 
                
                UpdateDB('tty')    
                return IPriroot,Comuser,Compass,Spasswd
            else:
                return UserID
        else:
            help(7)
            exit()   
    else:
        help(3)
        exit()
    
    conn.close()

#获取窗口大小
def getwinsize():
    """This returns the window size of the child tty.
    The return value is a tuple of (rows, cols).
    """
    if 'TIOCGWINSZ' in dir(termios):
        TIOCGWINSZ = termios.TIOCGWINSZ
    else:
        TIOCGWINSZ = 1074295912L # Assume
    s = struct.pack('HHHH', 0, 0, 0, 0)
    x = fcntl.ioctl(sys.stdout.fileno(), TIOCGWINSZ, s)
    return struct.unpack('HHHH', x)[0:2]

def Fork(cmd):
    
    AllInfo = GetUserAndPri() #获取主机用户信息及root权限
    iproot = AllInfo[0]
    Comuser = AllInfo[1]
    Compass = MyCrypt('decode', AllInfo[2])
    Spasswd = MyCrypt('decode', AllInfo[3])
    
    if cmd == '-c':
        try:
            localfile = raw_input('localfile>').strip()
            remotedir = raw_input('remotedir>').strip()
        except (KeyboardInterrupt,EOFError):
            exit()
            
        if os.path.isdir(localfile):
            Cmd = 'scp -r %s %s@%s:%s' % (localfile,Comuser,Value['TargetIP'],remotedir)
            
        elif os.path.isfile(localfile): 
            Cmd = 'scp %s %s@%s:%s' % (localfile,Comuser,Value['TargetIP'],remotedir)
        
        else:
            help(12)
            exit()
        
        try:
            scp = pexpect.spawn(Cmd)
            i = scp.expect(['assword:', 'continue connecting (yes/no)?','\$'], timeout=None)
            fout = open(fname,'w')
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
            fout.write('scp %s localfile:%s  remotedir:%s \n' % (Value['TargetIP'],localfile,remotedir))
            fout.close() 
                
        except (KeyboardInterrupt,EOFError,UnboundLocalError):
            exit()         
        except pexpect.EOF:
            print "Connect Error"
        except pexpect.TIMEOUT:
            print 'TIMEOUT'
            
    
    elif cmd == '-b':
        try:
            remotefile = raw_input('remotefile>').strip()
            localdir = raw_input('localdir>').strip()
        except (KeyboardInterrupt,EOFError):
            exit()
            
        if os.path.isdir(localdir):
            Cmd = 'scp -r %s@%s:%s %s' % (Comuser,Value['TargetIP'],remotefile,localdir)
        else:
            help(11)
            exit()
            
        
        try:
            scp = pexpect.spawn(Cmd)
            i = scp.expect(['assword:', 'continue connecting (yes/no)?','\$'], timeout=None)
            fout = open(fname,'w')
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
            fout.write('scp %s remotefir:%s localdir:%s \n' % (Value['TargetIP'],remotefile,localdir))
            fout.close()  
            
        except (KeyboardInterrupt,EOFError,UnboundLocalError):
            exit()         
        except pexpect.EOF:
            print "Connect Error"
        except pexpect.TIMEOUT:
            print 'TIMEOUT'
        

        
    elif cmd == '-s' and iproot:
        ssh = pexpect.spawn('ssh %s@%s' % (Comuser,Value['TargetIP']))
        fout = open(fname,'w')
        ssh.logfile = fout   #记录日志
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
                winsize = getwinsize()
                ssh.setwinsize(winsize[0], winsize[1])
                ssh.interact(escape_character = chr(28),input_filter = None, output_filter = None)
                UpdateDB(cmd='Utty')
                
            except:
                sys.exit()
            
        except (KeyboardInterrupt,EOFError):
            exit()         
        except pexpect.EOF:
            print "Connect Error"
            ssh.close()
        except pexpect.TIMEOUT:
            print 'TIMEOUT'
            ssh.close()
        fout.close()  
    
        
    
    elif cmd ==0 :
        ssh = pexpect.spawn('ssh %s@%s' % (Comuser,Value['TargetIP']))
        fout = open(fname,'w')
        ssh.logfile = fout 
        try:
            i = ssh.expect(['assword:', 'continue connecting (yes/no)?','\$'], timeout=15)
            if i == 0:
                ssh.delaybeforesend = 0.05
                ssh.sendline('%s' % Compass)
            elif i == 1:
                ssh.sendline('yes')
                ssh.expect('assword:')
                ssh.delaybeforesend = 0.05
                ssh.sendline('%s' % Compass)
            
            try:
                winsize = getwinsize()
                ssh.setwinsize(winsize[0], winsize[1])
                ssh.interact(escape_character = chr(28),input_filter = None, output_filter = None)
                UpdateDB(cmd='Utty')
            except:
                sys.exit()
            
        except (KeyboardInterrupt,EOFError):
            exit()
        except pexpect.EOF:
            print "Connect Error"
            ssh.close()
        except pexpect.TIMEOUT:
            print 'TIMEOUT'
            ssh.close()
        fout.close()  

    else:
        help(9)
        exit()

  
def Filter():  
#===============================================================================
# 默认直接登录
# -l 用户权限获取 用户权限更新 用户修改登陆密码 用户
# -s root用户登陆
# -c 文件传输
# -b 文件下载到本地
# 
#
#===============================================================================
    
    if Value['ForkCmd'] == '-l' and GetUserAndPri():
        Menu()
    
    elif Value['ForkCmd'] in ('-s','-p','-c','-b'):
        Fork(Value['ForkCmd'])    
           
    else:
        Fork(0)
        

def Init(value):
    #配置文件及时间的变量
    import json
    
    global ConF
    global now
    global DD
    global fname
    global Value
    
    #配置文件
    Config = '/opt/PyLogin/.config.ini'
    configfile = '/opt/PyLogin/.Config.ini'
    LogDir = '/var/log/.PyLogin'
    ConF = {}
    
    with open(Config,'r') as fn:
        for i in fn.readlines():
            #可以使用 'DATABASE' in i 的简单方式
            if i.find('DATABASE') == 0 :
                ConF['db'] = MyCrypt('decode',i.strip('\n').split(':')[1])
            if i.find('USER') == 0 :
                ConF['user'] = MyCrypt('decode',i.strip('\n').split(':')[1])
            if i.find('PASSWD') == 0:
                ConF['passwd'] = MyCrypt('decode',i.strip('\n').split(':')[1])
            if i.find('HOST') == 0:
                ConF['host'] = MyCrypt('decode',i.strip('\n').split(':')[1])
        
    '''
    #以后可以考虑每个服务器上都部署，需要将配置文件加密或者写死
    fname = shelve.open(configfile,writeback=True)
    for index in ConF:
        fname[index] = ConF[index]
    fname.close()
    '''
            
    try:     
        if ConF['db'] == '' or ConF['user'] == '' or ConF['passwd'] == '' or ConF['host'] == '' :
            help(2)
            exit()
    except (NameError,KeyError),e:
        help(2)
        
    fn.close()
    
    #获取参数
    Value = value
    
    #创建操作日志文件
    if os.path.isdir(LogDir):
        pass
    else:
        os.umask(0)     #文件夹权限
        os.makedirs(LogDir)
    
    now = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
    DD = time.strftime('%Y%m%d%H%M%S',time.localtime())
    fname = LogDir + '/' + DD + '_' + Value['User'] +'.txt'
  
    #主程序入口
    Filter()
        

if __name__ == '__main__':
    #登陆用户名密码

    if len(sys.argv) < 2:
        print '''
Usage: 
    %s <Server IP> 
    OR
    %s <Server IP> Command 
    ''' % (sys.argv[0],sys.argv[0])
        exit()
    try:
        User = raw_input('Your name: ')
        Passwd = getpass.getpass()
        
        
        
        ##ipaddress
        if check_ip(sys.argv[1]):
            value={'Execfile':sys.argv[0],'User':User,'Passwd':Passwd,'TargetIP':check_ip(sys.argv[1]),'ForkCmd':0}
        
        elif sys.argv[1] in ('-s','-p','-c','-b') and check_ip(sys.argv[2]):
            value={'Execfile':sys.argv[0],'User':User,'Passwd':Passwd,'TargetIP':check_ip(sys.argv[2]),'ForkCmd':sys.argv[1]}
        
        elif sys.argv[1] == '-l':
            value={'Execfile':sys.argv[0],'User':User,'Passwd':Passwd,'TargetIP':0,'ForkCmd':sys.argv[1]}
    
        else:
            exit()       
            
        Init(value)
        
    except (KeyboardInterrupt,EOFError):
        exit()
