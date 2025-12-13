#!/anaconda3/bin python3.7
# -*- coding: utf-8 -*-
# ---
# @Software: PyCharm
# @File: action_control.py
# @Author: James.Zhou
# @E-mail: 407360491@163.com
# @Site: 
# @Time: 七月 04, 2022
# ---


import threading
from autoads.webdriver import WebDriver
from queue import Queue

import autoads.tools as tools
from autoads.log import log
import random

from selenium.common.exceptions import TimeoutException

from selenium.webdriver.support.wait import WebDriverWait

MAX_ITEM_COUNT = 5000


class ActionControl(threading.Thread):
    is_finished = False

    def __init__(self, ):
        super(ActionControl, self).__init__()
        self._action_queue = Queue(maxsize=MAX_ITEM_COUNT)

    def run(self):
        self._thread_stop = False
        while not self._thread_stop:
            while not self._action_queue.empty():
                action = self._action_queue.get_nowait()
                # print(action.browser._ads_id)
                # log.info('action 开始执行页面滚动程序')
                self.is_finished = action.scroll()
                # log.info(f'action 执行页面滚动程序结束,is finished:{self.is_finished}')
            tools.delay_time(1)

    def stop(self):
        self._thread_stop = True
        self._started.clear()

    def put_action(self, action=None):
        # log.info('正在新增action')
        self._action_queue.put(action)

    def is_not_task(self):
        return self.is_finished


class Action(object):
    def __init__(self, browser: WebDriver):
        self.browser = browser
        self.wait = WebDriverWait(browser, 8)

    def scroll_until_loaded(self, max_retries=3):
        """
        Scroll down the page until no new content loads
        
        :param max_retries: Number of retries if scroll fails
        :return: True if finished scrolling, False if more content may load
        """
        if self.browser:
            for attempt in range(max_retries):
                try:
                    check_height = self.browser.execute_script("return document.body.scrollHeight;")
                    
                    # Use JavaScript scrolling instead of Selenium actions to avoid element interaction issues
                    self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    
                    # Wait a bit for content to load
                    tools.delay_time(1.5)
                    
                    # Check if more content loaded
                    new_height = self.browser.execute_script("return document.body.scrollHeight;")
                    
                    if new_height > check_height:
                        return False  # More content loaded, not finished
                    
                    # Try to trigger lazy loading by scrolling up slightly and then down
                    self.browser.execute_script("window.scrollBy(0, -300);")
                    tools.delay_time(0.5)
                    self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    tools.delay_time(1)
                    
                    final_height = self.browser.execute_script("return document.body.scrollHeight;")
                    
                    if final_height > check_height:
                        return False  # More content loaded
                    
                    return True  # No more content, finished

                except Exception as e:
                    log.error(f"Scroll attempt {attempt + 1}/{max_retries} failed: {e}")
                    tools.delay_time(1)
                    if attempt == max_retries - 1:
                        return True  # Give up and consider it finished
            return True
        else:
            return True

    def scroll(self, max_retries=3):
        """
        Scroll down the page slowly in increments
        
        :param max_retries: Number of retries if scroll fails
        :return: True if finished scrolling (reached bottom), False otherwise
        """
        if self.browser:
            for attempt in range(max_retries):
                try:
                    check_height = self.browser.execute_script("return document.body.scrollHeight;")
                    is_finished = False
                    
                    # Calculate scroll increments (10 steps)
                    scroll_increment = max(check_height // 10, 300)  # Minimum 300px per scroll
                    slides = [scroll_increment] * 10
                    
                    for split_distance in slides:
                        try:
                            before_scroll = self.browser.execute_script('return window.document.documentElement.scrollTop;')
                            
                            # Use pure JavaScript scroll to avoid element interaction issues
                            self.browser.execute_script(f'window.scrollBy(0, {split_distance});')
                            log.info(f'scroll down by {split_distance}')
                            
                            # Random delay to simulate human behavior
                            tools.delay_time(random.randint(100, 200) / 100)
                            
                            after_scroll = self.browser.execute_script('return window.document.documentElement.scrollTop;')
                            
                            # Check if we've reached the bottom
                            is_finished = abs(before_scroll - after_scroll) < 5  # Allow small margin
                            
                            if is_finished:
                                # Double-check by trying to scroll a bit more
                                self.browser.execute_script('window.scrollBy(0, 500);')
                                tools.delay_time(0.5)
                                final_scroll = self.browser.execute_script('return window.document.documentElement.scrollTop;')
                                is_finished = abs(after_scroll - final_scroll) < 5
                                
                                if is_finished:
                                    return True
                                    
                        except Exception as inner_e:
                            log.warning(f'Scroll step failed: {inner_e}')
                            continue
                    
                    return is_finished
                    
                except Exception as e:
                    log.error(f'Scroll attempt {attempt + 1}/{max_retries} failed: {e}')
                    tools.delay_time(1)
                    if attempt == max_retries - 1:
                        return True  # Give up and consider it finished
            return True
        else:
            return True

    # def random_linspace(self, num, length):
    #     '''辅助函数
    #       传入要分成的几段 -> num ；长度 -> length, 生成一个递增的、随机的、不严格等差数列
    #     '''
    #     # 数列的起始值 、 结束值。 这里以平均值的 0.5 作为起始值，平均值的 1.5倍作为结束值。
    #     start, end = 0.5 * (length / num), 1.5 * (length / num)
    #     # 借助三方库生成一个标准的等差数列，主要是得出标准等差 space
    #     origin_list = np.linspace(start, end, num)
    #     space = origin_list[1] - origin_list[0]
    #     # 在标准等差的基础上，设置上下浮动的大小，（上下浮动10%）
    #     min_random, max_random = -(space / 10), space / 10
    #     result = []
    #     # 等差数列的初始值不变，就是我们设置的start
    #     value = start
    #     # 将等差数列添加到 list
    #     result.append(value)
    #     # 初始值已经添加，循环的次数 减一
    #     for i in range(num - 1):
    #         # 浮动的等差值 space
    #         random_space = space + random.uniform(min_random, max_random)
    #         value += random_space
    #         result.append(value)
    #     return result
    #
    # def slide_list(self, total_length):
    #     ''' 规划移动轨迹 等差数列生成器，根据传入的长度，生成一个随机的，先递增后递减，不严格的等差数列'''
    #     # 具体分成几段是随机的
    #     total_num = random.randint(8, 10)
    #
    #     # 中间的拐点是随机的
    #     mid = total_num - random.randint(3, 5)
    #
    #     # 第一段、第二段的分段数
    #     first_num, second_num = mid, total_num - mid
    #
    #     # 第一段、第二段的长度，根据总长度，按比例分成
    #     first_length, second_length = total_length * (first_num / total_num), total_length * (second_num / total_num)
    #
    #     # 调用上面的辅助函数，生成两个随机等差数列
    #     first_result = self.random_linspace(first_num, first_length)
    #     second_result = self.random_linspace(second_num, second_length)
    #
    #     # 第二段等差数列进行逆序排序
    #     slide_result = first_result + second_result[::-1]
    #
    #     # 由于随机性，判断一下总长度是否满足，不满足的再补上一段
    #     if sum(slide_result) < total_length:
    #         remain_result = total_length - sum(slide_result)
    #         if remain_result < 2:
    #             remain_result = remain_result * 20
    #         slide_result.append(remain_result)
    #     return slide_result
