#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
插件通用库
"""
import os
import json
import logging

from libs.utils import *


# 日志处理
logger = logging.getLogger('plugin')


# 获取配置项
def load_config(config_file_name):
    if os.path.exists(config_file_name):
        config_file = open(config_file_name, "r+")
        content = config_file.read()
        config_file.close()
        try:
            config_info = convert(json.loads(content.encode("utf-8")))
            logger.debug("load config info success，%s" % content)
            return config_info
        except Exception, e:
            logger.error("load config info fail，%r" % e)
            return None
    else:
        logger.error("config file is not exist. Please check!")
        return None
