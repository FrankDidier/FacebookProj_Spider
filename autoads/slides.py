# -*- coding: utf-8 -*-
# @Date:2020/2/15 2:09
# @Author: Lu
# @Description bilibili滑块验证码识别。B站有反爬限制，过快地拖拽会提示“怪物吃了拼图，请重试”。
# 目前B站有三张图片，只要对比完整图和缺失滑块背景图的像素，就可以得到偏移图片y轴距离，减去滑块空白距离=需要滑动的像素距离
# 这里采用边缘检测，检测缺失滑块的底图是否存在一条灰色竖线，即认为是滑块目标位置，存在失败的概率，适用范围应该更大些。
# https://blog.csdn.net/weixin_44549063/article/details/112193218
# https://blog.csdn.net/sinat_28371057/article/details/111824605

from selenium import webdriver
import time
import base64
import requests
from io import BytesIO
from selenium.webdriver.support.ui import WebDriverWait
import random
import json


def __get_random_pause_seconds():
    """
    :return:随机的拖动暂停时间
    """
    return random.uniform(0.6, 0.9)


def simulate_rotate_drag(driver, bg_url, rotate_url):
    """
    模拟人工拖动旋转图片
    :param driver:
    :param bg_url:
    :param rotate_url:
    :return:
    """

    res = requests.get(bg_url)
    bg_image_base64 = base64.b64encode(BytesIO(res.content).read())

    res = requests.get(rotate_url)
    rotate_image_base64 = base64.b64encode(BytesIO(res.content).read())

    data = {'slide_length': 100, 'bg_image': bg_image_base64, 'rotate_image': rotate_image_base64}

    res = requests.post('http://127.0.0.1:5000/rotate', data=data).json()
    target_offset = res['distance']

    source = driver.find_element_by_css_selector(".geetest_slider_button")
    action_chains = webdriver.ActionChains(driver)
    # 点击，准备拖拽
    action_chains.click_and_hold(source)
    for offset in target_offset:
        x = offset[0]
        y = offset[1]
        action_chains.move_by_offset(x, y)
        # 暂停一会
        action_chains.pause(__get_random_pause_seconds())

    action_chains.release()
    action_chains.perform()
    pass


def simulate_rect_drag(driver, bg_url, slide_url):
    """
    模拟人工拖动验证框
    :param driver:
    :param bg_url:
    :param slide_url:
    :return:
    """

    # WebDriverWait(driver, 5).until(
    #     lambda driver: driver.find_element_by_css_selector('.geetest_canvas_bg.geetest_absolute'))
    # time.sleep(1)
    res = requests.get(bg_url)
    bg_image_base64 = base64.b64encode(BytesIO(res.content).read())

    res = requests.get(slide_url)
    slide_image_base64 = base64.b64encode(BytesIO(res.content).read())

    data = {'offset': 10, 'bg_image': bg_image_base64, 'slide_image': slide_image_base64}
    res = requests.post('http://127.0.0.1:5000/distance', data=data).json()
    target_offset = res['distance']

    source = driver.find_element_by_css_selector(".geetest_slider_button")
    action_chains = webdriver.ActionChains(driver)
    # 点击，准备拖拽
    action_chains.click_and_hold(source)
    for offset in target_offset:
        x = offset[0]
        y = offset[1]
        action_chains.move_by_offset(x, y)
        # 暂停一会
        action_chains.pause(__get_random_pause_seconds())

    action_chains.release()
    action_chains.perform()


if __name__ == '__main__':
    # simulate_rect_drag(None,
    #                    bg_url='https://p16-captcha-va.ibyteimg.com/tos-maliva-i-71rtze2081-us/470ee1b6880140fd94a5839390afa67e~tplv-71rtze2081-2.jpeg',
    #                    slide_url='https://p16-captcha-va.ibyteimg.com/tos-maliva-i-71rtze2081-us/3c12e660c21e4252bc2aecb91422efa5~tplv-71rtze2081-1.png')

    simulate_rotate_drag(None,
                         bg_url='https://p19-captcha-va.ibyteimg.com/tos-maliva-i-71rtze2081-us/edf6c1d22e6a488693737b74f3ae8917~tplv-71rtze2081-1.png',
                         rotate_url='https://p19-captcha-va.ibyteimg.com/tos-maliva-i-71rtze2081-us/1ffa1ebf3dfd4209aaeaa466ad6342ca~tplv-71rtze2081-1.png')
