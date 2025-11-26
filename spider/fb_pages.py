# -*- coding: utf-8 -*-
"""
FB Public Page Collection - Collect Facebook public pages
"""
import autoads
from autoads.items.page_item import PageItem
from autoads.log import log
from autoads.action_control import Action
from datetime import datetime
from autoads import tools
from autoads.config import config
import os
from autoads import ads_api


class PagesSpider(autoads.AirSpider):
    """Collect Facebook public pages"""

    def start_requests(self):
        if not self.ads_ids:
            self.ads_ids = tools.get_ads_id(self.config.account_nums)

        # Get page keywords or URLs from config
        page_keywords = getattr(config, 'page_keywords', [])
        page_urls = getattr(config, 'page_urls', [])

        if not page_keywords and not page_urls:
            tools.send_message_to_ui(self.ms, self.ui, "请先输入页面关键词或URL")
            return

        tools.send_message_to_ui(self.ms, self.ui, f"正在采集公共主页")

        i = 0
        priority = 10

        # Process keywords
        for keyword in page_keywords:
            if i == len(self.ads_ids):
                i = 0
                priority += 10

            ads_id = self.ads_ids[i]
            i += 1
            url = f"https://www.facebook.com/search/pages/?q={keyword}"
            log.info(f'搜索公共主页: {url}')

            yield autoads.Request(
                url=url,
                ads_id=ads_id,
                index=0,
                priority=priority,
                keyword=keyword,
                driver_count=len(self.ads_ids),
                stop_event=self.stop_event
            )

        # Process direct URLs
        for page_url in page_urls:
            if i == len(self.ads_ids):
                i = 0
                priority += 10

            ads_id = self.ads_ids[i]
            i += 1
            log.info(f'采集公共主页: {page_url}')

            yield autoads.Request(
                url=page_url,
                ads_id=ads_id,
                index=0,
                priority=priority,
                page_url=page_url,
                driver_count=len(self.ads_ids),
                stop_event=self.stop_event
            )

    def parse(self, request, response):
        browser = response.browser
        if not browser:
            return

        current_url = browser.current_url

        # Check for account issues
        if 'facebook.com/login' in current_url or 'checkpoint' in current_url:
            ads_api.remove_expired_ads(request.ads_id)
            request.webdriver_pool.remove(request.ads_id)
            return

        # XPath for pages (may need adjustment)
        page_xpath = [
            "//div[@role='article']//a[contains(@href, '/pages/')]",
            "//a[contains(@href, '/pages/') and @role='link']"
        ]

        page_elements = tools.get_page_data_mutilxpath(browser, page_xpath)
        items_count = len(page_elements)
        page_elements = page_elements[request.index:]

        page_table = "./fb/page/pages.txt"

        for element in page_elements:
            try:
                page_item = PageItem()
                page_item.__table_name__ = page_table
                
                page_item.page_name = element.get_attribute('aria-label') or element.text
                temp_link = element.get_attribute('href')
                page_item.page_link = temp_link[:temp_link.rfind('?')] if '?' in temp_link else temp_link
                page_item.page_id = page_item.page_link.split('/')[-1] if page_item.page_link else None
                
                page_item.ads_id = request.ads_id
                page_item.create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                page_item.status = 'collected'
                yield page_item
            except Exception as e:
                log.error(f"Error extracting page: {e}")
                continue

        if items_count - request.index > 0:
            tools.send_message_to_ui(
                self.ms, self.ui,
                f'采集到[新{items_count-request.index}/总{items_count}]个公共主页'
            )

        request.index = items_count
        is_finished = Action(browser).scroll_until_loaded()
        request.request_sync = True

        if is_finished:
            tools.send_message_to_ui(self.ms, self.ui, '公共主页采集完成')
            request.index = -1
            yield request
        else:
            yield request

