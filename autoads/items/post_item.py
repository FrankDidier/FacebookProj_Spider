# -*- coding: utf-8 -*-
"""
Facebook Group Post Item
"""
from autoads.item import Item
from autoads.config import config


class PostItem(Item):
    __table_name__ = './fb/post/'
    __update_key__ = ('status', 'update_time')

    def __init__(self):
        self.group_name = None
        self.group_link = None
        self.post_id = None
        self.post_link = None
        self.post_content = None
        self.post_author = None
        self.post_author_link = None
        self.post_time = None
        self.likes_count = 0
        self.comments_count = 0
        self.shares_count = 0
        self.ads_id = None
        self.create_time = None
        self.update_time = None
        self.status = 'init'  # init, collected, failed
        self.unique_key = ('post_link',)

