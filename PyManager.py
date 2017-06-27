#!/usr/bin/env python
# -*- set coding:utf-8 -*-
'''
Created on 2014��3��23��

@author: richardzgt
'''

#===============================================================================
# 管理数据库中的权限及密码记录
# version 2014-08-22
#===============================================================================

import base64
import sys
import os
import MySQLdb
import getpass
import PyLogin
import AuthCode
import time
import goodprint
import Ldap
def help(rtn):
    if rtn == 0:
        print '''

    ''' 
        
    elif rtn == 1:
        print '''
Not of the server or rootAuth wrong type or t_UserAuth exist data
        '''
    elif rtn == 2:
        print '''
config file valid
        '''        
    elif rtn == 3:
        print '''
Config file  Syntax error
        '''      
    elif rtn == 4:
        print '''
Ldap exist user data
        '''
        
    elif rtn == 5:
        print '''
Ldap miss user data
        '''
    elif rtn == 6:
        print '''
t_AdminUser duplicate data
'''

    elif rtn == 7:
        print '''
t_HostPasswd duplicate data
'''

def UAuth(username,ipaddr):
        try:
            conn = MySQLdb.connect(ConF['host'],ConF['user'],ConF['passwd'],ConF['db'],port=3306,charset='utf8')
            cursor = conn.cursor()
            
            if PyLogin.check_ip(ipaddr):  
                SQL = ''' select b.IP,a.IPiroot from  t_UserAuth a,t_HostPasswd b where a.UserID=%s and b.ID=a.HPID and b.ip='%s' ''' % (MyLdap.ldap_get_user(username)['uid'],ipaddr)
           
            else:
                SQL = ''' select b.IP,a.IPiroot from  t_UserAuth a,t_HostPasswd b where a.UserID=%s and b.ID=a.HPID and b.ip like '%%%s%%' ''' % (MyLdap.ldap_get_user(username)['uid'],ipaddr)
            
            cursor.execute(SQL)
            for each in cursor.fetchall():
                print '%s    %s' % (each[0],each[1])
        except Exception,e:
            print e
            sys.exit()

def MyDB(cmd):
    dict = {}
    try:
        conn = MySQLdb.connect(ConF['host'],ConF['user'],ConF['passwd'],ConF['db'],port=3306,charset='utf8')
        cursor = conn.cursor()
        cursor.execute('''update t_AdminUser set logintime=sysdate() where admin='%s' ''' % PyLogin.MyCrypt('encode',Admin) )  
    except Exception,e:
        print e
        sys.exit()
 
 
#0 Admin Init()
#=======================================================================
# 
#=======================================================================
    if cmd == 'admin':
        Addict = {}
        cursor.execute('''select admin,adpass from t_AdminUser''')
        content = cursor.fetchall()
        for i in range(len(content)):
            Addict[PyLogin.MyCrypt('decode',str(content[i][0]))] = PyLogin.MyCrypt('decode',str(content[i][1])) 
        return(Addict)
        
        
