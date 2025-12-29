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
    # Compatibility fix for newer Selenium versions
    start_error_message = "Please check that the chromedriver is installed and in PATH."
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure log_file attribute exists for compatibility
        if not hasattr(self, 'log_file') or self.log_file is None:
            self.log_file = PIPE
    
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
            error_msg = getattr(self, 'start_error_message', 'Check chromedriver installation.')
            if err.errno == errno.ENOENT:
                raise WebDriverException(
                    "'%s' executable needs to be in PATH. %s" % (
                        os.path.basename(self.path), error_msg)
                )
            elif err.errno == errno.EACCES:
                raise WebDriverException(
                    "'%s' executable may have wrong permissions. %s" % (
                        os.path.basename(self.path), error_msg)
                )
            else:
                raise
        except Exception as e:
            error_msg = getattr(self, 'start_error_message', 'Check chromedriver installation.')
            raise WebDriverException(
                "The executable %s needs to be available in the path. %s\n%s" %
                (os.path.basename(self.path), error_msg, str(e)))
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
        self._ads_id = ads_id
        self.retry_times = 0
        self.stop_event = stop_event
        self.ms = ms
        self.ui = ui

        # Auto-detect service URL based on browser type if not provided
        if service_url:
            self._service_url = service_url
        else:
            browser_type = getattr(config, 'browser_type', 'adspower')
            if browser_type == 'bitbrowser':
                port = getattr(config, 'bitbrowser_port', '54345')
                self._service_url = f"http://127.0.0.1:{port}"
            else:
                # Get AdsPower service URL
                self._service_url = ads_api.start_service()

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
        
        # Get proxy from IP pool if enabled
        proxy_config = None
        try:
            from autoads.ip_pool import ip_pool
            if ip_pool.is_enabled():
                proxy_config = ip_pool.get_proxy_for_browser(self._ads_id)
                if proxy_config:
                    log.info(f'使用代理 IP: {proxy_config.get("proxy_host")}:{proxy_config.get("proxy_port")}')
                    tools.send_message_to_ui(ms=self.ms, ui=self.ui, 
                        message=f'使用代理: {proxy_config.get("proxy_host")}:{proxy_config.get("proxy_port")}')
        except Exception as e:
            log.warning(f'IP Pool error: {e}')
        
        if not (self.stop_event and self.stop_event.isSet()):
            try:
                if browser_type == 'bitbrowser':
                    # BitBrowser uses POST with JSON body
                    log.info(f'使用 BitBrowser API 启动浏览器 {self._ads_id}')
                    result = bitbrowser_api.start_browser(self._ads_id, proxy_config=proxy_config)
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
                chrome_driver_path = resp["data"]["webdriver"]
                debugger_address = resp["data"]["ws"]["selenium"]
                
                chrome_options = Options()
                chrome_options.add_experimental_option("debuggerAddress", debugger_address)

                log.info(f'连接并开启浏览器中... driver={chrome_driver_path}, debugger={debugger_address}')
                tools.send_message_to_ui(ms=self.ms, ui=self.ui,
                                         message=f'连接并开启远程[{debugger_address}]浏览器中...')
                
                try_times = 0
                while try_times < 2:  # 连接远程浏览器，尝试2次之后就直接放弃
                    try:
                        if not (self.stop_event and self.stop_event.isSet()):
                            # Try NoConsoleService first, fall back to regular Service
                            try:
                                s = NoConsoleService(chrome_driver_path)
                                driver = webdriver.Chrome(service=s, options=chrome_options)
                            except Exception as service_err:
                                log.warning(f'NoConsoleService failed, trying regular Service: {service_err}')
                                s = Service(chrome_driver_path)
                                driver = webdriver.Chrome(service=s, options=chrome_options)
                            
                            # Hide webdriver detection
                            try:
                                driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                                    'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
                                })
                            except:
                                pass  # Not critical if this fails
                            
                            tools.send_message_to_ui(ms=self.ms, ui=self.ui,
                                                     message=f'开启远程浏览器{self._ads_id} | 成功')
                            log.info(f'成功连接到浏览器 {self._ads_id}')
                            break
                        else:
                            break
                    except Exception as e:
                        log.error(f'连接浏览器失败: {e}')
                        tools.send_message_to_ui(ms=self.ms, ui=self.ui,
                                                 message=f'开启远程浏览器{self._ads_id} | 失败，再次尝试 | {str(e)}')
                        try_times += 1
                        time.sleep(1)  # Wait before retry

                # print(f'_window_size-->{self._window_size}')

                if self._window_size and driver:
                    chrome_para = self._window_size
                    driver.set_window_size(chrome_para[2], chrome_para[3])
                    driver.set_window_position(chrome_para[0], chrome_para[1])
                
                # Auto-login using saved cookies if available
                if driver:
                    try:
                        from autoads.auto_login import auto_login
                        # Try to auto-login with cookie for this browser
                        if auto_login.auto_login_with_cookie(driver, self._ads_id):
                            log.info(f"✅ 浏览器 {self._ads_id} Cookie自动登录成功")
                            tools.send_message_to_ui(ms=self.ms, ui=self.ui,
                                message=f'Cookie自动登录成功 ✓')
                            
                            # Handle 2FA if needed
                            if auto_login.handle_2fa_if_needed(driver, self._ads_id):
                                log.info(f"✅ 浏览器 {self._ads_id} 2FA验证通过")
                    except Exception as e:
                        log.debug(f"Auto-login check skipped: {e}")
                        # Not critical - user may login manually
                        
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
        """
        自动排列浏览器窗口 - Auto-arrange browser windows in grid layout
        
        For 1 browser: Full width
        For 2 browsers: Side by side
        For 4 browsers: 2x2 grid
        For 8 browsers: 4x2 grid
        
        Args:
            ads_id: Browser ID
            driver_count: Total number of browsers
        
        Returns:
            [x, y, width, height] - Window position and size
        """
        if ads_id in self.queue_chrome:
            return self.queue_chrome[ads_id]
        
        # Get screen resolution from config or use defaults
        try:
            screen_width = int(getattr(config, 'screen_width', 1920))
            screen_height = int(getattr(config, 'screen_height', 1080))
        except:
            screen_width = 1920
            screen_height = 1080
        
        # Calculate grid layout based on driver count
        if driver_count == 1:
            cols, rows = 1, 1
        elif driver_count == 2:
            cols, rows = 2, 1
        elif driver_count <= 4:
            cols, rows = 2, 2
        elif driver_count <= 6:
            cols, rows = 3, 2
        elif driver_count <= 8:
            cols, rows = 4, 2
        elif driver_count <= 9:
            cols, rows = 3, 3
        elif driver_count <= 12:
            cols, rows = 4, 3
        else:
            # For more than 12, calculate best fit
            cols = min(int(driver_count ** 0.5) + 1, 6)
            rows = (driver_count + cols - 1) // cols
        
        # Calculate window size
        window_width = screen_width // cols
        window_height = (screen_height - 50) // rows  # Leave space for taskbar
        
        # Generate positions if not already done
        if self.queue_size_param.empty():
            for row in range(rows):
                for col in range(cols):
                    x = col * window_width
                    y = row * window_height
                    self.queue_size_param.add([x, y, window_width, window_height])
        
        # Get position for this browser
        if not self.queue_size_param.empty():
            self.queue_chrome[ads_id] = self.queue_size_param.get()
        else:
            # Fallback: default position
            self.queue_chrome[ads_id] = [1, 1, 1024, 800]
        
        log.info(f"Browser {ads_id} positioned at {self.queue_chrome[ads_id]}")
        return self.queue_chrome[ads_id]

    def get_index(self, ads_id):
        if ads_id in self.queue:
            return list(self.queue.keys()).index(ads_id)
        else:
            return -1

    def reset_window_positions(self):
        """Reset window position cache for new spider run"""
        self.queue_chrome = {}
        self.queue_size_param = MemoryDB()
        log.info("Browser window position cache cleared")

    def get(self, ads_id, ms=None, ui=None, stop_event=None, driver_count=None) -> WebDriver:
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
            
            # 窗口自动排列 - 使用传入的driver_count或kwargs中的
            actual_driver_count = driver_count or kwargs.get('driver_count')
            if actual_driver_count:
                window_size = self.get_size(ads_id, actual_driver_count)
                kwargs["window_size"] = window_size
                log.info(f"🪟 窗口自动排列: 浏览器 {ads_id} 位置 {window_size} (共{actual_driver_count}个浏览器)")

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

    def remove(self, ads_id, pre_remove=None, force_close=False):
        """
        Remove browser from pool
        
        Args:
            ads_id: Browser ID
            pre_remove: Callback before removal
            force_close: If True, always close browser. If False, check config.
        """
        with self.lock:  # 防止线程多次并发
            if callable(pre_remove):
                pre_remove(ads_id)

            if ads_id in self.queue.keys():
                driver = self.queue.pop(ads_id)

                # Check if we should keep browser open
                keep_browser_open = getattr(config, 'keep_browser_open', True)
                
                if force_close or not keep_browser_open:
                    # Close the browser
                    if driver.get_driver():
                        try:
                            driver.quit()
                        except Exception as e:
                            log.debug(f"Error quitting driver: {e}")

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
                    
                    log.info(f'Browser {ads_id} closed')
                else:
                    # Just disconnect WebDriver but keep browser open
                    if driver.get_driver():
                        try:
                            # Detach from browser without closing
                            driver.get_driver().quit()
                        except Exception as e:
                            log.debug(f"Error detaching driver: {e}")
                    
                    log.info(f'Browser {ads_id} kept open (disconnected from WebDriver)')

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
                    response = requests.get(close_url, timeout=10)
                    # Handle empty or non-JSON responses
                    if response.text.strip():
                        try:
                            res = response.json()
                            if 'code' in res and res['code'] == 0:
                                log.info(f'close ads_id: {_key} | success')
                                break
                            else:
                                close_times += 1
                                log.info('close ads_id:' + _key + '|' + json.dumps(res))
                        except json.JSONDecodeError:
                            log.debug(f'close ads_id: {_key} | response not JSON: {response.text[:100]}')
                            close_times += 1
                    else:
                        log.debug(f'close ads_id: {_key} | empty response')
                        close_times += 1
                    tools.delay_time(2)
                except requests.exceptions.RequestException as e:
                    log.debug(f'close ads_id: {_key} | request error: {e}')
                    close_times += 1
                    tools.delay_time(2)
                except Exception as e:
                    log.error(f'close ads_id: {_key} | unexpected error: {e}')
                    close_times += 1
                    tools.delay_time(2)

            self.driver_count -= 1
            tools.delay_time(2)
