# -*- set coding:utf-8 -*-
'''
Created on 2014��4��30��

@author: Administrator
'''

import base64,binascii
import random,string

def MyCrypt(cmd,Orpass):
    if cmd == 'encode' and Orpass:
        try:
            s1 = base64.encodestring(Orpass)
            chars = random.choice(string.letters + string.digits)
            s2 = s1 + chars 
            s3 = base64.encodestring(s2)
            return s3
        except binascii.Error:
            print 'MyCrypt can\'t encode'
            exit()
        
    if cmd == 'decode' and Orpass:
        try:
            s1 = base64.decodestring(Orpass)
            s2 = base64.decodestring(s1[0:-2:])
            return s2
        except binascii.Error:
            print 'MyCrypt can\'t decode'
            exit()
            
def MyOldCrypt(cmd,Orpass):
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

if __name__ == '__main__':
    print MyOldCrypt('encode','W8tZ1elo')