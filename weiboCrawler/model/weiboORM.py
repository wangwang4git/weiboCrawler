#!/usr/bin/env python
# -*- coding: utf-8 -*-

from peewee import *
import datetime

weiboDB = SqliteDatabase('weibodata.db', threadlocals = True)

class BaseModel(Model):
    class Meta:
        database = weiboDB

class Weibo(BaseModel):
    mid = CharField(unique = True)
    date = DateTimeField(default = datetime.date.today)
    name = TextField()
    userurl = TextField()
    content = TextField()
    weibourl = TextField()
