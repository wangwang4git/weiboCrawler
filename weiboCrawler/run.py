#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
    # httpproxy = syscontext.config.get('httpproxy', 'http://web-proxy.oa.com:8080')
    # sina = LoginSinaWeibo(soft_path = file_path, proxy = httpproxy)
    sina = LoginSinaWeibo(soft_path = file_path)
    if sina.check_cookie(username, password, file_path):
        loginValid = True
        logInfo('sina weibo login sucess!')
    else:
        loginValid = False
        logInfo('sina weibo login failure, check username/password!')

    if loginValid:
        thread1 = SearchWeiboThread(1, 'search-1', sina)
        thread1.start()


if __name__ == '__main__':
    logInfo('hello')
    run()