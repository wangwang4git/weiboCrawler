#!/usr/bin/python
#-*- encoding: utf-8 -*-

# 参考1：https://github.com/CnPaMeng/WeiboMsgBackupGUI
# 参考2：http://www.jb51.net/article/44779.htm
# 参考3：http://blog.javachen.com/2014/03/18/simulate-weibo-login-in-python/

import urllib
import urllib2
import cookielib
import time
import datetime
import json
import re
import random
import base64
import StringIO
import gzip
import sys
import os

import rsa

from model.log4py import logInfo
from model.log4py import logWarn
from model.log4py import logError
from model import syscontext

'''
新浪微博模拟登录
'''
class LoginSinaWeibo():

    def __init__(self, **kwargs):
        '''
        构造函数
        '''
        self.soft_path = kwargs.get('soft_path', '')
        self.cookiefile = os.path.join(self.soft_path, 'cookie.dat')
        self.proxy = kwargs.get('proxy', '')
        if self.proxy.startswith('http://'):
            self.proxy = self.proxy.replace('http://', '')
        self.pcid = ''
        self.servertime = ''
        self.nonce = ''
        self.pubkey = ''
        self.rsakv = ''

        self.cj = cookielib.LWPCookieJar()
        self.cookie_support = urllib2.HTTPCookieProcessor(self.cj)
        if self.proxy == '':
            self.opener = urllib2.build_opener(self.cookie_support, urllib2.HTTPHandler)
        else:
            self.opener = urllib2.build_opener(self.cookie_support, urllib2.ProxyHandler({'http': self.proxy}))
        urllib2.install_opener(self.opener)

    def __get_millitime(self):
        '''
        获取ms
        '''
        pre = str(int(time.time()))
        pos = str(datetime.datetime.now().microsecond)[:3]
        p = pre + pos
        return p


    def get_servertime(self):
        """
        模拟登录第一步，获取servertime、nonce等信息，用于登录时加密用户名、密码
        """
        url = 'http://login.sina.com.cn/sso/prelogin.php?entry=account&callback=sinaSSOController.preloginCallBack&su=&rsakt=mod&client=ssologin.js(v1.4.2)&_=%s' % self.__get_millitime()
        result = {}
        servertime = None
        nonce = None
        headers = self.__get_headers()
        headers['Host'] = 'login.sina.com.cn'
        headers['Accept'] = '*/*'
        headers['Referer'] = 'http://weibo.com/'
        del headers['Accept-encoding']
        for i in range(3):
            req = self.pack_request(url, headers)
            data = urllib2.urlopen(req).read()
            p = re.compile('\((.*)\)')
            try:
                json_data = p.search(data).group(1)
                data = json.loads(json_data)
                result['servertime'] = str(data['servertime'])
                result['nonce'] = str(data['nonce'])
                result['rsakv'] = str(data['rsakv'])
                result['pubkey'] = str(data['pubkey'])
                self.pcid = str(data['pcid'])

                break
            except Exception, e:
                logError(e)
                msg = 'get severtime error!'
                logError(msg)

                continue
        return result


    def get_global_id(self):
        """
        获取会话（session）ID
        """
        url = 'http://beacon.sina.com.cn/a.gif'
        headers = self.__get_headers()
        headers['Host'] = 'beacon.sina.com.cn'
        headers['Accept'] = 'image/png,image/*;q=0.8,*/*;q=0.5'
        headers['Referer'] = 'http://weibo.com/'
        req = self.pack_request(url, headers)
        urllib2.urlopen(req)


    def get_random_nonce(self, range_num = 6):
        """
        get random nonce key
        """
        nonce = ''
        for i in range(range_num):
            nonce += random.choice('QWERTYUIOPASDFGHJKLZXCVBNM1234567890')

        return nonce


    def dec2hex(self, string_num):
        '''
        10进制转16进制
        '''
        base = [str(x) for x in range(10)] + [chr(x) for x in range(ord('A'), ord('A') + 6)]
        num = int(string_num)
        mid = []
        while True:
            if num == 0:
                break
            num, rem = divmod(num, 16)
            mid.append(base[rem])
        return ''.join([str(x) for x in mid[::-1]])


    def get_pwd(self, pwd, servertime, nonce):
        '''
        模拟登录第二步时，需要对密码加密
        '''
        p = int(self.pubkey, 16)
        pub_key  = rsa.PublicKey(p, int('10001', 16))
        pwd = '%s\t%s\n%s' % (servertime, nonce, pwd)
        pwd =  (self.dec2hex(rsa.transform.bytes2int(rsa.encrypt(pwd.encode('utf-8'), pub_key))))
        return pwd


    def get_user(self, username):
        '''
        用户名编码
        '''
        username_ = urllib.quote(username)
        username = base64.encodestring(username_)[:-1]
        return username


    def login(self, login_un, login_pw):
        '''
        对外暴露的登录接口
        '''
        loginFalg = False
        try:
            try:
                # 步骤一，获取加密用servertime、nonce等信息
                stObj = self.get_servertime()
                self.servertime = stObj.get('servertime')
                self.nonce = stObj.get('nonce')
                self.pubkey = stObj.get('pubkey')
                self.rsakv = stObj.get('rsakv')
            except Exception, e:
                logError(e)
                return False

            self.get_global_id()
            # 步骤二，加密密码登录
            loginHtml = self.do_login(login_un, login_pw)
            loginHtml = loginHtml.replace('"', "'")
            try:
                p = re.compile('location\.replace\(\'(.*?)\'\)')
                login_url = p.search(loginHtml).group(1)
                if 'retcode=0' in loginHtml:
                    # 步骤三，根据步骤二跳转地址，进一步登录，获取cookie信息
                    # 这一步成功才是真的成功！！
                    return self.redo_login(login_url)

                if 'retcode=5' in loginHtml:
                    logError('password or account error.')
                    return False

                if 'retcode=4040' in loginHtml:
                    logError('do login too much times.')
                    return False

                # 需要验证码，悲剧，先报错吧！后续优化~
                if 'retcode=4049' in login_url:
                    logError('nead input verify code, return failure.')
                    return False
            except  Exception, e:
                logError(e)
                s = sys.exc_info()
                msg = ('do login %s happened on line %d' % (s[1], s[2].tb_lineno))
                logError(msg)

                loginFalg = False
        except Exception, e:
            logError(e)
            s = sys.exc_info()
            msg = ('login: %s happened on line %d' % (s[1], s[2].tb_lineno))
            logError(msg)

            loginFalg = False

        return loginFalg


    def do_login(self, login_un, login_pw, door = ''):
        '''
        第二步登录
        '''
        loginFlag = False
        try:
            username = login_un
            pwd = login_pw

            url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.2)'
            # 构造POST体是关键！
            postdata = {
                    'entry': 'weibo',
                    'gateway': '1',
                    'from': '',
                    'savestate': '7',
                    'userticket': '1',
                    'pagerefer' : '',
                    'ssosimplelogin': '1',
                    'vsnf': '1',
                    'vsnval': '',
                    'service': 'miniblog',
                    'pwencode': 'rsa2',
                    'rsakv' : self.rsakv,
                    'encoding': 'UTF-8',
                    'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
                    'returntype': 'META',
                    'prelt' : '26',
                    }
            postdata['servertime'] = self.servertime
            postdata['nonce'] = self.nonce
            postdata['su'] = self.get_user(username)
            postdata['sp'] = self.get_pwd(pwd, self.servertime, self.nonce).lower()
            # 当需要验证码登录的时候，后续优化
            if door:
                postdata['pcid'] = self.pcid
                postdata['door'] = door.lower()

            headers = {
                    'Host': 'login.sina.com.cn',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:17.0) Gecko/20100101 Firefox/17.0',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-encoding': 'gzip, deflate',
                    'Accept-Language': 'zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3',
                    'Connection': 'keep-alive',
                    'Referer'  :  'http://weibo.com/',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    }

            req = self.pack_request(url, headers, postdata)
            result = urllib2.urlopen(req)

            if result.info().get("Content-Encoding") == 'gzip':
                text = self.gzip_data(result.read())
            else:
                text = result.read()

            return text
        except Exception, e:
            logError(e)
            s = sys.exc_info()
            msg = ('do_login: %s happened on line %d' % (s[1], s[2].tb_lineno))
            logError(msg)

            loginFlag = False

        return loginFlag


    def redo_login(self, login_url):
        '''
        第三步登录
        '''
        try:
            headers = self.__get_headers()
            headers['Referer'] = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.2)'
            req = self.pack_request(login_url, headers)
            urllib2.urlopen(req)

            # 保存cookie！！
            self.cj.save(self.cookiefile, True, True)
            msg = 'login success'
            logInfo(msg)

            loginFalg = True
        except Exception, e:
            logError(e)
            s = sys.exc_info()
            msg = ('redo_login %s happened on line %d' % (s[1], s[2].tb_lineno))
            logError(msg)

            loginFalg = False

        return loginFalg


    def check_cookie(self, un, pw, softPath):
        '''
        检查本地cookie文件
        '''
        loginFalg = True
        self.cookiefile = os.path.join(softPath, 'cookie.dat')
        if os.path.exists(self.cookiefile):
            msg = 'cookie dat exist.'
            logInfo(msg)
            if 'Set-Cookie' not in open(self.cookiefile, 'r').read():
                msg = 'but does not contain a valid cookie.'
                logInfo(msg)

                loginFalg = self.login(un, pw)
        else:
            msg = 'cookie dat not exist.'
            logInfo(msg)
            loginFalg = self.login(un, pw)

        if loginFalg:
            return self.valid_cookie()
        else:
            return False


    def valid_cookie(self, html = ''):
        '''
        验证本地cookie文件
        '''
        html = str(html)
        if not html:
            headers = self.__get_headers()
            # 测试李开复主页，判断cookie是否过期
            html = self.get_response_content(url = 'http://weibo.com/kaifulee', headers = headers)

        if not html:
            msg = 'need relogin.'
            logError(msg)

            self.clear_cookiedat(self.cookiefile)
            return False

        html = str(html)
        html = html.replace('"', "'")
        if 'sinaSSOController' in html:
            p = re.compile('location\.replace\(\'(.*?)\'\)')
            try:
                login_url = p.search(html).group(1)
                headers = self.__get_headers()
                headers['Host'] = 'account.weibo.com'
                req = self.pack_request(url = login_url, headers = headers)
                result = urllib2.urlopen(req)
                self.cj.save(self.cookiefile, True, True)

                if result.info().get('Content-Encoding') == 'gzip':
                    html = self.gzipData(result.read())
                else:
                    html = result.read()
            except Exception, e:
                logError(e)
                msg = 'relogin failure.'
                logError(msg)

                self.clear_cookiedat(self.cookiefile)
                return False

        if '违反了新浪微博的安全检测规则' in html:
            msg = 'cookie failure.'
            logError(msg)

            self.clear_cookiedat(self.cookiefile)
            return False
        elif '您的帐号存在异常' in html and '解除限制' in html:
            msg = u'账号被限制.'
            logError(msg)

            self.clear_cookiedat(self.cookiefile)
            return False
        elif "$CONFIG['islogin'] = '0'" in html:
            msg = u'登录失败.'
            logError(msg)

            self.clear_cookiedat(self.cookiefile)
            return False
        elif "$CONFIG['islogin']='1'" in html:
            msg = 'cookie success.'
            logInfo(msg)

            self.cj.save(self.cookiefile, True, True)
            return True
        else:
            msg = u'登录失败.'
            logError(msg)

            self.clear_cookiedat(self.cookiefile)
            return False


    def get_response_content(self, url, headers = {}, data = None):
        '''
        获取响应数据
        '''
        content = ''
        try:
            # 关键的一步，加载模拟登录获取的cookie
            if os.path.exists(self.cookiefile):
                self.cj.revert(self.cookiefile, True, True)
                self.cookie_support = urllib2.HTTPCookieProcessor(self.cj)
                if self.proxy == '':
                    self.opener = urllib2.build_opener(self.cookie_support, urllib2.HTTPHandler)
                else:
                    self.opener = urllib2.build_opener(self.cookie_support, urllib2.ProxyHandler({'http': self.proxy}))
                urllib2.install_opener(self.opener)
            else:
                return ''

            req = self.pack_request(url = url, headers = headers, data = data)
            response = self.opener.open(req, timeout = 10)

            if response.info().get('Content-Encoding') == 'gzip':
                content = self.gzip_data(response.read())
            else:
                content = response.read()
        except urllib2.HTTPError, e:
            logError(e)
            return e.code
        except Exception, e:
            logError(e)
            s=sys.exc_info()
            msg = 'get_content Error %s happened on line %d' % (s[1], s[2].tb_lineno)
            logError(msg)

            content = ''
        return content


    def clear_cookiedat(self, datpath):
        try:
            os.remove(datpath)
        except Exception, e:
            logError(e)


    def pack_request(self, url = '', headers = {}, data = None):
        '''
        封装请求体
        '''
        if data:
            headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
            data = urllib.urlencode(data)

        return urllib2.Request(url = url, data = data, headers = headers)


    def gzip_data(self, spider_data):
        """ get data from gzip """
        if 0 == len(spider_data):
            return spider_data

        spiderDataStream = StringIO.StringIO(spider_data)
        spider_data = gzip.GzipFile(fileobj = spiderDataStream).read()
        return spider_data

    def __get_headers(self):
        headers = {
            'Host': 'weibo.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:13.0) Gecko/20100101 Firefox/13.0.1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-encoding': 'gzip, deflate',
            'Accept-Language': 'zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3',
            'Connection': 'keep-alive',
            }
        return headers
