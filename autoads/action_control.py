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

    def scroll_until_loaded(self):
        if self.browser:
            try:
                check_height = self.browser.execute_script("return document.body.scrollHeight;")
                self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                flag = self.wait.until(
                    lambda driver: driver.execute_script("return document.body.scrollHeight;") > check_height)
                return not flag

            except Exception as e:
                log.error(e)
                return True
        else:
            return True

    def scroll(self):
        # 页面一直滚动，直到‘已经到底啦~’出现
        # 慢慢的下拉

        if self.browser:
            try:
                check_height = self.browser.execute_script("return document.body.scrollHeight;")
                is_finished = False
                # 整个滚动条高度，10等分来滚动
                # slides = self.slide_list(check_height)
                slides = [check_height // 10] * 10
                # print('browser id:' + str(id(self.browser)))
                for split_distance in slides:
                    before_scroll = self.browser.execute_script('return window.document.documentElement.scrollTop;')
                    # log.info(before_scroll)
                    self.browser.execute_script(f'window.scrollBy(0,{split_distance})')
                    log.info(f'scroll down by {split_distance}')
                    tools.delay_time(random.randint(100, 200) / 100)
                    after_scroll = self.browser.execute_script('return window.document.documentElement.scrollTop;')
                    # log.info(after_scroll)
                    # 每次移动一下都检查是不是已经到底啦！
                    is_finished = before_scroll == after_scroll
                    # log.info(f'已经到底啦-->{is_finished}')

                    if is_finished:
                        return is_finished
                # log.info('已经执行完成了这一轮')
                return is_finished
            except Exception as e:
                log.error(e)
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
