# -*- coding: utf-8 -*-
"""
FB Auto Comment - Automatically comment on posts
"""
import autoads
from autoads.log import log
from autoads import tools
from autoads.config import config
from autoads.automation_actions import AutomationActions
from autoads import ads_api
import random
import threading


class AutoCommentSpider(autoads.AirSpider):
    """Automatically comment on Facebook posts"""
    
    def start_requests(self):
        if not self.ads_ids:
            self.ads_ids = tools.get_ads_id(self.config.account_nums)
        
        comment_mode = getattr(config, 'comment_mode', 'keywords')  # keywords, group, all
        comment_keywords = getattr(config, 'comment_keywords', [])
        comment_content = getattr(config, 'comment_content', [])
        comment_count = getattr(config, 'comment_count', 5)
        comment_interval = getattr(config, 'comment_interval', 10)
        
        if not comment_content:
            comment_content = ["Nice post!", "Great content!", "Thanks for sharing!"]
        
        tools.send_message_to_ui(self.ms, self.ui, 
                                 f"开始自动评论: 模式={comment_mode}, 数量={comment_count}")
        
        i = 0
        priority = 10
        
        if comment_mode == 'keywords':
            # Comment on posts with specific keywords
            for keyword in comment_keywords:
                url = f"https://www.facebook.com/search/posts/?q={keyword}"
                for j in range(min(comment_count, 3)):
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
                        comment_mode=comment_mode,
                        keyword=keyword,
                        comment_content=comment_content,
                        comment_interval=comment_interval,
                        driver_count=len(self.ads_ids),
                        stop_event=self.stop_event
                    )
        
        elif comment_mode == 'group':
            # Comment on posts in groups
            from autoads.items.group_item import GroupItem
            from autoads.pipelines.file_pipeline import FilePipeline
            
            pipeline = FilePipeline()
            group_template = GroupItem()
            groups = pipeline.load_items(group_template)
            
            for group_data in groups:
                try:
                    group = pipeline.dictToObj(group_data, group_template)
                    if group.group_link:
                        for j in range(min(comment_count, 2)):
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
                                comment_mode=comment_mode,
                                comment_content=comment_content,
                                comment_interval=comment_interval,
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
        
        comment_content = getattr(request, 'comment_content', ["Nice post!"])
        comment_interval = getattr(request, 'comment_interval', 10)
        
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
            
            commented_count = 0
            for post in posts[:3]:  # Comment on up to 3 posts per page
                if self.stop_event and self.stop_event.is_set():
                    break
                
                # Check if already commented (optional - can skip this check)
                # Select random comment from list
                comment_text = random.choice(comment_content)
                
                # Comment on the post
                if AutomationActions.comment_on_post(browser, comment_text, post_element=post):
                    commented_count += 1
                    tools.send_message_to_ui(self.ms, self.ui, 
                                            f"评论成功 ({commented_count}): {comment_text[:30]}...")
                    tools.delay_time(random.uniform(comment_interval, comment_interval * 1.5))
                else:
                    log.warning("Failed to comment on post")
            
            if commented_count > 0:
                tools.send_message_to_ui(self.ms, self.ui, 
                                        f"本页评论完成: {commented_count} 个帖子")
            
            # Scroll to load more posts
            browser.execute_script("window.scrollBy(0, 500);")
            tools.delay_time(2)
            
        except Exception as e:
            log.error(f"Error in auto-comment: {e}")
            tools.send_message_to_ui(self.ms, self.ui, f"评论出错: {str(e)}")

