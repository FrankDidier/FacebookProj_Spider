# -*- coding: utf-8 -*-
"""
Instagram Reels Comment Collection
"""
import autoads
from autoads.items.ins_user_item import InstagramReelsCommentItem
from autoads.log import log
from autoads.action_control import Action
from datetime import datetime
from autoads import tools
from autoads.config import config
import os
from autoads import ads_api
import re


class InstagramReelsCommentsSpider(autoads.AirSpider):
    """Collect Instagram Reels comments"""

    def start_requests(self):
        if not self.ads_ids:
            self.ads_ids = tools.get_ads_id(self.config.account_nums)

        # Get reels URLs from config
        reels_urls = getattr(config, 'ins_reels_urls', [])
        
        if not reels_urls:
            tools.send_message_to_ui(self.ms, self.ui, "请先输入Instagram Reels URL")
            return

        tools.send_message_to_ui(self.ms, self.ui, f"正在采集 {len(reels_urls)} 个Reels的评论")

        i = 0
        priority = 10

        for reels_url in reels_urls:
            reels_url = reels_url.strip()
            if not reels_url or 'instagram.com/reel/' not in reels_url:
                continue

            if i == len(self.ads_ids):
                i = 0
                priority += 10

            ads_id = self.ads_ids[i]
            i += 1
            log.info(f'采集Reels评论: {reels_url}')

            yield autoads.Request(
                url=reels_url,
                ads_id=ads_id,
                index=0,
                priority=priority,
                reels_url=reels_url,
                driver_count=len(self.ads_ids),
                stop_event=self.stop_event
            )

    def parse(self, request, response):
        browser = response.browser
        if not browser:
            return

        current_url = browser.current_url
        reels_url = request.reels_url

        if 'instagram.com/accounts/login' in current_url or 'challenge' in current_url:
            ads_api.remove_expired_ads(request.ads_id)
            request.webdriver_pool.remove(request.ads_id)
            return

        # Extract reels ID
        reels_id = reels_url.split('/reel/')[-1].split('/')[0] if '/reel/' in reels_url else None

        # Instagram comment XPath (may need adjustment)
        comment_xpath = [
            "//ul[@role='list']//li[contains(@class, 'comment')]",
            "//div[contains(@class, 'x1i10hfl')]//span[contains(@class, 'comment')]"
        ]

        try:
            comment_elements = tools.get_page_data_mutilxpath(browser, comment_xpath)
            items_count = len(comment_elements)
            comment_elements = comment_elements[request.index:]

            comment_table = f"./ins/reels_comment/{tools.make_safe_filename(reels_id or 'reels')}.txt"

            for element in comment_elements:
                try:
                    comment_item = InstagramReelsCommentItem()
                    comment_item.__table_name__ = comment_table
                    comment_item.reels_url = reels_url
                    comment_item.reels_id = reels_id
                    
                    # Extract comment data
                    try:
                        comment_item.comment_text = element.text or ""
                        comment_item.comment_id = element.get_attribute('id') or f"comment_{datetime.now().timestamp()}"
                    except:
                        comment_item.comment_text = ""
                        comment_item.comment_id = f"comment_{datetime.now().timestamp()}"

                    # Extract author
                    from selenium.webdriver.common.by import By
                    try:
                        author_elem = element.find_element(By.XPATH, ".//a[contains(@href, '/')]")
                        comment_item.comment_author_link = author_elem.get_attribute('href')
                        comment_item.comment_author = author_elem.text or comment_item.comment_author_link.split('/')[-2] if comment_item.comment_author_link else ""
                    except:
                        comment_item.comment_author = ""
                        comment_item.comment_author_link = ""

                    comment_item.ads_id = request.ads_id
                    comment_item.create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    comment_item.status = 'collected'
                    yield comment_item
                except Exception as e:
                    log.error(f"Error extracting comment: {e}")
                    continue

            if items_count - request.index > 0:
                tools.send_message_to_ui(
                    self.ms, self.ui,
                    f'Reels [{reels_id}] 采集到[新{items_count-request.index}/总{items_count}]个评论'
                )

            request.index = items_count
            is_finished = Action(browser).scroll_until_loaded()
            request.request_sync = True

            if is_finished:
                tools.send_message_to_ui(self.ms, self.ui, f'Reels [{reels_id}] 评论采集完成')
                request.index = -1
                yield request
            else:
                yield request
        except Exception as e:
            log.error(f"Error parsing comments: {e}")
            tools.send_message_to_ui(self.ms, self.ui, f'Reels [{reels_id}] 评论采集出错: {str(e)}')

