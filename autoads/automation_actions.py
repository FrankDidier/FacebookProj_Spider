# -*- coding: utf-8 -*-
"""
Automation Actions - Core automation functions for Facebook interactions
"""
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from autoads.log import log
from autoads import tools
import random
import time


class AutomationActions:
    """Core automation actions for Facebook interactions"""
    
    @staticmethod
    def like_post(browser, post_element=None, xpath_selectors=None):
        """
        Like a Facebook post
        Args:
            browser: Selenium WebDriver instance
            post_element: Optional specific post element to like
            xpath_selectors: List of XPath selectors for like button
        Returns:
            bool: True if liked successfully, False otherwise
        """
        try:
            if xpath_selectors is None:
                xpath_selectors = [
                    ".//div[@role='button' and contains(@aria-label, 'Like')]",
                    ".//span[contains(text(), 'Like')]/ancestor::div[@role='button']",
                    ".//div[contains(@aria-label, '赞')]/ancestor::div[@role='button']",
                    ".//span[contains(@class, 'like')]/ancestor::div[@role='button']"
                ]
            
            like_button = None
            if post_element:
                for xpath in xpath_selectors:
                    try:
                        like_buttons = post_element.find_elements('xpath', xpath)
                        if like_buttons:
                            like_button = like_buttons[0]
                            break
                    except:
                        continue
            
            if not like_button:
                # Try to find like button on page
                for xpath in xpath_selectors:
                    try:
                        like_buttons = browser.find_elements('xpath', xpath)
                        if like_buttons:
                            like_button = like_buttons[0]
                            break
                    except:
                        continue
            
            if like_button:
                browser.execute_script("arguments[0].click();", like_button)
                tools.delay_time(random.uniform(1, 3))
                log.info("Post liked successfully")
                return True
            else:
                log.warning("Like button not found")
                return False
                
        except Exception as e:
            log.error(f"Error liking post: {e}")
            return False
    
    @staticmethod
    def comment_on_post(browser, comment_text, post_element=None, xpath_selectors=None):
        """
        Comment on a Facebook post
        Args:
            browser: Selenium WebDriver instance
            comment_text: Text to comment
            post_element: Optional specific post element
            xpath_selectors: List of XPath selectors for comment box
        Returns:
            bool: True if commented successfully, False otherwise
        """
        try:
            if xpath_selectors is None:
                xpath_selectors = [
                    ".//div[@role='textbox' and contains(@aria-label, 'Write a comment')]",
                    ".//div[@role='textbox' and contains(@aria-label, '写评论')]",
                    ".//div[@contenteditable='true' and contains(@role, 'textbox')]",
                    ".//textarea[@placeholder*='comment' or @placeholder*='评论']"
                ]
            
            comment_box = None
            if post_element:
                for xpath in xpath_selectors:
                    try:
                        comment_boxes = post_element.find_elements('xpath', xpath)
                        if comment_boxes:
                            comment_box = comment_boxes[0]
                            break
                    except:
                        continue
            
            if not comment_box:
                # Try to find comment box on page
                for xpath in xpath_selectors:
                    try:
                        comment_boxes = browser.find_elements('xpath', xpath)
                        if comment_boxes:
                            comment_box = comment_boxes[0]
                            break
                    except:
                        continue
            
            if comment_box:
                # Click to focus
                browser.execute_script("arguments[0].click();", comment_box)
                tools.delay_time(1)
                
                # Type comment
                comment_box.send_keys(comment_text)
                tools.delay_time(random.uniform(1, 2))
                
                # Find and click post button
                post_button_xpaths = [
                    ".//div[@role='button' and contains(@aria-label, 'Post')]",
                    ".//div[@role='button' and contains(@aria-label, '发布')]",
                    ".//span[contains(text(), 'Post')]/ancestor::div[@role='button']",
                    ".//span[contains(text(), '发布')]/ancestor::div[@role='button']"
                ]
                
                for xpath in post_button_xpaths:
                    try:
                        if post_element:
                            post_buttons = post_element.find_elements('xpath', xpath)
                            post_button = post_buttons[0] if post_buttons else None
                        else:
                            post_buttons = browser.find_elements('xpath', xpath)
                            post_button = post_buttons[0] if post_buttons else None
                        
                        if post_button:
                            browser.execute_script("arguments[0].click();", post_button)
                            tools.delay_time(random.uniform(2, 4))
                            log.info(f"Comment posted: {comment_text[:50]}")
                            return True
                    except:
                        continue
                
                log.warning("Post button not found after typing comment")
                return False
            else:
                log.warning("Comment box not found")
                return False
                
        except Exception as e:
            log.error(f"Error commenting on post: {e}")
            return False
    
    @staticmethod
    def follow_user(browser, user_url=None, xpath_selectors=None):
        """
        Follow a Facebook user/page
        Args:
            browser: Selenium WebDriver instance
            user_url: Optional URL of user to follow
            xpath_selectors: List of XPath selectors for follow button
        Returns:
            bool: True if followed successfully, False otherwise
        """
        try:
            if user_url:
                browser.get(user_url)
                tools.delay_time(3)
            
            if xpath_selectors is None:
                xpath_selectors = [
                    "//div[@role='button' and contains(@aria-label, 'Follow')]",
                    "//div[@role='button' and contains(@aria-label, '关注')]",
                    "//span[contains(text(), 'Follow')]/ancestor::div[@role='button']",
                    "//span[contains(text(), '关注')]/ancestor::div[@role='button']"
                ]
            
            follow_button = None
            for xpath in xpath_selectors:
                try:
                    buttons = browser.find_elements('xpath', xpath)
                    if buttons:
                        follow_button = buttons[0]
                        break
                except:
                    continue
            
            if follow_button:
                browser.execute_script("arguments[0].click();", follow_button)
                tools.delay_time(random.uniform(2, 4))
                log.info("User followed successfully")
                return True
            else:
                log.warning("Follow button not found")
                return False
                
        except Exception as e:
            log.error(f"Error following user: {e}")
            return False
    
    @staticmethod
    def add_friend(browser, user_url=None, xpath_selectors=None):
        """
        Send friend request to a Facebook user
        Args:
            browser: Selenium WebDriver instance
            user_url: Optional URL of user to add
            xpath_selectors: List of XPath selectors for add friend button
        Returns:
            bool: True if friend request sent successfully, False otherwise
        """
        try:
            if user_url:
                browser.get(user_url)
                tools.delay_time(3)
            
            if xpath_selectors is None:
                xpath_selectors = [
                    "//div[@role='button' and contains(@aria-label, 'Add Friend')]",
                    "//div[@role='button' and contains(@aria-label, '加为好友')]",
                    "//span[contains(text(), 'Add Friend')]/ancestor::div[@role='button']",
                    "//span[contains(text(), '加为好友')]/ancestor::div[@role='button']"
                ]
            
            add_friend_button = None
            for xpath in xpath_selectors:
                try:
                    buttons = browser.find_elements('xpath', xpath)
                    if buttons:
                        add_friend_button = buttons[0]
                        break
                except:
                    continue
            
            if add_friend_button:
                browser.execute_script("arguments[0].click();", add_friend_button)
                tools.delay_time(random.uniform(2, 4))
                log.info("Friend request sent successfully")
                return True
            else:
                log.warning("Add friend button not found")
                return False
                
        except Exception as e:
            log.error(f"Error adding friend: {e}")
            return False
    
    @staticmethod
    def join_group(browser, group_url, xpath_selectors=None):
        """
        Join a Facebook group
        Args:
            browser: Selenium WebDriver instance
            group_url: URL of group to join
            xpath_selectors: List of XPath selectors for join button
        Returns:
            bool: True if joined successfully, False otherwise
        """
        try:
            browser.get(group_url)
            tools.delay_time(3)
            
            if xpath_selectors is None:
                xpath_selectors = [
                    "//div[@role='button' and contains(@aria-label, 'Join')]",
                    "//div[@role='button' and contains(@aria-label, '加入')]",
                    "//span[contains(text(), 'Join Group')]/ancestor::div[@role='button']",
                    "//span[contains(text(), '加入小组')]/ancestor::div[@role='button']"
                ]
            
            join_button = None
            for xpath in xpath_selectors:
                try:
                    buttons = browser.find_elements('xpath', xpath)
                    if buttons:
                        join_button = buttons[0]
                        break
                except:
                    continue
            
            if join_button:
                browser.execute_script("arguments[0].click();", join_button)
                tools.delay_time(random.uniform(2, 4))
                
                # Check for questions dialog
                question_dialogs = browser.find_elements('xpath', "//div[@role='dialog']")
                if question_dialogs:
                    # Handle questions if needed
                    log.info("Group join requires answering questions")
                
                log.info("Group join request sent successfully")
                return True
            else:
                log.warning("Join button not found")
                return False
                
        except Exception as e:
            log.error(f"Error joining group: {e}")
            return False
    
    @staticmethod
    def post_to_group(browser, group_url, post_content, images=None, xpath_selectors=None):
        """
        Post content to a Facebook group
        Args:
            browser: Selenium WebDriver instance
            group_url: URL of group to post to
            post_content: Text content to post
            images: Optional list of image paths
            xpath_selectors: List of XPath selectors for post input
        Returns:
            bool: True if posted successfully, False otherwise
        """
        try:
            browser.get(group_url)
            tools.delay_time(3)
            
            if xpath_selectors is None:
                xpath_selectors = [
                    "//div[@role='textbox' and contains(@aria-label, 'Write something')]",
                    "//div[@role='textbox' and contains(@aria-label, '写点什么')]",
                    "//div[@contenteditable='true' and contains(@data-testid, 'post')]"
                ]
            
            post_input = None
            for xpath in xpath_selectors:
                try:
                    inputs = browser.find_elements('xpath', xpath)
                    if inputs:
                        post_input = inputs[0]
                        break
                except:
                    continue
            
            if post_input:
                browser.execute_script("arguments[0].click();", post_input)
                tools.delay_time(1)
                post_input.send_keys(post_content)
                tools.delay_time(random.uniform(1, 2))
                
                # Upload images if provided
                if images:
                    file_input_xpaths = [
                        "//input[@type='file']",
                        "//div[@role='button' and contains(@aria-label, 'Photo')]"
                    ]
                    for xpath in file_input_xpaths:
                        try:
                            file_inputs = browser.find_elements('xpath', xpath)
                            if file_inputs:
                                for img_path in images:
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
                            log.info("Post published successfully")
                            return True
                    except:
                        continue
                
                log.warning("Post button not found")
                return False
            else:
                log.warning("Post input not found")
                return False
                
        except Exception as e:
            log.error(f"Error posting to group: {e}")
            return False

    @staticmethod
    def send_message(browser, recipient_url=None, message_text="", images=None):
        """
        Send a private message to a user
        Args:
            browser: Selenium WebDriver instance
            recipient_url: URL of the user's profile or messenger page
            message_text: Text message to send
            images: Optional list of image paths to attach
        Returns:
            bool: True if message sent successfully, False otherwise
        """
        try:
            if recipient_url:
                # Navigate to messenger with user
                messenger_url = recipient_url.replace('/profile.php', '/messages/t/').replace('www.facebook.com/', 'www.facebook.com/messages/t/')
                if '/messages/t/' not in messenger_url:
                    # Extract user ID and construct messenger URL
                    if '?' in messenger_url:
                        messenger_url = f"https://www.facebook.com/messages/t/{messenger_url.split('id=')[-1].split('&')[0]}"
                    else:
                        messenger_url = f"https://www.facebook.com/messages/t/{messenger_url.split('/')[-1]}"
                
                browser.get(messenger_url)
                tools.delay_time(3)
            
            # Find message input
            message_input_xpaths = [
                "//div[@role='textbox' and contains(@aria-label, 'Message')]",
                "//div[@role='textbox' and contains(@aria-label, '消息')]",
                "//div[@contenteditable='true' and contains(@data-testid, 'message')]",
                "//div[@role='textbox'][@contenteditable='true']"
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
                browser.execute_script("arguments[0].click();", message_input)
                tools.delay_time(0.5)
                message_input.send_keys(message_text)
                tools.delay_time(random.uniform(0.5, 1))
                
                # Upload images if provided
                if images:
                    try:
                        file_inputs = browser.find_elements('xpath', "//input[@type='file']")
                        if file_inputs:
                            for img_path in images:
                                file_inputs[0].send_keys(img_path)
                                tools.delay_time(2)
                    except:
                        pass
                
                # Send message (press Enter or click send button)
                from selenium.webdriver.common.keys import Keys
                message_input.send_keys(Keys.RETURN)
                tools.delay_time(random.uniform(2, 3))
                
                log.info("Message sent successfully")
                return True
            else:
                log.warning("Message input not found")
                return False
                
        except Exception as e:
            log.error(f"Error sending message: {e}")
            return False

    @staticmethod
    def register_account(browser, registration_data=None):
        """
        Register a new Facebook account
        Args:
            browser: Selenium WebDriver instance
            registration_data: Dictionary with registration info:
                - first_name: First name
                - last_name: Last name
                - email or phone: Email or phone number
                - password: Password
                - birthday: {'month': 1, 'day': 1, 'year': 1990}
                - gender: 'male', 'female', or 'custom'
        Returns:
            dict: Registration result with status and details
        """
        try:
            result = {
                'success': False,
                'message': '',
                'account': None
            }
            
            if not registration_data:
                result['message'] = 'No registration data provided'
                return result
            
            # Navigate to registration page
            browser.get("https://www.facebook.com/r.php")
            tools.delay_time(3)
            
            # Fill in first name
            first_name_inputs = browser.find_elements('xpath', "//input[@name='firstname']")
            if first_name_inputs:
                first_name_inputs[0].send_keys(registration_data.get('first_name', ''))
                tools.delay_time(0.5)
            
            # Fill in last name
            last_name_inputs = browser.find_elements('xpath', "//input[@name='lastname']")
            if last_name_inputs:
                last_name_inputs[0].send_keys(registration_data.get('last_name', ''))
                tools.delay_time(0.5)
            
            # Fill in email or phone
            email_inputs = browser.find_elements('xpath', "//input[@name='reg_email__']")
            if email_inputs:
                email_inputs[0].send_keys(registration_data.get('email', registration_data.get('phone', '')))
                tools.delay_time(0.5)
            
            # Fill in password
            password_inputs = browser.find_elements('xpath', "//input[@name='reg_passwd__']")
            if password_inputs:
                password_inputs[0].send_keys(registration_data.get('password', ''))
                tools.delay_time(0.5)
            
            # Select birthday
            birthday = registration_data.get('birthday', {})
            if birthday:
                # Month
                month_selects = browser.find_elements('xpath', "//select[@name='birthday_month']")
                if month_selects:
                    from selenium.webdriver.support.ui import Select
                    Select(month_selects[0]).select_by_value(str(birthday.get('month', 1)))
                
                # Day
                day_selects = browser.find_elements('xpath', "//select[@name='birthday_day']")
                if day_selects:
                    Select(day_selects[0]).select_by_value(str(birthday.get('day', 1)))
                
                # Year
                year_selects = browser.find_elements('xpath', "//select[@name='birthday_year']")
                if year_selects:
                    Select(year_selects[0]).select_by_value(str(birthday.get('year', 1990)))
            
            # Select gender
            gender = registration_data.get('gender', 'male')
            gender_map = {'male': '2', 'female': '1', 'custom': '-1'}
            gender_radios = browser.find_elements('xpath', f"//input[@name='sex' and @value='{gender_map.get(gender, '2')}']")
            if gender_radios:
                browser.execute_script("arguments[0].click();", gender_radios[0])
            
            tools.delay_time(1)
            
            # Click submit button
            submit_buttons = browser.find_elements('xpath', "//button[@name='websubmit']")
            if submit_buttons:
                browser.execute_script("arguments[0].click();", submit_buttons[0])
                tools.delay_time(5)
                
                result['success'] = True
                result['message'] = 'Registration form submitted'
                result['account'] = {
                    'email': registration_data.get('email', ''),
                    'phone': registration_data.get('phone', ''),
                    'name': f"{registration_data.get('first_name', '')} {registration_data.get('last_name', '')}"
                }
            else:
                result['message'] = 'Submit button not found'
            
            return result
            
        except Exception as e:
            log.error(f"Error registering account: {e}")
            return {'success': False, 'message': str(e), 'account': None}

    @staticmethod
    def generate_contact_list(count=10, country_code='+1', area_code='', name_language='en', sequential=False):
        """
        Generate a contact list with random names and phone numbers
        Args:
            count: Number of contacts to generate
            country_code: Country code (e.g., '+1' for US)
            area_code: Area code (e.g., '415' for San Francisco)
            name_language: Language for names ('en' for English, 'cn' for Chinese)
            sequential: If True, generate sequential phone numbers
        Returns:
            list: List of contact dictionaries with 'name' and 'phone'
        """
        import random
        import string
        
        contacts = []
        
        # English name components
        en_first_names = ['John', 'Jane', 'Michael', 'Emily', 'David', 'Sarah', 'James', 'Emma', 'Robert', 'Olivia',
                          'William', 'Sophia', 'Richard', 'Isabella', 'Joseph', 'Mia', 'Thomas', 'Charlotte', 'Christopher', 'Amelia']
        en_last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez',
                         'Anderson', 'Taylor', 'Thomas', 'Moore', 'Jackson', 'Martin', 'Lee', 'Thompson', 'White', 'Harris']
        
        # Chinese name components
        cn_last_names = ['王', '李', '张', '刘', '陈', '杨', '黄', '赵', '周', '吴', '徐', '孙', '马', '朱', '胡']
        cn_first_names = ['伟', '芳', '娜', '秀英', '敏', '静', '丽', '强', '磊', '军', '洋', '勇', '艳', '杰', '娟']
        
        # Generate area code if not provided
        if not area_code:
            area_code = str(random.randint(200, 999))
        
        # Base number for sequential generation
        base_number = random.randint(1000000, 9999999) if not sequential else 1000000
        
        for i in range(count):
            # Generate name
            if name_language == 'cn':
                last = random.choice(cn_last_names)
                first = random.choice(cn_first_names)
                name = f"{last}{first}"
            else:
                first = random.choice(en_first_names)
                last = random.choice(en_last_names)
                name = f"{first} {last}"
            
            # Generate phone number
            if sequential:
                phone_number = f"{country_code}{area_code}{base_number + i}"
            else:
                phone_number = f"{country_code}{area_code}{random.randint(1000000, 9999999)}"
            
            contacts.append({
                'name': name,
                'phone': phone_number
            })
        
        log.info(f"Generated {len(contacts)} contacts")
        return contacts

