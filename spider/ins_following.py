# -*- coding: utf-8 -*-
"""
Instagram User Following Collection
"""
import autoads
from autoads.items.ins_user_item import InstagramFollowingItem
from autoads.log import log
from autoads.action_control import Action
from datetime import datetime
from autoads import tools
from autoads.config import config
import os
from autoads import ads_api


class InstagramFollowingSpider(autoads.AirSpider):
    """Collect Instagram user following"""

    def start_requests(self):
        if not self.ads_ids:
            self.ads_ids = tools.get_ads_id(self.config.account_nums)

        target_users = getattr(config, 'ins_target_users', [])
        
        if not target_users:
            tools.send_message_to_ui(self.ms, self.ui, "请先输入Instagram用户名")
            return

        tools.send_message_to_ui(self.ms, self.ui, f"正在采集 {len(target_users)} 个用户的关注")

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
            url = f"https://www.instagram.com/{username}/following/"
            log.info(f'采集关注: {url}')

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

        if 'instagram.com/accounts/login' in current_url or 'challenge' in current_url:
            ads_api.remove_expired_ads(request.ads_id)
            request.webdriver_pool.remove(request.ads_id)
            return

        following_xpath = [
            "//div[@role='dialog']//a[contains(@href, '/')]",
            "//div[contains(@class, 'x1i10hfl')]//a[contains(@href, '/')]"
        ]

        try:
            following_elements = tools.get_page_data_mutilxpath(browser, following_xpath)
            items_count = len(following_elements)
            following_elements = following_elements[request.index:]

            following_table = f"./ins/following/{tools.make_safe_filename(target_user)}.txt"

            for element in following_elements:
                try:
                    following_item = InstagramFollowingItem()
                    following_item.__table_name__ = following_table
                    following_item.target_user = target_user
                    following_item.target_user_link = f"https://www.instagram.com/{target_user}/"
                    
                    temp_link = element.get_attribute('href')
                    if temp_link and '/p/' not in temp_link and '/reel/' not in temp_link:
                        following_item.following_link = temp_link
                        following_item.following_username = temp_link.rstrip('/').split('/')[-1]
                        following_item.following_full_name = element.get_attribute('title') or element.text or ""
                        
                        following_item.ads_id = request.ads_id
                        following_item.create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        following_item.status = 'collected'
                        yield following_item
                except Exception as e:
                    log.error(f"Error extracting following: {e}")
                    continue

            if items_count - request.index > 0:
                tools.send_message_to_ui(
                    self.ms, self.ui,
                    f'用户 [{target_user}] 采集到[新{items_count-request.index}/总{items_count}]个关注'
                )

            request.index = items_count
            is_finished = Action(browser).scroll_until_loaded()
            request.request_sync = True

            if is_finished:
                tools.send_message_to_ui(self.ms, self.ui, f'用户 [{target_user}] 关注采集完成')
                request.index = -1
                yield request
            else:
                yield request
        except Exception as e:
            log.error(f"Error parsing following: {e}")
            tools.send_message_to_ui(self.ms, self.ui, f'用户 [{target_user}] 关注采集出错: {str(e)}')

