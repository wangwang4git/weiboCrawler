#!/usr/bin/env python
# -*- coding: utf-8 -*-

# http://s.weibo.com/wb/haha&xsort=time&scope=ori&timescope=custom:2015-04-11-0:2015-04-11-12&page=2
# http://s.weibo.com/wb/【关键词】&xsort=time&scope=ori&timescope=custom:【起始时间】:【终止时间】&page=【页码】

import sys
import threading

from model.log4py import logInfo
from model.log4py import logWarn
from model.log4py import logError
from model import syscontext

class SearchWeiboThread(threading.Thread):

    def __init__(self, id, time, sina):
        threading.Thread.__init__(self)

        self.id = id
        self.time = time
        self.sina = sina
        self.key = syscontext.searchKey

    def run(self):
        try:
            searchResult = ''
            url = 'http://s.weibo.com/wb/%s&xsort=time&scope=ori&timescope=custom:%s:%s&page=%d' \
                % (self.key, '2015-04-11-0', '2015-04-11-12', self.id)
            headers = {
                'Host':'s.weibo.com',
                'User-Agent':'Mozilla/5.0 (Windows NT 6.1; rv:13.0) Gecko/20100101 Firefox/13.0.1',
                'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language':'zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3',
                'Accept-Encoding':'gzip, deflate',
                'Connection':'keep-alive',
                'Referer':'http://s.weibo.com',
                }
            content = self.sina.get_response_content(url, headers)
            if content == '':
                msg = u'%s failure:获取网页内容为空！' % self.id
                logError(msg)
                searchResult = 'error'
            # 后续处理，提取微博信息
        except Exception, e:
            logError(e)
            searchResult = 'error'
            s = sys.exc_info()
            msg = ('getSinaUserInfo Error %s happened on line %d' % (s[1], s[2].tb_lineno))
            logError(msg)


if __name__ == '__main__':
    pass
