# -*- coding: utf-8 -*-
"""
Facebook Public Page Item
"""
from autoads.item import Item
from autoads.config import config


class PageItem(Item):
    __table_name__ = './fb/page/'
    __update_key__ = ('status', 'update_time')

    def __init__(self):
        self.page_name = None
        self.page_link = None
        self.page_id = None
        self.followers_count = 0
        self.likes_count = 0
        self.page_category = None
        self.page_description = None
        self.ads_id = None
        self.create_time = None
        self.update_time = None
        self.status = 'init'  # init, collected, failed
        self.unique_key = ('page_link',)

