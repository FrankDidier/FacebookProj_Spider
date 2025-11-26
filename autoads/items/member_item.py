# -*- coding: utf-8 -*-
"""
Created on 2022-06-10 16:44:21
---------
@summary:
---------
@author: Administrator
"""

from autoads.item import Item
from autoads.config import config


class MemberItem(Item):
    __table_name__ = config.members_table
    __update_key__ = ('status',)

    def __init__(self):
        self.group_name=None
        self.group_link = None  # 备份一下是哪个群组里面的成员
        # self.group_type = None  # 备份一下，这个群组是不是需要加入的，如果是需要加入的就需要由指定的ads_id来处理
        self.member_name = None
        self.member_link = None
        self.unique_key = ['member_link']
        self.role_type = None  # 普通用户或者管理员和版主
        self.ads_id = None  # 备份一下，方便下次找的时候能够找到是对应哪个账号操作了当前群组
        self.priority = 300
        self.status='init' # 默认是处于初始化状态，如果发送完成了就更新成send状态
