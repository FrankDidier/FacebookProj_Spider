# -*- coding: utf-8 -*-
"""
FB Auto Like - Automatically like posts based on criteria
"""
import autoads
from autoads.log import log
from autoads import tools
from autoads.config import config
from autoads.automation_actions import AutomationActions
from autoads import ads_api
import random
import threading


class AutoLikeSpider(autoads.AirSpider):
    """Automatically like Facebook posts"""
    
    def start_requests(self):
        if not self.ads_ids:
            self.ads_ids = tools.get_ads_id(self.config.account_nums)
        
        like_mode = getattr(config, 'like_mode', 'all')  # all, keywords, group, search
        like_keywords = getattr(config, 'like_keywords', [])
        like_groups = getattr(config, 'like_groups', [])
        like_count = getattr(config, 'like_count', 10)
        like_interval = getattr(config, 'like_interval', 5)
        
        tools.send_message_to_ui(self.ms, self.ui, 
                                 f"开始自动点赞: 模式={like_mode}, 数量={like_count}")
        
        i = 0
        priority = 10
        
        if like_mode == 'all':
            # Like all posts on news feed
            url = "https://www.facebook.com/"
            for j in range(like_count):
                if i == len(self.ads_ids):
                    i = 0
                    priority += 10
                
                ads_id = self.ads_ids[i]
                i += 1
                
                yield autoads.Request(
                    url=url,
                    ads_id=ads_id,
                    index=j,
                    priority=priority + j,
                    like_mode=like_mode,
                    like_interval=like_interval,
                    driver_count=len(self.ads_ids),
                    stop_event=self.stop_event
                )
        
        elif like_mode == 'keywords':
            # Like posts with specific keywords
            for keyword in like_keywords:
                url = f"https://www.facebook.com/search/posts/?q={keyword}"
                for j in range(min(like_count, 5)):
                    if i == len(self.ads_ids):
                        i = 0
                        priority += 10
                    
                    ads_id = self.ads_ids[i]
                    i += 1
                    
                    yield autoads.Request(
                        url=url,
                        ads_id=ads_id,
                        index=j,
                        priority=priority + j,
                        like_mode=like_mode,
                        keyword=keyword,
                        like_interval=like_interval,
                        driver_count=len(self.ads_ids),
                        stop_event=self.stop_event
                    )
        
        elif like_mode == 'group':
            # Like posts in specific groups
            from autoads.items.group_item import GroupItem
            from autoads.pipelines.file_pipeline import FilePipeline
            
            pipeline = FilePipeline()
            group_template = GroupItem()
            groups = pipeline.load_items(group_template)
            
            for group_data in groups:
                try:
                    group = pipeline.dictToObj(group_data, group_template)
                    if group.group_link:
                        for j in range(min(like_count, 3)):
                            if i == len(self.ads_ids):
                                i = 0
                                priority += 10
                            
                            ads_id = self.ads_ids[i]
                            i += 1
                            
                            yield autoads.Request(
                                url=group.group_link,
                                ads_id=ads_id,
                                index=j,
                                priority=priority + j,
                                like_mode=like_mode,
                                like_interval=like_interval,
                                driver_count=len(self.ads_ids),
                                stop_event=self.stop_event
                            )
                except StopIteration:
                    break
    
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
        
        like_interval = getattr(request, 'like_interval', 5)
        like_mode = getattr(request, 'like_mode', 'all')
        
        try:
            # Find posts on page
            post_xpaths = [
                "//div[@role='article']",
                "//div[contains(@class, 'userContentWrapper')]"
            ]
            
            posts = tools.get_page_data_mutilxpath(browser, post_xpaths)
            
            if not posts:
                tools.send_message_to_ui(self.ms, self.ui, 
                                        f"未找到帖子，等待页面加载...")
                tools.delay_time(3)
                posts = tools.get_page_data_mutilxpath(browser, post_xpaths)
            
            liked_count = 0
            for post in posts[:5]:  # Like up to 5 posts per page
                if self.stop_event and self.stop_event.is_set():
                    break
                
                # Check if already liked
                like_indicators = post.find_elements('xpath', 
                    ".//div[@aria-pressed='true' and contains(@aria-label, 'Like')]")
                
                if not like_indicators:
                    # Like the post
                    if AutomationActions.like_post(browser, post_element=post):
                        liked_count += 1
                        tools.send_message_to_ui(self.ms, self.ui, 
                                                f"点赞成功 ({liked_count})")
                        tools.delay_time(random.uniform(like_interval, like_interval * 1.5))
                    else:
                        log.warning("Failed to like post")
                else:
                    log.info("Post already liked")
            
            if liked_count > 0:
                tools.send_message_to_ui(self.ms, self.ui, 
                                        f"本页点赞完成: {liked_count} 个帖子")
            
            # Scroll to load more posts
            browser.execute_script("window.scrollBy(0, 500);")
            tools.delay_time(2)
            
        except Exception as e:
            log.error(f"Error in auto-like: {e}")
            tools.send_message_to_ui(self.ms, self.ui, f"点赞出错: {str(e)}")

