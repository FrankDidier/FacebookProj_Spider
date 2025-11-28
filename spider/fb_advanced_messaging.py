# -*- coding: utf-8 -*-
"""
FB Advanced Messaging - Advanced messaging features
"""
import autoads
from autoads.log import log
from autoads import tools
from autoads.config import config
from autoads import ads_api
import random
import os


class AdvancedMessagingSpider(autoads.AirSpider):
    """Advanced messaging features: online friends, all friends, images, anti-ban, etc."""
    
    def start_requests(self):
        if not self.ads_ids:
            self.ads_ids = tools.get_ads_id(self.config.account_nums)
        
        message_mode = getattr(config, 'message_mode', 'all_friends')  # online_friends, all_friends
        message_content = getattr(config, 'advanced_message_content', [])
        message_images = getattr(config, 'advanced_message_images', [])
        message_interval = getattr(config, 'advanced_message_interval', 5)
        message_count = getattr(config, 'advanced_message_count', 10)
        message_anti_ban = getattr(config, 'message_anti_ban', False)
        message_cloud_backup = getattr(config, 'message_cloud_backup', False)
        
        if not message_content:
            message_content = ["Hello!", "How are you?"]
        
        tools.send_message_to_ui(self.ms, self.ui, 
                                 f"开始高级私信: 模式={message_mode}, 数量={message_count}")
        
        i = 0
        priority = 10
        
        if message_mode == 'online_friends':
            url = "https://www.facebook.com/messages"
        elif message_mode == 'all_friends':
            url = "https://www.facebook.com/friends"
        else:
            url = "https://www.facebook.com/friends"
        
        for j in range(message_count):
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
                message_mode=message_mode,
                message_content=message_content,
                message_images=message_images,
                message_interval=message_interval,
                message_anti_ban=message_anti_ban,
                message_cloud_backup=message_cloud_backup,
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
        
        message_mode = getattr(request, 'message_mode', 'all_friends')
        message_content = getattr(request, 'message_content', ["Hello!"])
        message_images = getattr(request, 'message_images', [])
        message_interval = getattr(request, 'message_interval', 5)
        message_anti_ban = getattr(request, 'message_anti_ban', False)
        
        try:
            if message_mode == 'online_friends':
                # Find online friends
                online_xpaths = [
                    "//div[contains(@class, 'online')]//a[contains(@href, '/messages/t/')]",
                    "//div[@aria-label*='online' or @aria-label*='在线']//a"
                ]
                friend_links = tools.get_page_data_mutilxpath(browser, online_xpaths)
            else:
                # Find all friends
                friend_xpaths = [
                    "//div[@role='article']//a[contains(@href, '/profile.php') or contains(@href, '/people/')]",
                    "//a[contains(@href, '/profile.php') or contains(@href, '/people/')]"
                ]
                friend_links = tools.get_page_data_mutilxpath(browser, friend_xpaths)
            
            if not friend_links:
                tools.send_message_to_ui(self.ms, self.ui, 
                                        f"未找到好友，等待页面加载...")
                tools.delay_time(3)
                if message_mode == 'online_friends':
                    friend_links = tools.get_page_data_mutilxpath(browser, online_xpaths)
                else:
                    friend_links = tools.get_page_data_mutilxpath(browser, friend_xpaths)
            
            messaged_count = 0
            for friend_link in friend_links[:5]:  # Message up to 5 friends per page
                if self.stop_event and self.stop_event.is_set():
                    break
                
                try:
                    friend_url = friend_link.get_attribute('href')
                    if friend_url:
                        # Navigate to friend profile
                        browser.get(friend_url)
                        tools.delay_time(2)
                        
                        # Find message button
                        message_btn_xpaths = [
                            "//div[@role='button' and contains(@aria-label, 'Message')]",
                            "//div[@role='button' and contains(@aria-label, '发消息')]",
                            "//span[contains(text(), 'Message')]/ancestor::div[@role='button']"
                        ]
                        
                        message_button = None
                        for xpath in message_btn_xpaths:
                            try:
                                buttons = browser.find_elements('xpath', xpath)
                                if buttons:
                                    message_button = buttons[0]
                                    break
                            except:
                                continue
                        
                        if message_button:
                            browser.execute_script("arguments[0].click();", message_button)
                            tools.delay_time(2)
                            
                            # Wait for message input
                            message_input_xpaths = [
                                "//div[@role='textbox']",
                                "//div[@contenteditable='true']"
                            ]
                            
                            message_input = None
                            for xpath in message_input_xpaths:
                                try:
                                    inputs = browser.find_elements('xpath', xpath)
                                    if inputs:
                                        message_input = inputs[0]
                                        break
                                except:
                                    continue
                            
                            if message_input:
                                # Select message content
                                content = random.choice(message_content)
                                
                                # Add anti-ban message if enabled
                                if message_anti_ban:
                                    anti_ban_text = "This is an automated message. Please reply if you're interested."
                                    content = f"{content}\n\n{anti_ban_text}"
                                
                                message_input.send_keys(content)
                                tools.delay_time(random.uniform(1, 2))
                                
                                # Upload images if provided
                                if message_images:
                                    file_input_xpaths = [
                                        "//input[@type='file']",
                                        "//div[@role='button' and contains(@aria-label, 'Photo')]"
                                    ]
                                    for xpath in file_input_xpaths:
                                        try:
                                            file_inputs = browser.find_elements('xpath', xpath)
                                            if file_inputs:
                                                for img_path in message_images:
                                                    if os.path.exists(img_path):
                                                        file_inputs[0].send_keys(img_path)
                                                        tools.delay_time(2)
                                                break
                                        except:
                                            continue
                                
                                # Send message
                                send_button_xpaths = [
                                    "//div[@role='button' and contains(@aria-label, 'Send')]",
                                    "//div[@role='button' and contains(@aria-label, '发送')]"
                                ]
                                
                                for xpath in send_button_xpaths:
                                    try:
                                        buttons = browser.find_elements('xpath', xpath)
                                        if buttons:
                                            browser.execute_script("arguments[0].click();", buttons[0])
                                            tools.delay_time(random.uniform(2, 4))
                                            messaged_count += 1
                                            tools.send_message_to_ui(self.ms, self.ui, 
                                                                    f"私信发送成功 ({messaged_count})")
                                            
                                            # Cloud backup if enabled
                                            if message_cloud_backup:
                                                # Save message log (implement cloud backup logic here)
                                                log.info(f"Message sent to {friend_url} - Cloud backup enabled")
                                            
                                            tools.delay_time(random.uniform(message_interval, message_interval * 1.5))
                                            break
                                    except:
                                        continue
                            
                            # Close message dialog
                            close_button_xpaths = [
                                "//div[@role='button' and contains(@aria-label, 'Close')]",
                                "//span[.//*[name()='line']]"
                            ]
                            for xpath in close_button_xpaths:
                                try:
                                    buttons = browser.find_elements('xpath', xpath)
                                    if buttons:
                                        buttons[0].click()
                                        tools.delay_time(1)
                                        break
                                except:
                                    continue
                        
                        # Go back
                        browser.back()
                        tools.delay_time(1)
                except Exception as e:
                    log.error(f"Error messaging friend: {e}")
                    continue
            
            if messaged_count > 0:
                tools.send_message_to_ui(self.ms, self.ui, 
                                        f"本页私信完成: {messaged_count} 个好友")
            
        except Exception as e:
            log.error(f"Error in advanced messaging: {e}")
            tools.send_message_to_ui(self.ms, self.ui, f"高级私信出错: {str(e)}")