#1 修改服务器密码记录
#===============================================================================
#1 指定服务器  ModHostPass  指定服务器进行密码修改，可以修改登陆用户名、密码及root用户密码，
#    如果要改ip地址，就只能进数据库改
#2 批量base64加密  BaseBATCH 当t_HostPasswd全部是明文密码时，采用加密
#3 导入密码文件 PassFile  直接导入密码文件[添加服务器]
#格式：
#    IP  用户(ecp/oracle/mysql) 用户密码    root密码 
#4 删除服务器
#===============================================================================
    if cmd == 'ModHostPass':
        try:
            ipaddress = raw_input('ipaddress: ')
            Comuser = raw_input('common user: ')
            Compass = raw_input('common password: ') 
            Spasswd = raw_input('root password: ') 
            SQL1 = 'select ip from  t_HostPasswd where ip=\'%s\'' % ipaddress
            cursor.execute(SQL1)
            if len(cursor.fetchall()) == 1:
                SQL2 = 'update t_HostPasswd set user=\'%s\',password=\'%s\',spassword=\'%s\' where ip=\'%s\'' % \
            (Comuser,PyLogin.MyCrypt('encode',Compass),PyLogin.MyCrypt('encode',Spasswd),ipaddress) 
                cursor.execute(SQL2)
                print '---- execute ok -----'
        except (KeyboardInterrupt,EOFError):
            exit()
            
            
    if cmd == 'BaseBATCH':
        cursor.execute('select ip,password from t_HostPasswd')
        PW = cursor.fetchall()
        
        for i in PW:
            dict[i[0]] = PyLogin.MyCrypt('encode',i[1])
            
        for key in dict.keys():
            print key,dict[key]
            cursor.execute('update t_HostPasswd set password=\'%s\' where ip=\'%s\'' % (dict[key],key))
   
    if cmd == 'PassFile':
        fname = raw_input('输入密码文件:')
        if os.path.exists(fname):
            file = open(fname,'r')
            for i in file.readlines():
                SQL1 = 'select count(ip) from  t_HostPasswd where ip=\'%s\'' % i.split()[0]
                cursor.execute(SQL1)
                hostinfo = cursor.fetchall()
                if hostinfo[0][0] == 0:
                    print i.split()[0],i.split()[1],PyLogin.MyCrypt('encode',i.split()[2]),PyLogin.MyCrypt('encode',i.split()[3])
                    SQL2 = 'insert into t_HostPasswd (ip,user,password,spassword)values(\'%s\',\'%s\',\'%s\',\'%s\')' % \
                    (i.split()[0],i.split()[1],PyLogin.MyCrypt('encode',i.split()[2]),PyLogin.MyCrypt('encode',i.split()[3])) 
                    cursor.execute(SQL2)
                    print '---- execute ok -----'
                else:
                    help(7)
            file.close()

    if cmd == 'DelServ':
        try:
            ipaddress = raw_input('ipaddress: ')
            SQL1 = 'select ip from  t_HostPasswd where ip=\'%s\'' % ipaddress
            cursor.execute(SQL1)
            if len(cursor.fetchall()) == 1:
                SQL2 = '''DELETE FROM t_HostPassLog WHERE HPID=(SELECT id FROM t_HostPasswd WHERE ip='%s') ''' % ipaddress 
                SQL3 = ''' DELETE FROM t_HostPasswd WHERE ip='%s' ''' % ipaddress
                SQL4 = ''' DELETE FROM t_UserAuth WHERE HPID=(SELECT id FROM t_HostPasswd WHERE ip='%s') ''' % ipaddress
                cursor.execute(SQL2)
                cursor.execute(SQL3)
                cursor.execute(SQL4)
                print '---- execute ok -----'
            else:
                print '---- execute failure ---'    
            
        except (KeyboardInterrupt,EOFError):
            exit()        

        
