# -*- coding: utf-8 -*-
"""
Instagram User Profile Collection
"""
import autoads
from autoads.items.ins_user_item import InstagramUserItem
from autoads.log import log
from datetime import datetime
from autoads import tools
from autoads.config import config
import os
from autoads import ads_api
import re


class InstagramProfileSpider(autoads.AirSpider):
    """Collect Instagram user profiles"""

    def start_requests(self):
        if not self.ads_ids:
            self.ads_ids = tools.get_ads_id(self.config.account_nums)

        target_users = getattr(config, 'ins_target_users', [])
        
        if not target_users:
            tools.send_message_to_ui(self.ms, self.ui, "请先输入Instagram用户名")
            return

        tools.send_message_to_ui(self.ms, self.ui, f"正在采集 {len(target_users)} 个用户的简介")

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
            url = f"https://www.instagram.com/{username}/"
            log.info(f'采集用户简介: {url}')

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

        try:
            # Wait for page to load
            import time
            time.sleep(2)

            # Extract profile data
            user_item = InstagramUserItem()
            user_item.__table_name__ = "./ins/user/profiles.txt"
            user_item.username = target_user
            user_item.user_link = f"https://www.instagram.com/{target_user}/"

            # Extract profile information (these selectors may need adjustment)
            try:
                page_text = browser.page_source
                
                # Extract full name
                full_name_match = re.search(r'"full_name":"([^"]+)"', page_text)
                if full_name_match:
                    user_item.full_name = full_name_match.group(1)

                # Extract bio
                bio_match = re.search(r'"biography":"([^"]+)"', page_text)
                if bio_match:
                    user_item.bio = bio_match.group(1)

                # Extract follower count
                followers_match = re.search(r'"edge_followed_by":{"count":(\d+)}', page_text)
                if followers_match:
                    user_item.followers_count = int(followers_match.group(1))

                # Extract following count
                following_match = re.search(r'"edge_follow":{"count":(\d+)}', page_text)
                if following_match:
                    user_item.following_count = int(following_match.group(1))

                # Extract posts count
                posts_match = re.search(r'"edge_owner_to_timeline_media":{"count":(\d+)}', page_text)
                if posts_match:
                    user_item.posts_count = int(posts_match.group(1))

                # Check if verified
                user_item.is_verified = '"is_verified":true' in page_text

                # Check if private
                user_item.is_private = '"is_private":true' in page_text

                # Extract profile pic
                pic_match = re.search(r'"profile_pic_url":"([^"]+)"', page_text)
                if pic_match:
                    user_item.profile_pic_url = pic_match.group(1)

            except Exception as e:
                log.error(f"Error extracting profile data: {e}")

            user_item.ads_id = request.ads_id
            user_item.create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            user_item.status = 'collected'
            yield user_item

            tools.send_message_to_ui(
                self.ms, self.ui,
                f'用户 [{target_user}] 简介采集完成'
            )

        except Exception as e:
            log.error(f"Error parsing profile: {e}")
            tools.send_message_to_ui(self.ms, self.ui, f'用户 [{target_user}] 简介采集出错: {str(e)}')

