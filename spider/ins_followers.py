# -*- coding: utf-8 -*-
"""
Instagram User Follower Collection
"""
import autoads
from autoads.items.ins_user_item import InstagramFollowerItem
from autoads.log import log
from autoads.action_control import Action
from datetime import datetime
from autoads import tools
from autoads.config import config
import os
from autoads import ads_api


class InstagramFollowersSpider(autoads.AirSpider):
    """Collect Instagram user followers"""

    def start_requests(self):
        if not self.ads_ids:
            self.ads_ids = tools.get_ads_id(self.config.account_nums)

        # Get target users from config
        target_users = getattr(config, 'ins_target_users', [])
        
        if not target_users:
            tools.send_message_to_ui(self.ms, self.ui, "请先输入Instagram用户名")
            return

        tools.send_message_to_ui(self.ms, self.ui, f"正在采集 {len(target_users)} 个用户的粉丝")

        i = 0
        priority = 10

        for username in target_users:
            username = username.strip().replace('@', '')
            if not username:
                continue

            if i == len(self.ads_ids):
                i = 0
                priority += 10

            ads_id = self.ads_ids[i]
            i += 1
            url = f"https://www.instagram.com/{username}/followers/"
            log.info(f'采集粉丝: {url}')

            yield autoads.Request(
                url=url,
                ads_id=ads_id,
                index=0,
                priority=priority,
                target_user=username,
                driver_count=len(self.ads_ids),
                stop_event=self.stop_event
            )

    def parse(self, request, response):
        browser = response.browser
        if not browser:
            return

        current_url = browser.current_url
        target_user = request.target_user

        # Check for account issues
        if 'instagram.com/accounts/login' in current_url or 'challenge' in current_url:
            ads_api.remove_expired_ads(request.ads_id)
            request.webdriver_pool.remove(request.ads_id)
            return

        # Instagram follower XPath (may need adjustment based on current Instagram structure)
        follower_xpath = [
            "//div[@role='dialog']//a[contains(@href, '/')]",
            "//div[contains(@class, 'x1i10hfl')]//a[contains(@href, '/')]"
        ]

        try:
            follower_elements = tools.get_page_data_mutilxpath(browser, follower_xpath)
            items_count = len(follower_elements)
            follower_elements = follower_elements[request.index:]

            follower_table = f"./ins/follower/{tools.make_safe_filename(target_user)}.txt"

            for element in follower_elements:
                try:
                    follower_item = InstagramFollowerItem()
                    follower_item.__table_name__ = follower_table
                    follower_item.target_user = target_user
                    follower_item.target_user_link = f"https://www.instagram.com/{target_user}/"
                    
                    temp_link = element.get_attribute('href')
                    if temp_link and '/p/' not in temp_link and '/reel/' not in temp_link:
                        follower_item.follower_link = temp_link
                        follower_item.follower_username = temp_link.rstrip('/').split('/')[-1]
                        follower_item.follower_full_name = element.get_attribute('title') or element.text or ""
                        
                        follower_item.ads_id = request.ads_id
                        follower_item.create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        follower_item.status = 'collected'
                        yield follower_item
                except Exception as e:
                    log.error(f"Error extracting follower: {e}")
                    continue

            if items_count - request.index > 0:
                tools.send_message_to_ui(
                    self.ms, self.ui,
                    f'用户 [{target_user}] 采集到[新{items_count-request.index}/总{items_count}]个粉丝'
                )

            request.index = items_count
            is_finished = Action(browser).scroll_until_loaded()
            request.request_sync = True

            if is_finished:
                tools.send_message_to_ui(self.ms, self.ui, f'用户 [{target_user}] 粉丝采集完成')
                request.index = -1
                yield request
            else:
                yield request
        except Exception as e:
            log.error(f"Error parsing followers: {e}")
            tools.send_message_to_ui(self.ms, self.ui, f'用户 [{target_user}] 粉丝采集出错: {str(e)}')

