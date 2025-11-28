# -*- coding: utf-8 -*-
"""
FB Auto Follow - Automatically follow users/pages
"""
import autoads
from autoads.log import log
from autoads import tools
from autoads.config import config
from autoads.automation_actions import AutomationActions
from autoads import ads_api
import random


class AutoFollowSpider(autoads.AirSpider):
    """Automatically follow Facebook users/pages"""
    
    def start_requests(self):
        if not self.ads_ids:
            self.ads_ids = tools.get_ads_id(self.config.account_nums)
        
        follow_mode = getattr(config, 'follow_mode', 'fans')  # fans, recommended, search
        follow_count = getattr(config, 'follow_count', 10)
        follow_interval = getattr(config, 'follow_interval', 5)
        follow_keywords = getattr(config, 'follow_keywords', [])
        
        tools.send_message_to_ui(self.ms, self.ui, 
                                 f"开始自动关注: 模式={follow_mode}, 数量={follow_count}")
        
        i = 0
        priority = 10
        
        if follow_mode == 'fans':
            # Follow fans/followers
            url = "https://www.facebook.com/friends"
            for j in range(follow_count):
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
                    follow_mode=follow_mode,
                    follow_interval=follow_interval,
                    driver_count=len(self.ads_ids),
                    stop_event=self.stop_event
                )
        
        elif follow_mode == 'recommended':
            # Follow recommended friends
            url = "https://www.facebook.com/friends/requests"
            for j in range(follow_count):
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
                    follow_mode=follow_mode,
                    follow_interval=follow_interval,
                    driver_count=len(self.ads_ids),
                    stop_event=self.stop_event
                )
        
        elif follow_mode == 'search':
            # Follow users from search
            for keyword in follow_keywords:
                url = f"https://www.facebook.com/search/people/?q={keyword}"
                for j in range(min(follow_count, 5)):
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
                        follow_mode=follow_mode,
                        keyword=keyword,
                        follow_interval=follow_interval,
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
        
        follow_interval = getattr(request, 'follow_interval', 5)
        follow_mode = getattr(request, 'follow_mode', 'fans')
        
        try:
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
            
            followed_count = 0
            for user_link in user_links[:5]:  # Follow up to 5 users per page
                if self.stop_event and self.stop_event.is_set():
                    break
                
                try:
                    user_url = user_link.get_attribute('href')
                    if user_url and 'facebook.com' in user_url:
                        # Navigate to user profile
                        browser.get(user_url)
                        tools.delay_time(2)
                        
                        # Follow the user
                        if AutomationActions.follow_user(browser):
                            followed_count += 1
                            tools.send_message_to_ui(self.ms, self.ui, 
                                                    f"关注成功 ({followed_count})")
                            tools.delay_time(random.uniform(follow_interval, follow_interval * 1.5))
                        else:
                            log.warning("Failed to follow user")
                        
                        # Go back
                        browser.back()
                        tools.delay_time(1)
                except Exception as e:
                    log.error(f"Error following user: {e}")
                    continue
            
            if followed_count > 0:
                tools.send_message_to_ui(self.ms, self.ui, 
                                        f"本页关注完成: {followed_count} 个用户")
            
            # Scroll to load more users
            browser.execute_script("window.scrollBy(0, 500);")
            tools.delay_time(2)
            
        except Exception as e:
            log.error(f"Error in auto-follow: {e}")
            tools.send_message_to_ui(self.ms, self.ui, f"关注出错: {str(e)}")

