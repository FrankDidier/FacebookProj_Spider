# -*- coding: utf-8 -*-
"""
Created on 2021/3/18 4:59 下午
---------
@summary:
---------
@author: Boris
@email: boris_liu@foxmail.com
"""
import sys
import os
import time
import json
import errno
import threading
import subprocess
from subprocess import PIPE
import platform

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
from selenium.webdriver.chrome.service import Service

from autoads.log import log

import requests
from autoads.tools import Singleton
from autoads import tools
from autoads.config import config
from autoads import bitbrowser_api
from autoads.memory_db import MemoryDB
from autoads import ads_api


class NoConsoleService(Service):
    def start(self):
        try:
            cmd = [self.path]
            cmd.extend(self.command_line_args())
            if 'win32' == sys.platform.lower():
                si = subprocess.STARTUPINFO()
                si.dwFlags = subprocess.CREATE_NEW_CONSOLE | subprocess.STARTF_USESHOWWINDOW
                si.wShowWindow = subprocess.SW_HIDE
                self.process = subprocess.Popen(cmd, env=self.env,
                                                close_fds=platform.system() != 'Windows',
                                                startupinfo=si,
                                                stdout=self.log_file,
                                                stderr=self.log_file,
                                                stdin=PIPE)
            else:
                self.process = subprocess.Popen(cmd, env=self.env,
                                                close_fds=platform.system() != 'Windows',
                                                stdout=self.log_file,
                                                stderr=self.log_file,
                                                stdin=PIPE)
        except TypeError:
            raise
        except OSError as err:
            if err.errno == errno.ENOENT:
                raise WebDriverException(
                    "'%s' executable needs to be in PATH. %s" % (
                        os.path.basename(self.path), self.start_error_message)
                )
            elif err.errno == errno.EACCES:
                raise WebDriverException(
                    "'%s' executable may have wrong permissions. %s" % (
                        os.path.basename(self.path), self.start_error_message)
                )
            else:
                raise
        except Exception as e:
            raise WebDriverException(
                "The executable %s needs to be available in the path. %s\n%s" %
                (os.path.basename(self.path), self.start_error_message, str(e)))
        count = 0
        while True:
            self.assert_process_still_running()
            if self.is_connectable():
                break
            count += 1
            time.sleep(1)
            if count == 30:
                raise WebDriverException("Can not connect to the Service %s" % self.path)


