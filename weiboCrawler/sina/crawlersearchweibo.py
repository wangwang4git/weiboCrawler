#!/usr/bin/env python
# -*- coding: utf-8 -*-

# http://s.weibo.com/wb/haha&xsort=time&scope=ori&timescope=custom:2015-04-11-0:2015-04-11-12&page=2
# http://s.weibo.com/wb/【关键词】&xsort=time&scope=ori&timescope=custom:【起始时间】:【终止时间】&page=【页码】

import threading

from model.log4py import logInfo
from model.log4py import logWarn
from model.log4py import logError
from model import syscontext

class SearchWeiboThread(threading.Thread):

    def __init__(self, id, name, sina):
        threading.Thread.__init__(self)

        self.id = id
        self.name = name
        self.sina = sina
        self.key = syscontext.searchKey

    def run(self):
        self.sina.get_content()


if __name__ == '__main__':
    pass
