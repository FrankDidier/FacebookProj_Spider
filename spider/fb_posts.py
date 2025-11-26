# -*- coding: utf-8 -*-
"""
FB Group Post Collection - Collect posts from Facebook groups
"""
import autoads
from autoads.items.post_item import PostItem
from autoads.items.group_item import GroupItem
from autoads.log import log
from autoads.action_control import Action
from datetime import datetime
from autoads import tools
from autoads.config import config
config.name = 'config.ini'  # Ensure config is initialized
import json
import os
from autoads import ads_api
import threading


class PostsSpider(autoads.AirSpider):
    """Collect posts from Facebook groups"""
    pipeline = None

    def start_requests(self):
        self.pipeline = self._item_buffer._pipelines[0]
        group_template = GroupItem()
        groups = self.pipeline.load_items(group_template)

        if not self.ads_ids:
            self.ads_ids = tools.get_ads_id()

        request_dict = {}
        max_groups = int(getattr(config, 'post_groups_nums', 10))

        for ads_id in self.ads_ids:
            try:
                if ads_id not in request_dict:
                    request_dict[ads_id] = []

                i = len(request_dict[ads_id])
                while i < max_groups:
                    item = next(groups)
                    dictobj = json.loads(item)
                    group: GroupItem = self.pipeline.dictToObj(dictobj, group_template)

                    # Skip if already collected
                    post_file = f"./fb/post/{tools.make_safe_filename(group.group_name)}.txt"
                    if os.path.exists(post_file):
                        continue

                    if group.status == 'apply-join' and group.ads_id:
                        if group.ads_id not in request_dict:
                            request_dict[group.ads_id] = []
                        request_dict[group.ads_id].append(group)
                    else:
                        request_dict[ads_id].append(group)

                    i += 1
            except StopIteration:
                break

        count = 0
        for ads_id, groups_list in request_dict.items():
            for group in groups_list:
                count += 1
                url = group.group_link
                log.info(f'正在采集群组帖子: {group.group_name} -> {url}')

                yield autoads.Request(
                    url=url,
                    ads_id=ads_id if group.status != 'apply-join' else group.ads_id,
                    index=0,
                    priority=count * 10,
                    group=group,
                    driver_count=len(self.ads_ids),
                    stop_event=self.stop_event
                )

        tools.send_message_to_ui(self.ms, self.ui, f'共{count}个群组待采集帖子')

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

        # XPath for posts (this may need adjustment based on Facebook's current structure)
        post_xpath = [
            "//div[@role='article']",
            "//div[contains(@class, 'userContentWrapper')]"
        ]

        try:
            post_elements = tools.get_page_data_mutilxpath(browser, post_xpath)
            items_count = len(post_elements)
            post_elements = post_elements[request.index:]

            post_table = f"./fb/post/{tools.make_safe_filename(group.group_name)}.txt"

            for element in post_elements:
                try:
                    post_item = PostItem()
                    post_item.__table_name__ = post_table
                    post_item.group_name = group.group_name
                    post_item.group_link = group.group_link
                    
                    # Extract post data (these selectors may need adjustment)
                    from selenium.webdriver.common.by import By
                    try:
                        post_item.post_content = element.find_element(By.XPATH, ".//div[@data-testid='post_message']").text
                    except:
                        post_item.post_content = element.text[:500] if element.text else ""
                    
                    try:
                        link_elem = element.find_element(By.XPATH, ".//a[contains(@href, '/posts/') or contains(@href, '/permalink/')]")
                        post_item.post_link = link_elem.get_attribute('href')
                        post_item.post_id = post_item.post_link.split('/')[-1] if post_item.post_link else None
                    except:
                        post_item.post_link = None
                        post_item.post_id = None

                    post_item.ads_id = request.ads_id
                    post_item.create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    post_item.status = 'collected'
                    yield post_item
                except Exception as e:
                    log.error(f"Error extracting post: {e}")
                    continue

            if items_count - request.index > 0:
                tools.send_message_to_ui(
                    self.ms, self.ui,
                    f'群组 [{group.group_name}] 采集到[新{items_count-request.index}/总{items_count}]个帖子'
                )

            request.index = items_count
            is_finished = Action(browser).scroll_until_loaded()
            request.request_sync = True

            if is_finished:
                tools.send_message_to_ui(self.ms, self.ui, f'群组 [{group.group_name}] 帖子采集完成')
                request.index = -1
                yield request
            else:
                yield request
        except Exception as e:
            log.error(f"Error parsing posts: {e}")
            tools.send_message_to_ui(self.ms, self.ui, f'群组 [{group.group_name}] 帖子采集出错: {str(e)}')

