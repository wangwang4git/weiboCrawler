#!/usr/bin/env python
# -*- coding: utf-8 -*-

# http://s.weibo.com/weibo/【关键词】&xsort=time&scope=ori&timescope=custom:【起始时间】:【终止时间】&page=【页码】
# http://s.weibo.com/weibo/haha&xsort=time&scope=ori&timescope=custom:2015-04-11-0:2015-04-11-12&page=2

import sys
import threading
import re
import json
from bs4 import BeautifulSoup

from model.log4py import logInfo
from model.log4py import logWarn
from model.log4py import logError
from model import syscontext
from weibocontent import WeiboBean

'''
线程id代表当前线程处理的是搜索结果的第几页
'''
class SearchWeiboThread(threading.Thread):

    def __init__(self, id, start, end, sina):
        threading.Thread.__init__(self)

        self.id = id
        self.startTime = start
        self.endTime = end
        self.sina = sina
        self.key = syscontext.searchKey
        self.weibolist = []

    def run(self):
        reload(sys)
        sys.setdefaultencoding('utf-8')

        try:
            searchResult = ''
            url = 'http://s.weibo.com/weibo/%s&xsort=time&scope=ori&timescope=custom:%s:%s&page=%d' \
                % (self.key, self.startTime, self.endTime, self.id)
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
            # 其他类型错误处理
            # 后续处理，提取微博信息

            result = open('result.html', 'w')
            print >> result, content
            self.fetch(content)

        except Exception, e:
            logError(e)
            searchResult = 'error'
            s = sys.exc_info()
            msg = ('SearchWeiboThread run Error %s happened on line %d' % (s[1], s[2].tb_lineno))
            logError(msg)

    def fetch(self, content):
        '''
        1. 提取json数据， 关键词 <script>STK && STK\.pageletM && STK\.pageletM\.view\((.*)\).*?</script> ；
        2. 提取weibo列表，关键词 <div mid=\\"\d*\\" action-type=\\"feed_list_item\\"> ；
        3.
        '''
        pattern = re.compile(r'<script>STK && STK\.pageletM && STK\.pageletM\.view\((.*)\).*?</script>')
        result = pattern.findall(content)
        if result:
            # 遍历，提取json数据
            for i in range(len(result)):
                strContent = result[i]
                # 剔除Emoji，留个坑，后续解决！！
                pass

                if '"pl_weibo_direct"' in strContent:
                    decodejson = json.loads(strContent)
                    htmlDoc = decodejson['html']

                    result2 = open('result2.html', 'w')
                    print >> result2, htmlDoc

                    soup = BeautifulSoup(htmlDoc)
                    li = soup.find_all('div', {'action-type': 'feed_list_item'})
                    for i in range(len(li)):
                        soupi = li[i]
                        weibo = WeiboBean()

                        weibo.mid = soupi['mid']

                        soupii = soupi.find('div', {'class': 'feed_content wbcon'})
                        weibo.name = soupii.a['nick-name'].decode('gbk')
                        weibo.userurl = soupii.a['href']
                        weibo.content = soupii.p.get_text()

                        print weibo
                        break

                    break


if __name__ == '__main__':
    pass
