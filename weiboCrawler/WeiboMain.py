#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2015-04-09 20:08:45
# @Author  : VictorWwang (wangwang4whu@126.com)
# @Link    : https://github.com/wangwang4git
# @Version : v0.1

# 参考：http://www.jb51.net/article/44779.htm

import urllib2
import cookielib
import Logger

class WeiboLogin:

    def __init__(self, user, pwd, proxy = False):

        '''
          初始化WeiboLogin对象
          user 用户名
          pwd 密码
          proxy 是否使用代理
        '''

        Logger.logInfo('init WeiboLogin...')
        self.userName = user
        self.passWord = pwd
        self.proxyEnable = proxy

        self.serverUrl = 'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=&rsakt=mod&client=ssologin.js(v1.4.11)&_=1379834957683'
        self.loginUrl = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.11)'
        self.postHeader = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:24.0) Gecko/20100101 Firefox/24.0'}

    def Login(self):
        '''
          登陆操作
        '''

        # cookie或代理服务器配置
        self.EnableCookie(self.proxyEnable)

        # 登陆步骤一
        serverTime, nonce, pubkey, rsakv = self.GetServerTime()
        # 加密用户名、密码
        postData = WeiboEncode.PostEncode(self.userName, self.passWord, serverTime, nonce, pubkey, rsakv)
        Logger.logInfo('post data length:' len(postData))

        #登陆步骤二
        req = urllib2.Request(self.loginUrl, postData, self.postHeader)
        Logger.logInfo('post request...')

        result = urllib2.urlopen(req)
        text = result.read()
        try:
            # 重定向url
            loginUrl = WeiboSearch.sRedirectData(text)
            urllib2.urlopen(loginUrl)
        except:
            Logger.logError('login error！')
            return False

        Logger.logInfo('login sucess!')
        return True

if __name__ == '__main__':
    Logger.logInfo('test')