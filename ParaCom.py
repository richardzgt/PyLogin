# -*- set coding:utf-8 -*-
'''
Created on 2014��6��4��

@author: Administrator
'''

import datetime
import sys,os
import threading
import time


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

def Pexpect(ip,user,userpass,cmd):
    try:
        import pexpect
    except ImportError:
        print 'no module named pexpect'

    ssh = pexpect.spawn('ssh %s@%s' % (user,userpass))
    try:
        ssh.expect('continue connecting (yes/no)?', timeout=5)
        ssh.sendline('yes')
        ssh.prompt(timeout=5)
        ssh.sendline(str(cmd))
        return 1
    except pexpect.EOF:
        print "Connect Error"
        ssh.close()
    except pexpect.TIMEOUT:
        print 'TIMEOUT'
        ssh.close()
    except Exception,e:
        print e
        ssh.close()
        sys.exit()
    

def sshCmd(ip,proc,cmd):
    AllInfo = GetPass(ip) #获取主机用户信息及root权限
    Comuser = AllInfo[0]
    Compass = PyLogin.MyCrypt('decode', AllInfo[1])
    Spasswd = PyLogin.MyCrypt('decode', AllInfo[2])
    
    try:
        client = paramiko.SSHClient()
        client.load_system_host_keys()
#        client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        if ip not in ['192.168.100.119','192.168.100.120','192.168.100.121' ]:
            client.connect(ip, 22, Comuser, Compass, timeout=5)
        else:
            Pexpect(ip,'root',Spasswd,cmd)
        
                        
        stdin, stdout, stderr = client.exec_command(cmd)
        lines = stdout.readlines()
        
        for line in lines:
            
            var1,var2 = line.split() 
            
            #检查进程
            if var2 == 'ps':
                if var1 <> '-1':
                    print '%s \t 正在运行 %s 进程号是 %s \n' % (ip,proc,str(line.split()[0]))
                else:
                    print '%s \t 程序 %s 未运行 \n' % (ip,proc)
            
    
            #kill 进程
            if  var2 == 'kill':
                if var1 == '0':
                    print '%s \t kill %s 执行完毕' % (ip,proc)
                else:
                    print '%s \t kill %s 未成功' % (ip,proc)
            
            #start 启动
            if var2 == 'start':
                if var1 == '0':
                    print '%s \t start %s 执行完毕' % (ip,proc)
                else:
                    print '%s \t start %s 未成功' % (ip,proc)
        
            
    except Exception,e:
        print '%s\t 运行失败,失败原因 \n%s' % (ip, e)
        if str(e).find('not found in known_hosts') > -1:
            if Pexpect(ip,Comuser,Compass):
                sshCmd(ip,proc,cmd)                

    finally:
        client.close()

def Commlist():
    threads=[]
    #状态检查

    ##工单及管理
    Menu0 = {'1':'工单接口状态',
             '2':'停工单接口',
             '3':'启动工单接口',
             '4':'能力接口状态',
             '5':'停止能力接口',
             '6':'启动能力接口',
             '7':'APP接入服务状态',
             '8':'停止APP接入服务',
             '9':'启动APP接入服务-无效',
             'q':'退出'}
    Menu1 = {
             '1':'/opt/PyLogin/commlist.properties/gongdanserver',
             '4':'/opt/PyLogin/commlist.properties/nenglijiekou',
             '5':'/opt/PyLogin/commlist.properties/nenglijiekou-stop',
             '6':'/opt/PyLogin/commlist.properties/nenglijiekou-start',
             '7':'/opt/PyLogin/commlist.properties/appjiekou',
             '8':'/opt/PyLogin/commlist.properties/appjiekou-stop',
             '9':'/opt/PyLogin/commlist.properties/appjiekou-start'
    }

    while True:
        keys = sorted(Menu0.keys())
        for key in keys:
            print key,Menu0[key]
            
        choice = raw_input('>').strip()
        
        if choice in Menu0.keys():
            if choice != 'q':
                with open(Menu1[choice],'r') as fobj:
                    for eachline in fobj:
                        if eachline.find('#') != 0:
                            ip = eachline.split('@')[0]
                            proc = eachline.split('@')[1]
                            cmmd = eachline.split('@')[2]
                            th = threading.Thread(target=sshCmd,args=(ip,proc,cmmd))
                            th.start()
                            threads.append(th)  #加入多线程
                            time.sleep(1)
                
            if choice == 'q':
                exit()
    
    for th in threads:
        th.join()
        
    print "程序结束运行%s" % datetime.datetime.now()

    
def Init():
    #配置文件及时间的变量
    global ConF
    global fname
    global commlistdir
    
    #配置文件
    Config = '/opt/PyLogin/.config.ini'
    commlistdir = '/opt/PyLogin/commlist.properties'
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

    
    
    if not os.path.exists(commlistdir):
        print 'not found %s' % commlistdir
        exit()
        

if __name__ == '__main__':
    Init()
    Commlist()