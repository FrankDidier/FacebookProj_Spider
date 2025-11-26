#!/anaconda3/bin python3.7
# -*- coding: utf-8 -*-
# ---
# @Software: PyCharm
# @File: ins_item.py
# @Author: James.Zhou
# @E-mail: 407360491@163.com
# @Site: 
# @Time: 十月 07, 2022
# ---
from autoads.item import Item
from autoads.config import config


class ArticleItem(Item):
    __table_name__ = config.get_option('table', 'ins_post')
    __update_key__ = ('mp4', 'status')

    def __init__(self):
        self.ads_id = None  # 使用的浏览器id，会对应tiktok账号，在获取成员的时候就直接使用此id
        self.user_page = None  # 用户主页
        self.post = None  # 视频帖子地址
        self.mp4 = None  # 视频真实下载地址
        self.status = 'init'  # 视频帖子的状态，init,parse-success,parse-fail,download-success,download-fail
        self.unique_key = ('post',)