class WebDriver(RemoteWebDriver):

    def __init__(
            self,
            timeout=16,
            window_size=[1, 1, 1024, 800],
            service_url=None,
            ads_id=None,
            stop_event=None,
            ms=None,
            ui=None,
            **kwargs,
    ):
        """
        webdirver 封装，支持chrome

        """

        self._timeout = timeout
        self._window_size = window_size
        self._service_url = service_url
        self._ads_id = ads_id
        self.retry_times = 0
        self.stop_event = stop_event
        self.ms = ms
        self.ui = ui

        self.driver = self.chrome_driver()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val:
            log.error(exc_val)

        self.quit()
        return True

    def get_driver(self):
        return self.driver

    def get_remote_driver(self):
        # Check browser type to use correct API
        browser_type = getattr(config, 'browser_type', 'adspower') if hasattr(config, 'browser_type') else 'adspower'
        
        tools.delay_time(2)
        log.info(f'线程{threading.current_thread().name}正在开启浏览器{self._ads_id}')
        tools.send_message_to_ui(ms=self.ms, ui=self.ui, message=f'获取远程浏览器{self._ads_id}启动参数中...')
        
        if not (self.stop_event and self.stop_event.isSet()):
            try:
                if browser_type == 'bitbrowser':
                    # BitBrowser uses POST with JSON body
                    log.info(f'使用 BitBrowser API 启动浏览器 {self._ads_id}')
                    result = bitbrowser_api.start_browser(self._ads_id)
                    log.info(f'BitBrowser API 返回: {result}')
                    
                    if result and result.get('success'):
                        data = result.get('data', {})
                        # BitBrowser returns format like:
                        # {"success":true,"data":{"http":"127.0.0.1:9222","ws":"ws://127.0.0.1:9222/devtools/browser/xxx","driver":"C:\\xxx\\chromedriver.exe"}}
                        
                        # Get WebSocket address - BitBrowser uses 'http' or direct IP:port for debugging
                        ws_address = data.get('http', '')  # Like "127.0.0.1:9222"
                        if not ws_address:
                            # Try alternative format
                            ws_address = data.get('ws', '').replace('ws://', '').split('/devtools')[0] if data.get('ws') else ''
                        
                        # Get chromedriver path
                        driver_path = data.get('driver', '') or data.get('webdriver', '')
                        
                        if ws_address and driver_path:
                            resp = {
                                'code': 0,
                                'data': {
                                    'ws': {
                                        'selenium': ws_address
                                    },
                                    'webdriver': driver_path
                                }
                            }
                            tools.send_message_to_ui(ms=self.ms, ui=self.ui, message=f'获取远程浏览器{self._ads_id}启动参数 | 成功！')
                            log.info(f'BitBrowser 开启浏览器结果={resp}')
                            return resp
                        else:
                            log.warning(f'BitBrowser 返回数据不完整: ws={ws_address}, driver={driver_path}')
                            # Still try to return what we got
                            resp = {
                                'code': 0,
                                'data': {
                                    'ws': {
                                        'selenium': ws_address or data.get('http', '') or '127.0.0.1:9222'
                                    },
                                    'webdriver': driver_path or 'chromedriver'
                                }
                            }
                            return resp
                    else:
                        msg = result.get('msg', 'Unknown error') if result else 'Failed to start browser'
                        log.error(f'BitBrowser 启动失败: {msg}')
                        tools.send_message_to_ui(ms=self.ms, ui=self.ui,
                                                message=f'获取远程浏览器{self._ads_id}启动参数 | 失败 | {msg} | 再次尝试！')
                        if self.retry_times < 3:
                            self.retry_times += 1
                            return self.get_remote_driver()
                        return None
                else:
                    # AdsPower uses GET with query parameters
                    open_url = f"{self._service_url}/api/v1/browser/start?user_id={self._ads_id}&open_tabs=1"
                    log.info(f'使用 AdsPower API 启动浏览器: {open_url}')
                    resp = requests.get(open_url).json()
                    log.info(f'开启浏览器结果={resp}')
                    if resp["code"] != 0:
                        if resp['code'] == 'ETIMEDOUT':
                            msg = resp["message"]
                            log.error(msg)
                        else:
                            msg = resp['msg']
                            log.error(msg)
                        tools.send_message_to_ui(ms=self.ms, ui=self.ui,
                                                message=f'获取远程浏览器{self._ads_id}启动参数 | 失败 | {msg} | 再次尝试！')
                        if self.retry_times < 3:
                            self.retry_times += 1
                            return self.get_remote_driver()
                    else:
                        tools.send_message_to_ui(ms=self.ms, ui=self.ui, message=f'获取远程浏览器{self._ads_id}启动参数 | 成功！')
                        return resp
            except Exception as e:
                log.error(f'启动浏览器异常: {e}')
                tools.send_message_to_ui(ms=self.ms, ui=self.ui,
                                        message=f'获取远程浏览器{self._ads_id}启动参数 | 异常 | {str(e)}')
                if self.retry_times < 3:
                    self.retry_times += 1
                    return self.get_remote_driver()
        return None

    def chrome_driver(self):

        driver = None
        try:
            resp = self.get_remote_driver()
            log.info(resp)
            if resp:
                chrome_driver = resp["data"]["webdriver"]
                chrome_options = Options()
                chrome_options.add_experimental_option("debuggerAddress", resp["data"]["ws"]["selenium"])

                s = NoConsoleService(chrome_driver)
                # s=Service(chrome_driver)
                log.info('连接并开启浏览器中。。。')
                tools.send_message_to_ui(ms=self.ms, ui=self.ui,
                                         message=f'连接并开启远程[{resp["data"]["ws"]["selenium"]}]浏览器中...')
                try_times = 0
                while try_times < 2:  # 连接远程浏览器，尝试2次之后就直接放弃
                    try:
                        if not (self.stop_event and self.stop_event.isSet()):
                            driver = webdriver.Chrome(service=s, options=chrome_options)
                            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                                'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
                            })
                            tools.send_message_to_ui(ms=self.ms, ui=self.ui,
                                                     message=f'开启远程浏览器{self._ads_id} | 成功')
                            break
                        else:
                            break
                    except Exception as e:
                        log.error(e)
                        tools.send_message_to_ui(ms=self.ms, ui=self.ui,
                                                 message=f'开启远程浏览器{self._ads_id} | 失败，再次尝试 | {str(e)}')
                        try_times += 1

                # print(f'_window_size-->{self._window_size}')

                if self._window_size and driver:
                    chrome_para = self._window_size
                    driver.set_window_size(chrome_para[2], chrome_para[3])
                    driver.set_window_position(chrome_para[0], chrome_para[1])
        except Exception as e:
            log.exception(e)
        finally:
            if self.stop_event and self.stop_event.isSet():
                return None
            return driver

    @property
    def cookies(self):
        cookies_json = {}
        for cookie in self.driver.get_cookies():
            cookies_json[cookie["name"]] = cookie["value"]

        return cookies_json

    @cookies.setter
    def cookies(self, val: dict):
        """
        设置cookie
        Args:
            val: {"key":"value", "key2":"value2"}

        Returns:

        """
        for key, value in val.items():
            self.driver.add_cookie({"name": key, "value": value})

    def __getattr__(self, name):
        if self.driver:
            return getattr(self.driver, name)
        else:
            log.error(f'attribute name={name} | driver None')
            return None