#2 修改登陆权限
#===============================================================================
#1  用户指定增加权限  Addsingle 指定用户增加登陆权限（root可选）
#2  权限表去重  DelDup 权限表去重，防止多次 赋权造成的权限表重复
#3  删除用户权限 Delsingle  指定用户删除登陆权限，包括root权限
#4  批量赋权
#格式：
#   登陆用户     IP  是否root？(0/1)
#5  增加用户 AddComm  增加一个登陆用户
#6  删除用户 deluser
#7  用户列表 ListUsers
#===============================================================================
    if cmd == 'Addsingle':
        try:
            username = raw_input('username: ').split()[0]
            ipaddr = raw_input('ipaddress: ').split()[0]
            rootAuth = raw_input('RootAuth(1/0): ').split()[0]  
        
        except (KeyboardInterrupt,EOFError):
            exit()
        
        SQL1 = 'select count(*) from t_HostPasswd where ip=\'%s\'' % ipaddr
        cursor.execute(SQL1)
        IPinHP = cursor.fetchall()[0][0]  #t_HostPasswd确认主机是否存在
        if IPinHP == 1:
            SQL2 = ''' select count(*) from t_UserAuth a,t_HostPasswd b where a.UserID=%s and b.ID=a.HPID and b.ip='%s' ''' % (MyLdap.ldap_get_user(username)['uid'],ipaddr)
            cursor.execute(SQL2)
            CuAuth = cursor.fetchall()[0][0]  #t_UserAuth不要重复数据
        
        
            if IPinHP == 1 and CuAuth == 0 and rootAuth in ('1','0') :            
                SQL3 = ''' insert into t_UserAuth (UserID,HPID,IPiroot)values(%s, 
                (select ID from t_HostPasswd where ip='%s'),'%s') ''' % (MyLdap.ldap_get_user(username)['uid'],ipaddr,rootAuth) 
                cursor.execute(SQL3)
                print '---- execute ok -----'
            
                UAuth(username,ipaddr)
        else:
            help(1)
            
    if cmd =='DelDup': #t_UserAuth去重复
        SQL1=''' delete from t_UserAuth where SQUAuth in (select SQUAuth from (  
            select SQUAuth from t_UserAuth  a  where (a.HPID,a.UserID) in (select HPID,UserID from t_UserAuth group by HPID,UserID having count(*)>1) 
            and SQUAuth not in (select min(SQUAuth) from t_UserAuth group by HPID,UserID having count(*)>1)) tn ) '''
        cursor.execute(SQL1)
        print '----t_UserAuth execute ok -----'
        
        SQL2='delete from t_HostPasswd where id in (select id from (select id from t_HostPasswd where id not in \
        (select max(id) from t_HostPasswd group by ip having count(ip)>1)and id in (select id from t_HostPasswd group by ip having count(ip)>1)) tb)'
        cursor.execute(SQL2)
        print '----t_HostPasswd execute ok -----'        
    
    if cmd =='Delsingle': 
        try:
            username = raw_input('username: ')
            ipaddr = raw_input('ipaddress: ') 
        
        except (KeyboardInterrupt,EOFError):
            exit()
            
        SQL1 = 'select count(*) from t_HostPasswd where ip=\'%s\'' % ipaddr
        cursor.execute(SQL1)
        IPinHP = cursor.fetchall()[0][0]  #t_HostPasswd确认主机是否存在
        if IPinHP == 1:
            SQL2 = ''' select count(*) from t_UserAuth a,t_HostPasswd c where a.UserID=%s and c.IP='%s' and c.ID=a.HPID  ''' % (MyLdap.ldap_get_user(username)['uid'],ipaddr)
            cursor.execute(SQL2)
            CuAuth = cursor.fetchall()[0][0]  
        
            if CuAuth == 1:       #t_UserAuth防止重复数据     
                SQL3 = ''' delete from t_UserAuth where Userid = %s
                and HPID =(select ID from t_HostPasswd where ip='%s')  ''' % (MyLdap.ldap_get_user(username)['uid'],ipaddr) 
                cursor.execute(SQL3)
                print '---- execute ok -----'
        else:
            help(1)
        
    if cmd == 'UserFile': #导入用户权限文件
        fname = raw_input('输入用户权限文件:')
        if os.path.exists(fname):
            file = open(fname,'r')
            for i in file.readlines():
                print i.split()[0],i.split()[1],i.split()[2]
                SQL = '''insert into t_UserAuth (UserID,HPID,IPiroot)values(%s,(select ID from t_HostPasswd where ip='%s'),'%s') ''' \
                % (MyLdap.ldap_get_user(i)['uid'],i.split()[1],i.split()[2])
                cursor.execute(SQL)
                print '---- execute ok -----'
            file.close()


    if cmd == 'ListUsers':
        Userlist = []

        for dn,entry in MyLdap.ldap_get_all_users():
            if len(entry.values()) > 0:
                Userlist.append(entry.values()[0][0],MyLdap.ldap_get_user(entry.values()[0][0])['uid'])
        
        goodprint.GoodPrint(Userlist)
                        
