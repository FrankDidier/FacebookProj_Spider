# -*- coding: utf-8 -*-
"""
FB Group Member Rapid Collection - Fast member collection with optimized performance
"""
import autoads
from autoads.items.member_item import MemberItem
from autoads.items.group_item import GroupItem
from autoads.log import log
from autoads.action_control import Action
from datetime import datetime
from autoads import tools
from autoads.config import config
config.name = 'config.ini'  # Ensure config is initialized
import json
import os
from urllib.parse import urlparse
from autoads import ads_api
import threading


class MembersRapidSpider(autoads.AirSpider):
    """Fast member collection with optimized performance"""
    pipeline = None
    begin = 0

    def start_requests(self):
        self.pipeline = self._item_buffer._pipelines[0]
        group_template = GroupItem()
        groups = self.pipeline.load_items(group_template)

        request_dict = {}
        if not (hasattr(self, 'ads_id') and self.ads_ids):
            self.ads_ids = tools.get_ads_id()

        # Optimized: Use more accounts simultaneously for faster collection
        max_groups_per_account = int(self.config.groups_nums) if hasattr(self.config, 'groups_nums') else 5

        for ads_id in self.ads_ids:
            try:
                if ads_id not in request_dict:
                    request_dict[ads_id] = []

                i = len(request_dict[ads_id])
                while i < max_groups_per_account:
                    item = next(groups)
                    self.begin += 1
                    dictobj = json.loads(item)
                    group: GroupItem = self.pipeline.dictToObj(dictobj, group_template)

                    # Skip if already collected
                    if os.path.exists(self.config.members_table + tools.make_safe_filename(group.group_name) + '.txt'):
                        continue

                    if group.status == 'apply-join':
                        if group.ads_id not in request_dict:
                            request_dict[group.ads_id] = []
                        group.priority = len(request_dict[group.ads_id]) * 10
                        request_dict[group.ads_id].append(group)
                    else:
                        group.priority = (i + 1) * 10
                        request_dict[ads_id].append(group)

                    i += 1
            except StopIteration:
                break

        count = 0
        while request_dict:
            ads_id, groups_list = request_dict.popitem()
            for group in groups_list:
                count += 1
                url = group.group_link + '/members'
                log.info(f'正在采集群组成员: {group.group_name} -> {url}')

                yield autoads.Request(
                    url=url,
                    ads_id=ads_id if group.status == 'apply-join' else ads_id,
                    index=0,
                    priority=group.priority,
                    group=group,
                    driver_count=len(self.ads_ids),
                    stop_event=self.stop_event
                )

        tools.send_message_to_ui(self.ms, self.ui, f'共{count}个群组待采集成员')

    def parse(self, request, response):
        browser = response.browser
        if not browser:
            return

        current_url = browser.current_url
        group: GroupItem = request.group

        # Check for account issues
        if 'facebook.com/login' in current_url or 'checkpoint' in current_url:
            ads_api.remove_expired_ads(request.ads_id)
            request.webdriver_pool.remove(request.ads_id)
            return

        # Determine xpath based on group status
        if group.status == 'public':
            xpath_list = self.config.members_xpath_public_user
        elif group.status == 'apply-join':
            xpath_list = self.config.members_xpath_apply_join_user
        else:
            xpath_list = self.config.members_xpath_public_user

        member_elements = tools.get_page_data_mutilxpath(browser, xpath_list)
        items_count = len(member_elements)
        member_elements = member_elements[request.index:]

        member_table = self.config.members_table + tools.make_safe_filename(group.group_name) + '.txt'

        for element in member_elements:
            try:
                member_item = MemberItem()
                member_item.__table_name__ = member_table
                member_item.group_name = group.group_name
                member_item.group_link = group.group_link
                member_item.member_name = element.get_attribute('aria-label') or element.text
                temp_link = element.get_attribute('href')
                member_item.member_link = temp_link[:temp_link.rfind('?')] if '?' in temp_link else temp_link
                member_item.ads_id = request.ads_id
                member_item.create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                yield member_item
            except Exception as e:
                log.error(f"Error extracting member: {e}")
                continue

        if items_count - request.index > 0:
            tools.send_message_to_ui(
                self.ms, self.ui,
                f'群组 [{group.group_name}] 采集到[新{items_count-request.index}/总{items_count}]个成员'
            )

        request.index = items_count
        is_finished = Action(browser).scroll_until_loaded()
        request.request_sync = True

        if is_finished:
            tools.send_message_to_ui(self.ms, self.ui, f'群组 [{group.group_name}] 成员采集完成')
            request.index = -1
            yield request
        else:
            yield request

