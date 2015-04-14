#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

from model.log4py import logInfo
from model.log4py import logWarn
from model.log4py import logError
from model import syscontext
from sina.loginsinaweibo import LoginSinaWeibo
from sina.crawlersearchweibo import SearchWeiboThread

def run():
    loginValid = False

    # 模拟登录
    username = syscontext.user.get('un', 'wwang1969@126')
    password = syscontext.user.get('pw', 'w196988')
    file_path = syscontext.config.get('temp', './temp')
    httpproxy = syscontext.config.get('httpproxy', 'http://web-proxy.oa.com:8080')
    # 公司网络，必须走代理
    sina = LoginSinaWeibo(soft_path = file_path, proxy = httpproxy)
    # sina = LoginSinaWeibo(soft_path = file_path)
    if sina.check_cookie(username, password, file_path):
        loginValid = True
        logInfo('sina weibo login sucess!')
    else:
        loginValid = False
        logInfo('sina weibo login failure, check username/password!')

    if loginValid:
        timePref = time.strftime("%Y-%m-%d-", time.localtime())
        start = timePref + '0'
        end = timePref + '23'
        thread1 = SearchWeiboThread(1, start, end, sina)
        thread1.start()


if __name__ == '__main__':
    logInfo('hello')
    run()