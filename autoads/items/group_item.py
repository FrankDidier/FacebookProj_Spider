# -*- coding: utf-8 -*-
"""
Created on 2022-06-10 23:56:14
---------
@summary:
---------
@author: Administrator
"""

from autoads.item import Item
from autoads.config import config


class GroupItem(Item):
    __table_name__ = config.groups_table
    __update_key__ = ('status', 'last_apply_time', 'apply_nums')

    def __init__(self):
        self.word = None
        self.group_name = None
        self.group_link = None
        self.unique_key = ('group_link',)
        self.ads_id = None  # 使用的浏览器id，会对应facebook账号，在获取成员的时候就直接使用此id
        self.create_time = None  # 首次爬取日期
        self.last_apply_time = ''  # 最近一次申请的日期
        self.apply_nums = 0  # 默认申请是0次，达到了3次就不再申请了
        self.status = 'unknown'  # 默认是未知的  unknown,apply,public,apply-join  未知、需要申请、公开、已经加入
        self.priority = 300
