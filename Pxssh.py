
'''
Created on 2014��7��7��

@author: Administrator
'''

#!/usr/bin/env python

#!/usr/bin/env python

import pxssh
import getpass

try:    # 调用构造函数，创建一个 pxssh 类的对象.    
s = pxssh.pxssh()    
# 获得用户指定 ssh 主机域名.    
hostname = raw_input('hostname: ')   
 # 获得用户指定 ssh 主机用户名.   
 username = raw_input('username: ')    
# 获得用户指定 ssh 主机密码.   
 password = getpass.getpass('password: ')    
# 利用 pxssh 类的 login 方法进行 ssh 登录，
#原始 prompt 为'$' , '#'或'>'    
s.login (hostname, username, password, original_prompt='[$#>]')    
# 发送命令 'uptime'    
s.sendline ('uptime')    
# 匹配 prompt    s.prompt()    
# 将 prompt 前所有内容打印出，即命令 'uptime' 的执行结果.    
print s.before    
# 发送命令 ' ls -l '    s.sendline ('ls -l')    
# 匹配 prompt    s.prompt()    
# 将 prompt 前所有内容打印出，即命令 ' ls -l ' 的执行结果.    
print s.before    
# 退出 ssh session    s.logout()

except pxssh.ExceptionPxssh, e:    
print "pxssh failed on login."    print str(e)