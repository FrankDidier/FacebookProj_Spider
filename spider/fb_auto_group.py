# -*- coding: utf-8 -*-
"""
FB Auto Group - Automatically join groups and post to groups
"""
import autoads
from autoads.log import log
from autoads import tools
from autoads.config import config
from autoads.automation_actions import AutomationActions
from autoads import ads_api
import random


class AutoGroupSpider(autoads.AirSpider):
    """Automatically join groups and post to groups"""
    
    def start_requests(self):
        if not self.ads_ids:
            self.ads_ids = tools.get_ads_id(self.config.account_nums)
        
        group_action = getattr(config, 'group_action', 'join')  # join, post
        group_keywords = getattr(config, 'group_keywords', [])
        group_join_count = getattr(config, 'group_join_count', 5)
        group_post_content = getattr(config, 'group_post_content', [])
        group_post_images = getattr(config, 'group_post_images', [])
        group_post_interval = getattr(config, 'group_post_interval', 30)
        group_post_public = getattr(config, 'group_post_public', False)
        
        tools.send_message_to_ui(self.ms, self.ui, 
                                 f"开始群组自动化: 操作={group_action}")
        
        i = 0
        priority = 10
        
        if group_action == 'join':
            # Auto-join groups based on keywords
            for keyword in group_keywords:
                url = f"https://www.facebook.com/search/groups/?q={keyword}"
                for j in range(min(group_join_count, 3)):
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
                        group_action=group_action,
                        keyword=keyword,
                        driver_count=len(self.ads_ids),
                        stop_event=self.stop_event
                    )
        
        elif group_action == 'post':
            # Post to groups
            from autoads.items.group_item import GroupItem
            from autoads.pipelines.file_pipeline import FilePipeline
            
            pipeline = FilePipeline()
            group_template = GroupItem()
            groups = pipeline.load_items(group_template)
            
            for group_data in groups:
                try:
                    group = pipeline.dictToObj(group_data, group_template)
                    if group.group_link:
                        if i == len(self.ads_ids):
                            i = 0
                            priority += 10
                        
                        ads_id = self.ads_ids[i]
                        i += 1
                        
                        yield autoads.Request(
                            url=group.group_link,
                            ads_id=ads_id,
                            index=0,
                            priority=priority,
                            group_action=group_action,
                            group=group,
                            post_content=group_post_content,
                            post_images=group_post_images,
                            post_interval=group_post_interval,
                            post_public=group_post_public,
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
        
        group_action = getattr(request, 'group_action', 'join')
        
        try:
            if group_action == 'join':
                # Find groups on page
                group_xpaths = [
                    "//div[@role='feed']//a[@role='link' and contains(@href, '/groups/')]",
                    "//a[contains(@href, '/groups/') and @role='link']"
                ]
                
                group_links = tools.get_page_data_mutilxpath(browser, group_xpaths)
                
                if not group_links:
                    tools.send_message_to_ui(self.ms, self.ui, 
                                            f"未找到群组，等待页面加载...")
                    tools.delay_time(3)
                    group_links = tools.get_page_data_mutilxpath(browser, group_xpaths)
                
                joined_count = 0
                for group_link in group_links[:3]:  # Join up to 3 groups per page
                    if self.stop_event and self.stop_event.is_set():
                        break
                    
                    try:
                        group_url = group_link.get_attribute('href')
                        if group_url and 'facebook.com/groups' in group_url:
                            # Join the group
                            if AutomationActions.join_group(browser, group_url):
                                joined_count += 1
                                tools.send_message_to_ui(self.ms, self.ui, 
                                                        f"加入群组成功 ({joined_count})")
                                tools.delay_time(random.uniform(5, 10))
                            else:
                                log.warning("Failed to join group")
                    except Exception as e:
                        log.error(f"Error joining group: {e}")
                        continue
                
                if joined_count > 0:
                    tools.send_message_to_ui(self.ms, self.ui, 
                                            f"本页加入群组完成: {joined_count} 个")
            
            elif group_action == 'post':
                # Post to group
                group = getattr(request, 'group', None)
                post_content = getattr(request, 'post_content', [])
                post_images = getattr(request, 'post_images', [])
                post_public = getattr(request, 'post_public', False)
                
                if not post_content:
                    post_content = ["Hello everyone!", "Great group!"]
                
                content = random.choice(post_content)
                group_url = group.group_link if group else browser.current_url
                
                if AutomationActions.post_to_group(browser, group_url, content, post_images):
                    tools.send_message_to_ui(self.ms, self.ui, 
                                            f"群组发帖成功: {content[:30]}...")
                else:
                    tools.send_message_to_ui(self.ms, self.ui, "群组发帖失败")
            
        except Exception as e:
            log.error(f"Error in auto-group: {e}")
            tools.send_message_to_ui(self.ms, self.ui, f"群组操作出错: {str(e)}")

