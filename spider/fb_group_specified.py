# -*- coding: utf-8 -*-
"""
FB Group Specified Collection - Keyword-based group search
Similar to existing GroupSpider but optimized for specified keyword searches
"""
import autoads
from autoads.log import log
from autoads.action_control import Action
from datetime import datetime
from autoads.items.group_item import GroupItem
from autoads.config import config
config.name = 'config.ini'  # Ensure config is initialized
from autoads import tools
import codecs
import json
import os
from autoads import ads_api
from urllib.parse import urlparse
import threading


class GroupSpecifiedSpider(autoads.AirSpider):
    """FB Group Specified Collection - Search groups by keywords"""

    def start_requests(self):
        if not self.ads_ids:
            self.ads_ids = tools.get_ads_id(self.config.account_nums)

        # Get keywords from config or UI
        key_words = self.config.groups_words if hasattr(self.config, 'groups_words') else []
        
        if not key_words:
            tools.send_message_to_ui(self.ms, self.ui, "请先输入关键词")
            return

        tools.send_message_to_ui(self.ms, self.ui, f"正在根据关键词采集群组: {key_words}")

        i = 0
        priority = 10
        for word in key_words:
            # Check if already processed
            file_name = self.config.groups_table + tools.make_safe_filename(word) + '.txt'
            if os.path.exists(file_name):
                tools.send_message_to_ui(self.ms, self.ui, f'关键词 {word} 已采集过，跳过')
                continue

            if i == len(self.ads_ids):
                i = 0
                priority += 10

            ads_id = self.ads_ids[i]
            i += 1
            url = f"{self.config.groups_url}{word}"
            log.info(f'查询组：{url}')

            yield autoads.Request(
                url=url,
                ads_id=ads_id,
                index=0,
                priority=priority,
                word=word,
                driver_count=len(self.ads_ids),
                stop_event=self.stop_event
            )

    def parse(self, request, response):
        browser = response.browser
        if not browser:
            return

        current_url = browser.current_url
        log.info(f'当前页面URL: {current_url}')

        # Check if redirected (account issue)
        if 'facebook.com/login' in current_url or 'checkpoint' in current_url:
            ads_api.remove_expired_ads(request.ads_id)
            request.webdriver_pool.remove(request.ads_id)
            new_ads_id = tools.get_single_ads(ignore=self.ads_ids)
            if new_ads_id:
                request.ads_id = new_ads_id
                request.request_sync = True
                request.response = None
                tools.send_message_to_ui(self.ms, self.ui, '检测到账号异常，正在更换新账号...')
                yield request
            return

        # Extract groups
        group_link_page = tools.get_page_data_mutilxpath(browser, self.config.groups_xpath_query)
        items_count = len(group_link_page)
        log.info(f'页面中获取到的元素个数：{items_count}-->上一次获取个数：{request.index}')

        group_link_page = group_link_page[request.index:]
        group_table = self.config.groups_table + tools.make_safe_filename(request.word) + '.txt'

        for item in group_link_page:
            insert_item = GroupItem()
            insert_item.__table_name__ = group_table
            insert_item.group_name = item.get_attribute('aria-label')
            temp_link = item.get_attribute('href')
            insert_item.group_link = temp_link[:temp_link.rfind('?')] if '?' in temp_link else temp_link
            insert_item.create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            insert_item.ads_id = request.ads_id
            insert_item.word = request.word
            yield insert_item

        if items_count - request.index > 0:
            tools.send_message_to_ui(
                self.ms, self.ui,
                f'关键词 [{request.word}] 采集到[新{items_count-request.index}/总{items_count}]个群组'
            )

        request.index = items_count
        is_finished = Action(browser).scroll_until_loaded()
        request.request_sync = True

        if is_finished:
            tools.send_message_to_ui(self.ms, self.ui, f'关键词 [{request.word}] 群组采集结束')
            request.index = -1
            yield request
        else:
            yield request

