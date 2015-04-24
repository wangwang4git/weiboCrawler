#!/usr/bin/python
#-*- encoding: utf-8 -*-

class WeiboBean():

    def __init__(self):
        self.mid = ''
        self.name = ''
        self.userurl = ''
        self.content = ''
        self.weibourl = ''

    def __repr__(self):
        return '[ ' + self.mid + '|' + self.name + '|' + self.userurl + ' ]'

    def __str__(self):
        return '[ ' + self.mid + '|' + self.name + '|' + self.userurl + ' ]'

if __name__ == '__main__':
    print WeiboBean()