# 3  超级用户权限
#===============================================================================
#1  用户服务器提权  AddSuperSingle  赋权某个用户的某个服务器的root权限
#2  用户服务器降权  DelSuperSingle  删去某个用户的某个服务器的root权限
#3  增加超级用户 SuperAdmin   赋权某个用户所有服务器的root权限
#4  返回
#===============================================================================
    if cmd == 'AddSuperSingle': 
        try:
            username = raw_input('username: ')
            ipaddr = raw_input('ipaddress: ') 
            SQL1 = ''' select a.squauth from t_UserAuth a,t_HostPasswd b where a.UserID=%s and b.ID=a.HPID and b.ip='%s' ''' % (MyLdap.ldap_get_user(username)['uid'],ipaddr)
            cursor.execute(SQL1)
            try:
                squauth = cursor.fetchall()[0][0]
                if squauth :
                    SQL2 = 'update t_UserAuth set IPiroot=\'1\' where  squauth=\'%s\'' % (squauth)
                    cursor.execute(SQL2)
                    print '---- execute ok -----'
                    UAuth(username,ipaddr)
            except IndexError,e:
                help(5)
            
        except (KeyboardInterrupt,EOFError):
            exit()
            
            
    if cmd == 'DelSuperSingle':
        try:
            username = raw_input('username: ')
            ipaddr = raw_input('ipaddress: ') 
            SQL1 = ''' select a.squauth from t_UserAuth a,t_HostPasswd b where a.UserID=%s and b.ID=a.HPID and b.ip='%s' ''' % (MyLdap.ldap_get_user(username)['uid'],ipaddr)
            cursor.execute(SQL1)
            try:
                squauth = cursor.fetchall()[0][0]
                if squauth :
                    SQL2 = 'update t_UserAuth set IPiroot=\'0\' where squauth=\'%s\'' % (squauth)
                    cursor.execute(SQL2)
                    print '---- execute ok -----'
                    UAuth(username,ipaddr)
            except IndexError,e:
                help(5) 
            
        except (KeyboardInterrupt,EOFError):
            exit()        
        
    if cmd == 'SuperAdmin': #一键超级用户
        username = raw_input('username: ')
        SQL1 = (''' INSERT INTO t_UserAuth(UserID,hpid,IPiroot)
            SELECT {0},a.id,1 FROM t_HostPasswd a WHERE a.id NOT IN (
            SELECT  a.hpid FROM t_UserAuth a WHERE a.UserID={0})''').format(MyLdap.ldap_get_user(username)['uid'])
        cursor.execute(SQL1)
        SQL2=''' update t_UserAuth set IPiroot='1' where userid=%s ''' % MyLdap.ldap_get_user(username)['uid']
        cursor.execute(SQL2)
        print '---- execute ok -----'
        
    
