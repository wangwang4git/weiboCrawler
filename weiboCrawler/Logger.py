#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2015-04-09 20:08:45
# @Author  : VictorWwang (wangwang4whu@126.com)
# @Link    : https://github.com/wangwang4git
# @Version : v0.1

import logging

# 创建logger
logger = logging.getLogger("weibocrawler")
logger.setLevel(logging.INFO)

# 创建handler
handler = logging.StreamHandler()

# 定义输出格式
formatter = logging.Formatter("%(asctime)s|%(name)s|%(levelname)s|%(message)s")

handler.setFormatter(formatter)
logger.addHandler(handler)

def logInfo(msg):
    logger.info(msg)

def logWarn(msg):
    logger.warn(msg)

def logError(msg):
    logger.error(msg)

if __name__ == '__main__':
    logInfo("test")
    logWarn("test")
    logError("test")
