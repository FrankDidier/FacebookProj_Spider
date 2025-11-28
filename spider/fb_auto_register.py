# -*- coding: utf-8 -*-
"""
FB Auto Register - Automatically register new Facebook accounts
"""
import autoads
from autoads.log import log
from autoads import tools
from autoads.config import config
from autoads import ads_api
import random
import string
import time


class AutoRegisterSpider(autoads.AirSpider):
    """Automatically register new Facebook accounts"""
    
    def start_requests(self):
        if not self.ads_ids:
            self.ads_ids = tools.get_ads_id(self.config.account_nums)
        
        register_count = getattr(config, 'register_count', 1)
        register_name_lang = getattr(config, 'register_name_lang', 'en')  # en, zh, etc.
        register_country_code = getattr(config, 'register_country_code', '+1')
        register_sms_platform = getattr(config, 'register_sms_platform', '')
        register_sms_api = getattr(config, 'register_sms_api', '')
        register_old_version = getattr(config, 'register_old_version', False)
        
        tools.send_message_to_ui(self.ms, self.ui, 
                                 f"开始自动注册: 数量={register_count}")
        
        i = 0
        priority = 10
        
        if register_old_version:
            url = "https://www.facebook.com/r.php"
        else:
            url = "https://www.facebook.com/reg/"
        
        for j in range(register_count):
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
                register_name_lang=register_name_lang,
                register_country_code=register_country_code,
                register_sms_platform=register_sms_platform,
                register_sms_api=register_sms_api,
                driver_count=len(self.ads_ids),
                stop_event=self.stop_event
            )
    
    def generate_name(self, lang='en'):
        """Generate random name based on language"""
        if lang == 'en':
            first_names = ['John', 'Jane', 'Mike', 'Sarah', 'David', 'Emily', 'Chris', 'Lisa']
            last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis']
        elif lang == 'zh':
            first_names = ['明', '强', '伟', '芳', '娜', '敏', '静', '丽']
            last_names = ['王', '李', '张', '刘', '陈', '杨', '赵', '黄']
        else:
            first_names = ['John', 'Jane', 'Mike', 'Sarah']
            last_names = ['Smith', 'Johnson', 'Williams', 'Brown']
        
        return random.choice(first_names), random.choice(last_names)
    
    def get_phone_number(self, country_code, sms_platform, sms_api):
        """Get phone number from SMS platform"""
        try:
            if sms_platform and sms_api:
                # Call SMS platform API to get phone number
                # Supports common SMS platforms: 5sim, sms-activate, etc.
                import requests
                
                # Try different SMS platform API formats
                api_endpoints = [
                    f"{sms_api}/get_number?country={country_code}",
                    f"{sms_api}/api/v1/get_number?country={country_code}",
                    f"{sms_api}/number?country={country_code}",
                ]
                
                for endpoint in api_endpoints:
                    try:
                        response = requests.get(endpoint, timeout=10)
                        if response.status_code == 200:
                            data = response.json()
                            # Try common response formats
                            phone = (data.get('phone_number') or 
                                    data.get('phone') or 
                                    data.get('number') or
                                    data.get('data', {}).get('phone_number') or
                                    data.get('data', {}).get('phone'))
                            if phone:
                                log.info(f"Got phone number from SMS platform: {phone}")
                                return phone
                    except:
                        continue
                
                log.warning(f"Could not get phone number from SMS platform: {sms_platform}")
                return None
            return None
        except Exception as e:
            log.error(f"Error getting phone number: {e}")
            return None
    
    def get_sms_code(self, sms_api, phone_number, timeout=120):
        """Get SMS verification code from SMS platform"""
        try:
            if sms_api and phone_number:
                import requests
                import time
                
                # Try different SMS platform API formats for getting codes
                api_endpoints = [
                    f"{sms_api}/get_code?phone={phone_number}",
                    f"{sms_api}/api/v1/get_code?phone={phone_number}",
                    f"{sms_api}/code?phone={phone_number}",
                    f"{sms_api}/sms?phone={phone_number}",
                ]
                
                # Poll for SMS code (wait up to timeout seconds)
                start_time = time.time()
                while time.time() - start_time < timeout:
                    for endpoint in api_endpoints:
                        try:
                            response = requests.get(endpoint, timeout=5)
                            if response.status_code == 200:
                                data = response.json()
                                # Try common response formats
                                code = (data.get('code') or 
                                       data.get('sms_code') or 
                                       data.get('verification_code') or
                                       data.get('data', {}).get('code') or
                                       data.get('data', {}).get('sms_code'))
                                if code:
                                    log.info(f"Got SMS code from platform: {code}")
                                    return code
                        except:
                            continue
                    
                    # Wait before next poll
                    time.sleep(5)
                
                log.warning(f"Timeout waiting for SMS code from platform")
                return None
            return None
        except Exception as e:
            log.error(f"Error getting SMS code: {e}")
            return None
    
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
        
        register_name_lang = getattr(request, 'register_name_lang', 'en')
        register_country_code = getattr(request, 'register_country_code', '+1')
        register_sms_platform = getattr(request, 'register_sms_platform', '')
        register_sms_api = getattr(request, 'register_sms_api', '')
        
        try:
            first_name, last_name = self.generate_name(register_name_lang)
            
            # Fill first name
            first_name_xpaths = [
                "//input[@name='firstname']",
                "//input[@placeholder*='First name' or @placeholder*='名']"
            ]
            for xpath in first_name_xpaths:
                try:
                    inputs = browser.find_elements('xpath', xpath)
                    if inputs:
                        inputs[0].send_keys(first_name)
                        break
                except:
                    continue
            
            tools.delay_time(1)
            
            # Fill last name
            last_name_xpaths = [
                "//input[@name='lastname']",
                "//input[@placeholder*='Last name' or @placeholder*='姓']"
            ]
            for xpath in last_name_xpaths:
                try:
                    inputs = browser.find_elements('xpath', xpath)
                    if inputs:
                        inputs[0].send_keys(last_name)
                        break
                except:
                    continue
            
            tools.delay_time(1)
            
            # Generate email
            email = f"{first_name.lower()}{last_name.lower()}{random.randint(1000, 9999)}@gmail.com"
            
            # Fill email
            email_xpaths = [
                "//input[@name='reg_email__']",
                "//input[@type='email']"
            ]
            for xpath in email_xpaths:
                try:
                    inputs = browser.find_elements('xpath', xpath)
                    if inputs:
                        inputs[0].send_keys(email)
                        break
                except:
                    continue
            
            tools.delay_time(1)
            
            # Fill confirm email
            confirm_email_xpaths = [
                "//input[@name='reg_email_confirmation__']"
            ]
            for xpath in confirm_email_xpaths:
                try:
                    inputs = browser.find_elements('xpath', xpath)
                    if inputs:
                        inputs[0].send_keys(email)
                        break
                except:
                    continue
            
            tools.delay_time(1)
            
            # Generate password
            password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
            
            # Fill password
            password_xpaths = [
                "//input[@name='reg_passwd__']",
                "//input[@type='password']"
            ]
            for xpath in password_xpaths:
                try:
                    inputs = browser.find_elements('xpath', xpath)
                    if inputs:
                        inputs[0].send_keys(password)
                        break
                except:
                    continue
            
            tools.delay_time(1)
            
            # Select birthday
            # This is simplified - actual implementation needs dropdown selection
            day = str(random.randint(1, 28))
            month = str(random.randint(1, 12))
            year = str(random.randint(1990, 2000))
            
            # Get phone number from SMS platform
            phone_number = self.get_phone_number(register_country_code, register_sms_platform, register_sms_api)
            
            if phone_number:
                # Fill phone number
                phone_xpaths = [
                    "//input[@name='reg_email__']",
                    "//input[@type='tel']"
                ]
                for xpath in phone_xpaths:
                    try:
                        inputs = browser.find_elements('xpath', xpath)
                        if inputs:
                            inputs[0].send_keys(phone_number)
                            break
                    except:
                        continue
            
            tools.delay_time(2)
            
            # Click sign up button
            signup_xpaths = [
                "//button[@name='websubmit']",
                "//button[contains(text(), 'Sign Up') or contains(text(), '注册')]"
            ]
            
            for xpath in signup_xpaths:
                try:
                    buttons = browser.find_elements('xpath', xpath)
                    if buttons:
                        browser.execute_script("arguments[0].click();", buttons[0])
                        tools.delay_time(5)
                        
                        # Wait for verification code
                        if phone_number:
                            tools.send_message_to_ui(self.ms, self.ui, 
                                                    f"等待验证码: {phone_number}")
                            # Get SMS verification code from SMS platform
                            if register_sms_platform and register_sms_api:
                                sms_code = self.get_sms_code(register_sms_api, phone_number)
                                if sms_code:
                                    # Enter SMS code
                                    code_input_xpaths = [
                                        "//input[@type='text' and contains(@name, 'code')]",
                                        "//input[@placeholder*='code' or @placeholder*='验证码']",
                                        "//input[@id*='code' or @id*='verification']"
                                    ]
                                    
                                    code_input = None
                                    for xpath in code_input_xpaths:
                                        try:
                                            inputs = browser.find_elements('xpath', xpath)
                                            if inputs:
                                                code_input = inputs[0]
                                                break
                                        except:
                                            continue
                                    
                                    if code_input:
                                        code_input.send_keys(sms_code)
                                        tools.delay_time(2)
                                        log.info("SMS code entered")
                                    else:
                                        log.warning("Could not find SMS code input field")
                                else:
                                    log.warning("Could not retrieve SMS code from platform")
                            time.sleep(10)
                        
                        tools.send_message_to_ui(self.ms, self.ui, 
                                                f"注册完成: {first_name} {last_name}")
                        return
                except:
                    continue
            
            log.warning("Sign up button not found")
            
        except Exception as e:
            log.error(f"Error in auto-register: {e}")
            tools.send_message_to_ui(self.ms, self.ui, f"注册出错: {str(e)}")