# 4 查询登陆历史
#===============================================================================
#1 用以查询登陆历史 HistList
#2 用以查询 用户权限 
#3 用以查询服务器列表  Serlist 
#4 查询服务器密码列表 ListHostPass
#===============================================================================

    if cmd == 'AdminInfo':
        SQL1=''' select telephone,now()-ListPasstime from t_AdminUser where admin='%s' ''' % (PyLogin.MyCrypt('encode',Admin))
        cursor.execute(SQL1)
        
        content = cursor.fetchall()
        
        if len(content) == 1:
            tel = content[0][0]
            falltime = content[0][1]
            
            if falltime > 600:
                return tel
            else:
                return False
             
        else:
            help(6)
            exit()
            

    if cmd == 'UpPassTime':
        SQL2='''update t_AdminUser set ListPasstime=sysdate() where admin='%s' ''' % (PyLogin.MyCrypt('encode',Admin))
        cursor.execute(SQL2)
            


    if cmd == 'Serlist':
        mycontent = []
        try:
            ipaddr = raw_input('ipaddress: ').strip()
            
             
            if  PyLogin.check_ip(ipaddr):
                SQL='''select a.ip,a.user,a.password,a.spassword,b.mtime from t_HostPasswd a  left join t_HostPassLog b
                    on a.id=b.hpid where ip='%s' ''' % ipaddr
            else:
                SQL='''select a.ip,a.user,a.password,a.spassword,b.mtime from t_HostPasswd a  left join t_HostPassLog b
                    on a.id=b.hpid where ip like '%s%%' or ip like '%%%s%%' or ip like '%%%s' ''' % (ipaddr,ipaddr,ipaddr)
            cursor.execute(SQL) 
            
            try:
                print '''IPaddress    Comuser     Compass    RootPassword   ModifyTime'''
                for x in [ j for j in [ i for i in cursor.fetchall() ]]:
                    mycontent.append([x[0],x[1],PyLogin.MyCrypt('decode',x[2]),PyLogin.MyCrypt('decode',x[3]),x[4]])
                
                goodprint.GoodPrint(mycontent)
                
                print '''
                
                
                '''
                
            except IndexError,e:
                print 'Not of server'
                exit()
            
        except KeyboardInterrupt:
            exit()
    
    conn.close()

def Menu():
    Menu0 = {'1':'修改服务器密码记录','2':'修改登陆权限','3':'超级用户权限','4':'查询密码及用户权限','5':'退出'}
    Menu1 = {'1':'指定服务器','2':'批量base64加密','3':'导入密码文件[添加服务器]','4':'删除服务器','5':'返回'}
    Menu2 = {'1':'用户指定增加权限','2':'服务器、权限表去重','3':'删除用户指定权限','4':'批量赋权','5':'增加用户-停','6':'删除用户-停','7':'用户列表','8':'返回'}
    Menu3 = {'1':'用户服务器提权','2':'用户服务器降权','3':'增加超级用户','4':'返回'}
    Menu4 = {'1':'登陆历史查询','2':'用户权限查询','3':'服务器及密码查询','4':'其他','5':'返回'}
    
    while True:
        keys = sorted(Menu0.keys())
        for key in keys:
            print key,Menu0[key]
        choice = raw_input('>').strip()
        if choice in Menu0.keys():
            
            if choice == '1':  #修改服务器密码记录
                keys = sorted(Menu1.keys())
                for key in keys:
                    print key,Menu1[key]
                choice1 = raw_input('>').strip()
                if choice1 in Menu1.keys():
                    if choice1 == '1':
                        MyDB('ModHostPass')
                    
                    if choice1 == '2':
                        MyDB('BaseBATCH')
                                    
                    if choice1 == '3':
                        MyDB('PassFile')
                        
                    if choice1 == '4':
                        try:
                            phone = MyDB('AdminInfo')
                            if phone:
                                AuthCode.AuthCode(phone)
                                code = raw_input('验证码: ')
                                if AuthCode.AuthCode(phone,0,code):
                                    MyDB('UpPassTime')
                                    MyDB('DelServ')   
                                else:   
                                    print '验证失败'        
                            else:
                                MyDB('DelServ')      
                            
                        except (KeyboardInterrupt,EOFError):
                            exit()
                        
                        
                        
                    if choice1 == '5':
                        continue
            
            if choice == '2': #修改登陆权限
                keys = sorted(Menu2.keys())
                for key in keys:
                    print key,Menu2[key]
                choice2 = raw_input('>').strip()    
                if choice2 in Menu2.keys():
                    if choice2 == '1':
                        MyDB('Addsingle')
             
                    if choice2 == '2':
                        MyDB('DelDup')
                      
                    if choice2 == '3':
                        MyDB('Delsingle')
                        
                    if choice2 == '4':
                        MyDB('UserFile') 
                    
                    if choice2 == '5':
                        #MyDB('AddComm')
                        print 'Not Be Used'
                    
                    if choice2 == '6':
                        print 'Not Be Used'
                        #MyDB('DelUser')
                        
                    if choice2 == '7':
                        try:
                            phone = MyDB('AdminInfo')
                            if phone:
                                AuthCode.AuthCode(phone)
                                code = raw_input('验证码: ')
                                if AuthCode.AuthCode(phone,0,code):
                                    MyDB('UpPassTime')
                                    MyDB('ListUsers')    
                                else:   
                                    print '验证失败'        
                            else:
                                MyDB('ListUsers')       
                            
                        except (KeyboardInterrupt,EOFError):
                            exit()
                        
                        
                    if choice2 == '8':
                        continue    

            if choice == '3':  #超级用户权限
                keys = sorted(Menu3.keys())
                for key in keys:
                    print key,Menu3[key]
                choice2 = raw_input('>').strip()    
                if choice2 in Menu3.keys():
                    if choice2 == '1':
                        MyDB('AddSuperSingle')
                        
                    if choice2 == '2':
                        MyDB('DelSuperSingle')
                    
                    if choice2 == '3':
                        MyDB('SuperAdmin')
                        
                    if choice2 == '4':
                        continue   
                    
            if choice == '4':  #查询登陆历史
                keys = sorted(Menu4.keys())
                for key in keys:
                    print key,Menu4[key]
                choice2 = raw_input('>').strip()    
                if choice2 in Menu4.keys():
                    if choice2 == '1':
                        MyDB('HistList')
                        
                    if choice2 == '2':
                        try:
                            username = raw_input('username: ')
                            ipaddr = raw_input('ipaddress: ') 
                            UAuth(username,ipaddr)
                            print '---- execute ok ----- \n'
            
                        except (KeyboardInterrupt,EOFError):
                            exit()
                    
                    if choice2 == '3':
                        try:
                            phone = MyDB('AdminInfo')
                            if phone:
                                AuthCode.AuthCode(phone)
                                code = raw_input('验证码: ')
                                if AuthCode.AuthCode(phone,0,code):
                                    MyDB('UpPassTime')
                                    MyDB('Serlist')    
                                else:   
                                    print '验证失败'        
                            else:
                                MyDB('Serlist')        
                            
                        except (KeyboardInterrupt,EOFError):
                            exit()
                        

                    if choice2 == '4':
                        pass
                        
                    if choice2 == '5':
                        continue   
                
            
            if choice == '5':  #退出
                exit()    
            
            
                
