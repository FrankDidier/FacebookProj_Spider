# -*- coding: utf-8 -*-
"""
FB Auto Post - Automatically post to main feed
"""
import autoads
from autoads.log import log
from autoads import tools
from autoads.config import config
from autoads.automation_actions import AutomationActions
from autoads import ads_api
import random


class AutoPostSpider(autoads.AirSpider):
    """Automatically post to Facebook main feed"""
    
    def start_requests(self):
        if not self.ads_ids:
            self.ads_ids = tools.get_ads_id(self.config.account_nums)
        
        post_content = getattr(config, 'main_post_content', [])
        post_images = getattr(config, 'main_post_images', [])
        post_count = getattr(config, 'main_post_count', 1)
        post_interval = getattr(config, 'main_post_interval', 60)
        post_public = getattr(config, 'main_post_public', True)
        
        if not post_content:
            post_content = ["Hello Facebook!", "Great day today!"]
        
        tools.send_message_to_ui(self.ms, self.ui, 
                                 f"开始自动发帖: 数量={post_count}")
        
        i = 0
        priority = 10
        
        url = "https://www.facebook.com/"
        
        for j in range(post_count):
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
                post_content=post_content,
                post_images=post_images,
                post_interval=post_interval,
                post_public=post_public,
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
        
        post_content = getattr(request, 'post_content', ["Hello!"])
        post_images = getattr(request, 'post_images', [])
        post_public = getattr(request, 'post_public', True)
        
        try:
            # Find post input box
            post_input_xpaths = [
                "//div[@role='textbox' and contains(@aria-label, 'What')]",
                "//div[@role='textbox' and contains(@aria-label, '在想什么')]",
                "//div[@contenteditable='true' and contains(@data-testid, 'post')]"
            ]
            
            post_input = None
            for xpath in post_input_xpaths:
                try:
                    inputs = browser.find_elements('xpath', xpath)
                    if inputs:
                        post_input = inputs[0]
                        break
                except:
                    continue
            
            if post_input:
                # Click to focus
                browser.execute_script("arguments[0].click();", post_input)
                tools.delay_time(1)
                
                # Select random content
                content = random.choice(post_content)
                post_input.send_keys(content)
                tools.delay_time(random.uniform(1, 2))
                
                # Set privacy if needed
                if post_public:
                    privacy_xpaths = [
                        "//div[@role='button' and contains(@aria-label, 'Public')]",
                        "//div[@role='button' and contains(@aria-label, '公开')]"
                    ]
                    for xpath in privacy_xpaths:
                        try:
                            privacy_buttons = browser.find_elements('xpath', xpath)
                            if privacy_buttons:
                                browser.execute_script("arguments[0].click();", privacy_buttons[0])
                                tools.delay_time(1)
                                break
                        except:
                            continue
                
                # Upload images if provided
                if post_images:
                    file_input_xpaths = [
                        "//input[@type='file']",
                        "//div[@role='button' and contains(@aria-label, 'Photo')]"
                    ]
                    for xpath in file_input_xpaths:
                        try:
                            file_inputs = browser.find_elements('xpath', xpath)
                            if file_inputs:
                                for img_path in post_images:
                                    file_inputs[0].send_keys(img_path)
                                    tools.delay_time(2)
                                break
                        except:
                            continue
                
                # Click post button
                post_button_xpaths = [
                    "//div[@role='button' and contains(@aria-label, 'Post')]",
                    "//div[@role='button' and contains(@aria-label, '发布')]",
                    "//span[contains(text(), 'Post')]/ancestor::div[@role='button']"
                ]
                
                for xpath in post_button_xpaths:
                    try:
                        buttons = browser.find_elements('xpath', xpath)
                        if buttons:
                            browser.execute_script("arguments[0].click();", buttons[0])
                            tools.delay_time(random.uniform(3, 5))
                            tools.send_message_to_ui(self.ms, self.ui, 
                                                    f"发帖成功: {content[:30]}...")
                            return
                    except:
                        continue
                
                log.warning("Post button not found")
            else:
                log.warning("Post input not found")
            
        except Exception as e:
            log.error(f"Error in auto-post: {e}")
            tools.send_message_to_ui(self.ms, self.ui, f"发帖出错: {str(e)}")

