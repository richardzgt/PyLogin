# -*- set coding:utf-8 -*-
import paramiko
import tty,sys,os
import termios
import interactive
import time
client = paramiko.SSHClient()
client.load_system_host_keys()
paramiko.util.log_to_file('syslogin.log')
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('192.168.102.40', 22, 'zgt', '20070522', timeout=5)
channel = client.invoke_shell()
time.sleep(0.1)
channel.send('export LC_ALL=zh_CN.UTF-8 \n')
channel.send('su - root \n')

tstr = ''
while not tstr.endswith(('word:','：')):
    resp=channel.recv(9999)
    tstr += resp

channel.send('xttx1234')
channel.send('\n')

tstr = ''
while not tstr.endswith('# '):
    resp=channel.recv(9999)
    tstr += resp
result = tstr
print result,
channel.send('\n')
interactive.interactive_shell(channel)
channel.close()
client.close()