@Singleton
class WebDriverPool:
    def __init__(self, **kwargs):
        self.queue = {}
        self.kwargs = kwargs
        self.lock = threading.RLock()
        self.driver_count = 0
        self.queue_chrome = {}  # 给每个chrome浏览器配置位置和大小
        self.queue_size_param = MemoryDB()
        self.queue_expried_ads = []
        self.queue_drop_res = {}
        
        # Check browser type and get appropriate service URL
        self.browser_type = getattr(config, 'browser_type', 'adspower') if hasattr(config, 'browser_type') else 'adspower'
        if self.browser_type == 'bitbrowser':
            self.service_url = bitbrowser_api.get_bitbrowser_url()
        else:
            self.service_url = ads_api.start_service()  # 开启ads power global 进程

    def get_size(self, ads_id, driver_count):
        if ads_id in self.queue_chrome:
            return self.queue_chrome[ads_id]
        if self.queue_size_param.empty():
            x = 1
            y = 1
            if driver_count == 1:
                # 默认只设置大小为1024*800
                self.queue_chrome[ads_id] = [x, y, 1024, 800]
            else:
                long = 1024
                high = 800
                reslution_x = 1920
                self.queue_size_param.add([x, y, long, high])
                for i in range(driver_count):
                    if (x + long / 8 >= reslution_x):
                        y = y + high
                        x = 1
                    else:
                        x = x + long / 8
                        y += 50
                        self.queue_size_param.add([x, y, long, high])

                self.queue_chrome[ads_id] = self.queue_size_param.get()
        else:
            self.queue_chrome[ads_id] = self.queue_size_param.get()

        return self.queue_chrome[ads_id]

    def get_index(self, ads_id):
        if ads_id in self.queue:
            return list(self.queue.keys()).index(ads_id)
        else:
            return -1

    def get(self, ads_id, ms=None, ui=None, stop_event=None) -> WebDriver:
        with self.lock:
            # 如果已经存在就直接访问，返回
            if ads_id in self.queue:
                log.info(f'5、线程{threading.current_thread().name}下浏览器{ads_id}直接返回，无需再创建')
                return self.queue[ads_id]

            kwargs = self.kwargs.copy()
            if ads_id:
                kwargs["ads_id"] = ads_id
            if self.service_url:
                kwargs["service_url"] = self.service_url
            if 'driver_count' in kwargs:
                driver_count = kwargs['driver_count']
                window_size = self.get_size(ads_id, driver_count)
                kwargs["window_size"] = window_size

            if stop_event:
                kwargs["stop_event"] = stop_event

            if ms:
                kwargs["ms"] = ms

            if ui:
                kwargs["ui"] = ui

            log.info(f'5、线程{threading.current_thread().name}下浏览器{ads_id}正在被创建')
            tools.send_message_to_ui(ms=ms, ui=ui, message=f'浏览器{ads_id}正在被创建')
            driver = WebDriver(**kwargs)
            # driver=[]
            self.queue[ads_id] = driver
            self.driver_count += 1

        driver = self.queue[ads_id]
        return driver

    def exists(self, ads_id):
        return ads_id in self.queue

    def expried(self, ads_id):
        return ads_id in self.queue_expried_ads

    def get_drop_res(self, ads_id):
        with self.lock:
            if ads_id and ads_id in self.queue_drop_res:
                res_list = self.queue_drop_res[ads_id]
                if len(res_list) > 0:
                    res = res_list.pop(-1)
                    return res
                    # self.queue_drop_res[ads_id]=res_list

            return None

    def add_drop_res(self, res):
        with self.lock:
            ads_id = res.ads_id
            if ads_id and res:
                if ads_id not in self.queue_drop_res:
                    self.queue_drop_res[ads_id] = []

                if res not in self.queue_drop_res[ads_id]:
                    self.queue_drop_res[ads_id].append(res)

            log.info(self.queue_drop_res)

    def remove(self, ads_id, pre_remove=None):
        with self.lock:  # 防止线程多次并发
            if callable(pre_remove):
                pre_remove(ads_id)

            if ads_id in self.queue.keys():
                driver = self.queue.pop(ads_id)

                if driver.get_driver():
                    driver.quit()

                # Close browser via appropriate API
                browser_type = getattr(config, 'browser_type', 'adspower') if hasattr(config, 'browser_type') else 'adspower'
                
                close_times = 0
                while close_times < 2:
                    try:
                        if browser_type == 'bitbrowser':
                            # BitBrowser uses POST with JSON body
                            result = bitbrowser_api.stop_browser(ads_id)
                            if result:
                                break
                            else:
                                close_times += 1
                                tools.delay_time(2)
                                log.info(f'close BitBrowser browser_id: {ads_id}')
                        else:
                            # AdsPower uses GET
                            close_url = f"{self.service_url}/api/v1/browser/stop?user_id={ads_id}"
                            res = requests.get(close_url).json()
                            if 'code' in res and res['code'] == 0:
                                break
                            else:
                                close_times += 1
                                tools.delay_time(2)
                                log.info('close ads_id:' + ads_id + '|' + json.dumps(res))
                    except Exception as e:
                        close_times += 1
                        log.error(e)
                        tools.delay_time(2)

                self.driver_count -= 1

    def close(self):
        for _key in list(self.queue):
            driver = self.queue.pop(_key)
            close_url = f"{self.service_url}/api/v1/browser/stop?user_id={_key}"
            try:
                driver.quit()
            except Exception as e:
                log.error(e)

            close_times = 0
            while close_times < 2:
                try:
                    res = requests.get(close_url).json()
                    if 'code' in res and res['code'] == 0:
                        break
                    else:
                        close_times += 1
                        tools.delay_time(2)

                    log.info('close ads_id:' + _key + '|' + json.dumps(res))
                except Exception as e:
                    log.error(e)
                    close_times += 1
                    tools.delay_time(2)

            self.driver_count -= 1
            tools.delay_time(2)
