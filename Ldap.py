#-*- coding: UTF-8 -*-
# from django.conf import settings
import sys,ldap
import logging
import logging.handlers

# LDAP_HOST = 'ldap://134.96.138.107'
# USER = 'cn=Manager,dc=ecp,dc=com'
# PASSWORD = '20070522'
# BASE_DN = 'dc=ecp,dc=com'

LDAP_HOST = 'ldap://10.0.0.200'
USER = 'cn=admin,dc=huored,dc=com'
PASSWORD = 'huored'
BASE_DN = 'dc=huoredsb,dc=com'

"log info"
#LOG_FILE = '/var/log/.PyLogin/Ldap.log'
LOG_FILE = 'D:\logs\Ldap.log'
logger = logging.getLogger('Ldap')    # 获取名为Ldap的logger
logger.setLevel(logging.INFO)
handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes = 1024*1024) # 实例化handler 
formatter = logging.Formatter('%(asctime)s- %(levelname)s - %(message)s')   # 实例化formatter
handler.setFormatter(formatter)      # 为handler添加formatter
logger.addHandler(handler)  




class LDAP(object):      
    def __init__(self,ldap_host=None,base_dn=None,user=None,password=None):
        if not ldap_host:
            ldap_host = LDAP_HOST
        if not base_dn:
            self.base_dn = BASE_DN
        if not user:
            self.user = USER
        if not password:
            self.password = PASSWORD
        try:
            ldap.set_option(ldap.OPT_PROTOCOL_VERSION, ldap.VERSION3)
            self.ldapconn = ldap.initialize(ldap_host)
        except ldap.LDAPError,e:
            logger.error(e)
  
  
    def ldap_get_vaild(self,uid=None,passwd=None):
        target_cn = self.ldap_search_dn(uid)
        try:
            try:
                logger.info('target_cn: %s' % target_cn)
                if self.ldapconn.simple_bind_s(target_cn,passwd):
                    logger.info('user:%s check vaild success' % uid)
                    return True
                else:
                    return False
            except ldap.LDAPError,e:
                logger.warn('ldap_get_vaild user: %s %s' % (uid,e))
                
        except Exception,e:
            logger.error('ldap_get_vaild user: %s %s' % (uid,e))
                

    def ldap_search_dn(self,uid=None):
        searchScope = ldap.SCOPE_SUBTREE
        retrieveAttributes = None
        searchFilter = "uid=" + uid
        try:
            try:
                self.ldapconn.simple_bind_s(self.user,self.password)
                logger.info('Manager bind success!')
                ldap_result_id = self.ldapconn.search(self.base_dn, searchScope, searchFilter, retrieveAttributes)
                result_type, result_data = self.ldapconn.result(ldap_result_id, 0)
    
                if result_type == ldap.RES_SEARCH_ENTRY:
                    #dn = result[0][0]
                    return result_data[0][0]
                else:
                    return None
            except ldap.LDAPError, e:
                logger.warn('ldap_search_dn user: %s %s' % (uid,e))
        except Exception,e:
            logger.error('ldap_get_vaild user: %s %s' % (uid,e))
        
    #查询用户记录，返回需要的信息
    def ldap_get_user(self,uid=None):
        searchScope = ldap.SCOPE_SUBTREE
        retrieveAttributes = None
        searchFilter = "uid=" + uid
        try:
            try:
                ldap_result_id = self.ldapconn.search(self.base_dn, searchScope, searchFilter, retrieveAttributes)
                result_type, result_data = self.ldapconn.result(ldap_result_id, 0)
                
                if result_type == ldap.RES_SEARCH_ENTRY:
                    username = result_data[0][1]['cn'][0]
                    uidNumber = result_data[0][1]['uidNumber'][0]
                    homeDirectory = result_data[0][1]['homeDirectory'][0]
                    result = {'username':username,'uid':uidNumber,'home':homeDirectory}
                    logger.info('user:%s check user info success:%s' % (uid,result))
                    return result
                else:
                    return None
            except ldap.LDAPError, e:
                logger.warn('ldap_get_user user: %s %s' % (uid,e))
        except Exception, e:
            logger.error('ldap_get_vaild user: %s %s' % (uid,e))

 
    #修改用户密码
    def ldap_update_pass(self,uid=None,oldpass=None,newpass=None):
        #modify_entry = [(ldap.MOD_REPLACE,'userpassword',newpass)]
        target_cn = self.ldap_search_dn(uid)
        try:
            try:
                #需要绑定manager才有权限改密码
                self.ldapconn.simple_bind_s(self.user,self.password)
                self.ldapconn.passwd_s(target_cn,oldpass,newpass)
                logger.info('user: %s modify passwd success' % uid )
                return True
            except ldap.LDAPError,e:
                logger.warn('user: %s %s' % (uid,e))
                return False
        except Exception, e:
            logger.error('ldap_update_pass: %s %s' % (uid,e))

    #所有用户清单
    def ldap_get_all_users(self,uid='zgt'):
        searchFilter = "(objectClass=*)"
        target_cn = self.ldap_search_dn(uid).split(',',1)[1]
        ldap_result = self.ldapconn.search_s(target_cn,ldap.SCOPE_SUBTREE,searchFilter,['cn'])
        return ldap_result
    
if __name__ == '__main__' :
    MyLdap=LDAP()
    # print MyLdap.ldap_update_pass('zgt','1','200770522')
    for dn,entry in MyLdap.ldap_get_all_users():
       if len(entry.values()) > 0:
           print entry.values()[0][0],MyLdap.ldap_get_user(entry.values()[0][0])['uid']
    # print MyLdap.ldap_get_vaild('gaotao','123')
    # print MyLdap.ldap_get_user('gaotao')
    #with open('2','r')  as f: 
    #    for i in f.readlines(): 
    #        print i,MyLdap.ldap_get_user(i.strip('\n'))['uid']


