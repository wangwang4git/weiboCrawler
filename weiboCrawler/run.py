#!/usr/bin/env python
# -*- coding: utf-8 -*-

from model.log4py import logInfo
from model.log4py import logWarn
from model.log4py import logError
from model import syscontext
from sina.loginsinaweibo import LoginSinaWeibo

def run():
    username = syscontext.user.get('un', 'wwang1969@126')
    password = syscontext.user.get('pw', 'w196988')

    file_path = syscontext.config.get('temp', './temp')
    sina = LoginSinaWeibo(soft_path = file_path)
    if sina.check_cookie(username, password, file_path):
        loginValid = 'sina weibo login sucess!'
        logInfo(loginValid)
    else:
        loginValid = 'sina weibo login failure, check username/password!'
        logInfo(loginValid)


if __name__ == '__main__':
    logInfo('hello')
    run()