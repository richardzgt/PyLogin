# -*- set coding:utf-8 -*-
'''
Created on 2014年10月9日

@author: Administrator
'''

import sys

try:
    import MyLogger
except ImportError:
    print 'no module named MyLogger'

try:
    import PyLogin
except ImportError:
    print 'no module named PyLogin'

try:
    import MySQLdb
except ImportError:
    print 'no module named MySQLdb'


def help(rtn):
    if rtn == 0:
        print '''
print "Wrong Command" 
    '''
    
    elif rtn == 1:
        print '''
wrong IP
        '''
        
    elif rtn == 2:
        print '''
Config file Syntax error
        '''
        
def GODB(ipaddress):
    try:
        conn = MySQLdb.connect(ConF['host'],ConF['user'],ConF['passwd'],ConF['db'],port=3306,charset='utf8')
    except Exception,e:
            #20140902添加为了防止数据库链接不上报错
        if str(e).find("2003")>-1:
            print "can not connect DB"
        else:
            print 'Mysql-server:',e
        
        sys.exit()        
        
    cursor = conn.cursor()
    SQL = ''' select count(1) from t_HostPasswd where ip='%s'  ''' % ipaddress
    
    cursor.execute(SQL)
    Result = cursor.fetchall()[0][0]
    return Result
        
        
def OMDB(hostname):
    try:
        connOM = MySQLdb.connect(ConF['omhost'],ConF['omuser'],ConF['ompasswd'],ConF['omdb'],port=3306,charset='utf8')
    except Exception,e:
            #20140902添加为了防止数据库链接不上报错
        if str(e).find("2003")>-1:
            print "can not connect OMDB"
        else:
            print 'OM-Mysql-server:',e
        sys.exit()        
        
    cursorOM = connOM.cursor()
    SQL = ''' select host_name,ip_address from server_net_detail where host_name='%s' ''' % hostname
    cursorOM.execute(SQL)
    Result = cursorOM.fetchall()
    
    for hostname,ipaddr in Result:
        if GODB(ipaddr) == 1:
            return ipaddr
        else:
            pass
    return False
   
    
def Init(hostname):
    global ConF
    Config = '/opt/PyLogin/.config.ini'
    ConF = {}
    
    with open(Config,'r') as fn:
        for i in fn.readlines():
            #可以使用 'DATABASE' in i 的简单方式
            if i.find('DATABASE') == 0 :
                ConF['db'] = PyLogin.MyCrypt('decode',i.strip('\n').split(':')[1])
            if i.find('USER') == 0 :
                ConF['user'] = PyLogin.MyCrypt('decode',i.strip('\n').split(':')[1])
            if i.find('PASSWD') == 0:
                ConF['passwd'] = PyLogin.MyCrypt('decode',i.strip('\n').split(':')[1])
            if i.find('HOST') == 0:
                ConF['host'] = PyLogin.MyCrypt('decode',i.strip('\n').split(':')[1])
            #OM config
            if i.find('OMDB') == 0 :
                ConF['omdb'] = PyLogin.MyCrypt('decode',i.strip('\n').split(':')[1])
            if i.find('OMUSER') == 0 :
                ConF['omuser'] = PyLogin.MyCrypt('decode',i.strip('\n').split(':')[1])
            if i.find('OMPASSWD') == 0:
                ConF['ompasswd'] = PyLogin.MyCrypt('decode',i.strip('\n').split(':')[1])
            if i.find('OMHOST') == 0:
                ConF['omhost'] = PyLogin.MyCrypt('decode',i.strip('\n').split(':')[1])
    try:     
        #每个值都必须获得
        if len(ConF.keys()) == len(ConF.values()) == 8:
            return OMDB(hostname)
        else:
            help(2)
            exit()
    except (NameError,KeyError),e:
        help(2)
        
    fn.close()
    

if __name__ == '__main__':
    print Init('cobbler')
    