def Init():
    #配置文件及时间的变量
    
    global now
    global DD
    global ConF
    global MyLdap
    
    ConF = {}
    DD = time.strftime('%Y%m%d%H%M%S',time.localtime())
    #配置文件
    Config = '/opt/PyLogin/.config.ini'
    LogDir = '/var/log/.PyLogin'
    
    
    #Ldap校验用户密码
    MyLdap=Ldap.LDAP()
    
    if os.path.exists(LogDir):
        pass
    else:
        os.umask(0)     #文件夹权限
        os.makedirs(LogDir)

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
#       print ConF['db'],ConF['user'],ConF['passwd'],ConF['host'],ConF['admin'],ConF['adpass']
        if ConF['db'] == '' or ConF['user'] == '' or ConF['passwd'] == '' or ConF['host'] == '':
            help(3)
            return 0
        else:
            return 1
    except (NameError,KeyError),e:
        help(2)
        return 0
            
    fn.close()



if __name__ == '__main__':
    if Init():
        global Admin
        Admin = ''
        addict = {}
        addict = MyDB('admin')
        
        try:
            Admin = raw_input('Input admin name: ')
            Adpass = getpass.getpass('Input admin password: ')
            if addict.has_key(Admin) and Adpass == addict[Admin]:
                Menu()
        except (KeyboardInterrupt,EOFError):
            exit()