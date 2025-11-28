# -*- coding: utf-8 -*-
"""
FB Auto Add Friend - Automatically add friends (8 variations)
"""
import autoads
from autoads.log import log
from autoads import tools
from autoads.config import config
from autoads.automation_actions import AutomationActions
from autoads import ads_api
import random


class AutoAddFriendSpider(autoads.AirSpider):
    """Automatically add friends with 8 different methods"""
    
    def start_requests(self):
        if not self.ads_ids:
            self.ads_ids = tools.get_ads_id(self.config.account_nums)
        
        add_friend_mode = getattr(config, 'add_friend_mode', 'random')  # random, friends_of_friends, own_friends, location, app_users, group_members, friend_requests, single
        add_friend_count = getattr(config, 'add_friend_count', 10)
        add_friend_interval = getattr(config, 'add_friend_interval', 5)
        add_friend_location = getattr(config, 'add_friend_location', '')
        add_friend_single_url = getattr(config, 'add_friend_single_url', '')
        
        tools.send_message_to_ui(self.ms, self.ui, 
                                 f"开始自动添加好友: 模式={add_friend_mode}, 数量={add_friend_count}")
        
        i = 0
        priority = 10
        
        if add_friend_mode == 'random':
            # Add random friends
            url = "https://www.facebook.com/friends/requests"
            for j in range(add_friend_count):
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
                    add_friend_mode=add_friend_mode,
                    add_friend_interval=add_friend_interval,
                    driver_count=len(self.ads_ids),
                    stop_event=self.stop_event
                )
        
        elif add_friend_mode == 'friends_of_friends':
            # Add friends of friends
            url = "https://www.facebook.com/friends"
            for j in range(add_friend_count):
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
                    add_friend_mode=add_friend_mode,
                    add_friend_interval=add_friend_interval,
                    driver_count=len(self.ads_ids),
                    stop_event=self.stop_event
                )
        
        elif add_friend_mode == 'location':
            # Add location-based friends
            if add_friend_location:
                url = f"https://www.facebook.com/search/people/?q={add_friend_location}"
                for j in range(add_friend_count):
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
                        add_friend_mode=add_friend_mode,
                        location=add_friend_location,
                        add_friend_interval=add_friend_interval,
                        driver_count=len(self.ads_ids),
                        stop_event=self.stop_event
                    )
        
        elif add_friend_mode == 'group_members':
            # Add group members as friends
            from autoads.items.group_item import GroupItem
            from autoads.pipelines.file_pipeline import FilePipeline
            
            pipeline = FilePipeline()
            group_template = GroupItem()
            groups = pipeline.load_items(group_template)
            
            for group_data in groups:
                try:
                    group = pipeline.dictToObj(group_data, group_template)
                    if group.group_link:
                        url = f"{group.group_link}/members"
                        for j in range(min(add_friend_count, 5)):
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
                                add_friend_mode=add_friend_mode,
                                add_friend_interval=add_friend_interval,
                                driver_count=len(self.ads_ids),
                                stop_event=self.stop_event
                            )
                except StopIteration:
                    break
        
        elif add_friend_mode == 'single':
            # Add single friend by URL
            if add_friend_single_url:
                for j in range(add_friend_count):
                    if i == len(self.ads_ids):
                        i = 0
                        priority += 10
                    
                    ads_id = self.ads_ids[i]
                    i += 1
                    
                    yield autoads.Request(
                        url=add_friend_single_url,
                        ads_id=ads_id,
                        index=j,
                        priority=priority + j,
                        add_friend_mode=add_friend_mode,
                        add_friend_interval=add_friend_interval,
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
        
        add_friend_interval = getattr(request, 'add_friend_interval', 5)
        add_friend_mode = getattr(request, 'add_friend_mode', 'random')
        
        try:
            if add_friend_mode == 'single':
                # Direct add friend for single URL
                if AutomationActions.add_friend(browser):
                    tools.send_message_to_ui(self.ms, self.ui, "好友请求发送成功")
                else:
                    tools.send_message_to_ui(self.ms, self.ui, "好友请求发送失败")
            else:
                # Find user/profile links
                user_xpaths = [
                    "//div[@role='article']//a[contains(@href, '/profile.php') or contains(@href, '/people/')]",
                    "//a[contains(@href, '/profile.php') or contains(@href, '/people/')]"
                ]
                
                user_links = tools.get_page_data_mutilxpath(browser, user_xpaths)
                
                if not user_links:
                    tools.send_message_to_ui(self.ms, self.ui, 
                                            f"未找到用户，等待页面加载...")
                    tools.delay_time(3)
                    user_links = tools.get_page_data_mutilxpath(browser, user_xpaths)
                
                added_count = 0
                for user_link in user_links[:5]:  # Add up to 5 friends per page
                    if self.stop_event and self.stop_event.is_set():
                        break
                    
                    try:
                        user_url = user_link.get_attribute('href')
                        if user_url and 'facebook.com' in user_url:
                            # Navigate to user profile
                            browser.get(user_url)
                            tools.delay_time(2)
                            
                            # Add friend
                            if AutomationActions.add_friend(browser):
                                added_count += 1
                                tools.send_message_to_ui(self.ms, self.ui, 
                                                        f"好友请求发送成功 ({added_count})")
                                tools.delay_time(random.uniform(add_friend_interval, add_friend_interval * 1.5))
                            else:
                                log.warning("Failed to add friend")
                            
                            # Go back
                            browser.back()
                            tools.delay_time(1)
                    except Exception as e:
                        log.error(f"Error adding friend: {e}")
                        continue
                
                if added_count > 0:
                    tools.send_message_to_ui(self.ms, self.ui, 
                                            f"本页添加好友完成: {added_count} 个")
            
            # Scroll to load more users
            browser.execute_script("window.scrollBy(0, 500);")
            tools.delay_time(2)
            
        except Exception as e:
            log.error(f"Error in auto-add-friend: {e}")
            tools.send_message_to_ui(self.ms, self.ui, f"添加好友出错: {str(e)}")

