# -*- set coding:utf-8 -*-
'''
Created on 2014��5��20��

@author: Administrator
'''

import MySQLdb


def dbtest():
    conn = MySQLdb.connect('192.168.100.54','Go','Go#2013','Go',port=3306,charset='utf8')
    cursor = conn.cursor()
    cursor.execute('show tables')
    content = cursor.fetchall()
    print content
    
if __name__ == '__main__':
    dbtest()