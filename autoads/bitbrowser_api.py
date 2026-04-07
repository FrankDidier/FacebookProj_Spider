#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BitBrowser API - 比特浏览器 API 适配器
BitBrowser 使用本地服务模式，需要用户登录

注意: 免费用户 API 调用频率不超过 2次/秒
"""
import os
import time
import requests
import json
from autoads.log import log
from autoads.config import config

# Rate limiting for free users (max 2 requests per second)
_last_request_time = 0
_request_interval = 0.6  # seconds between requests


def _rate_limit():
    """Enforce rate limiting to avoid 'Frequent requests' error"""
    global _last_request_time
    now = time.time()
    elapsed = now - _last_request_time
    if elapsed < _request_interval:
        time.sleep(_request_interval - elapsed)
    _last_request_time = time.time()


def get_bitbrowser_url():
    """获取 BitBrowser API URL"""
    port = getattr(config, 'bitbrowser_port', '54345') if hasattr(config, 'bitbrowser_port') else '54345'
    custom_url = getattr(config, 'bitbrowser_api_url', '') if hasattr(config, 'bitbrowser_api_url') else ''
    
    if custom_url:
        return custom_url
    return f'http://127.0.0.1:{port}'


def test_connection():
    """测试 BitBrowser 连接 - 使用 POST /health 端点"""
    try:
        base_url = get_bitbrowser_url()
        headers = {"Content-Type": "application/json"}
        
        # 使用 /health 端点测试连接
        try:
            response = requests.post(f"{base_url}/health", headers=headers, json={}, timeout=3)
            if response.status_code == 200:
                data = response.json()
                if data.get('success') == True:
                    log.info(f"BitBrowser 服务运行正常: {base_url}")
                    return True
        except:
            pass
        
        # 备用方案：尝试 GET 请求
        try:
            response = requests.get(f"{base_url}/", timeout=2)
            if response.status_code == 200:
                log.info(f"BitBrowser 服务可访问: {base_url}")
                return True
        except:
            pass
        
        log.warning(f"BitBrowser 服务未检测到: {base_url}")
        return False
    except Exception as e:
        log.error(f"测试 BitBrowser 连接失败: {e}")
        return False


def check_login_status():
    """检查用户是否已登录 BitBrowser"""
    try:
        _rate_limit()  # Avoid rate limiting
        base_url = get_bitbrowser_url()
        headers = {"Content-Type": "application/json"}
        
        # 使用正确的参数格式尝试获取浏览器列表 (BitBrowser uses 0-based pages)
        body = {"page": 0, "pageSize": 10}
        
        response = requests.post(f"{base_url}/browser/list", headers=headers, json=body, timeout=3)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') == True:
                return True, "已登录"
            
            msg = str(data.get('msg', ''))
            # 检查是否是 token/登录相关错误
            if 'token' in msg.lower() or '登录' in msg or 'login' in msg.lower():
                return False, "请先登录 BitBrowser"
            # 其他错误可能表示服务正常但配置问题
            return False, msg if msg else "未知错误"
        return False, f"HTTP 错误: {response.status_code}"
    except Exception as e:
        log.error(f"检查 BitBrowser 登录状态失败: {e}")
        return False, str(e)


def get_browser_list(page=0, page_size=200):
    """获取浏览器列表 - 需要用户已登录 BitBrowser
    
    Args:
        page: 页码，从0开始
        page_size: 每页大小，默认200以支持30-50+浏览器
    
    Returns:
        list: 浏览器列表，如果未登录或失败返回空列表
    """
    try:
        _rate_limit()  # Avoid rate limiting
        base_url = get_bitbrowser_url()
        headers = {"Content-Type": "application/json"}
        
        # BitBrowser 使用 POST 请求，JSON body 格式
        # 确保参数是整数类型 - 支持50+浏览器
        body = {
            "page": int(page),
            "pageSize": int(page_size)
        }
        
        # 主要端点
        endpoints = ['/browser/list', '/api/browser/list', '/api/v1/browser/list']
        
        for endpoint in endpoints:
            try:
                response = requests.post(f"{base_url}{endpoint}", headers=headers, json=body, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # 检查是否需要登录
                    if data.get('success') == False:
                        msg = str(data.get('msg', ''))
                        if 'token' in msg.lower() or '登录' in msg or 'login' in msg.lower():
                            log.warning(f"BitBrowser 需要登录: {msg}")
                            return []
                        log.warning(f"BitBrowser API 错误: {msg}")
                        continue
                    
                    # 成功获取列表
                    if data.get('success') == True:
                        browsers = []
                        if 'data' in data:
                            if isinstance(data['data'], dict) and 'list' in data['data']:
                                browsers = data['data']['list']
                            elif isinstance(data['data'], list):
                                browsers = data['data']
                        elif 'list' in data:
                            browsers = data['list']
                        
                        log.info(f"获取到 {len(browsers)} 个 BitBrowser 浏览器")
                        return browsers
                        
            except Exception as e:
                log.debug(f"尝试 {endpoint} 失败: {e}")
                continue
        
        log.warning("未能获取 BitBrowser 浏览器列表，请确保已登录 BitBrowser")
        return []
    except Exception as e:
        log.error(f"获取 BitBrowser 浏览器列表失败: {e}")
        return []


def update_browser_proxy(browser_id, proxy_config):
    """
    更新浏览器的代理配置
    
    BitBrowser API 需要完整的浏览器配置包括 browserFingerPrint
    """
    try:
        _rate_limit()
        base_url = get_bitbrowser_url()
        
        # 转换代理配置格式
        proxy_type = proxy_config.get('proxy_type', 'http')
        host = proxy_config.get('proxy_host', '')
        port = proxy_config.get('proxy_port', '')
        username = proxy_config.get('proxy_user', '')
        password = proxy_config.get('proxy_password', '')
        
        if not host or not port:
            log.warning(f"代理配置不完整: host={host}, port={port}")
            return False
        
        headers = {"Content-Type": "application/json"}
        
        # 方法1: 获取浏览器详情，然后使用完整配置更新
        browser_detail = get_browser_detail(browser_id)
        if browser_detail:
            log.info(f"获取到浏览器详情，尝试使用完整配置更新代理")
            
            # 构建更新请求，包含 browserFingerPrint
            update_body = {
                "id": browser_id,
                "proxyMethod": 2,  # 2 = 自定义代理
                "proxyType": proxy_type,
                "host": host,
                "port": str(port),
                "proxyUserName": username or "",
                "proxyPassword": password or ""
            }
            
            # 添加 browserFingerPrint (这是 BitBrowser 要求的必填字段)
            if 'browserFingerPrint' in browser_detail:
                update_body['browserFingerPrint'] = browser_detail['browserFingerPrint']
            elif 'fingerprint' in browser_detail:
                update_body['browserFingerPrint'] = browser_detail['fingerprint']
            
            # 复制其他必要字段
            for key in ['name', 'remark', 'groupId', 'seq']:
                if key in browser_detail:
                    update_body[key] = browser_detail[key]
            
            try:
                response = requests.post(f"{base_url}/browser/update", headers=headers, json=update_body, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        log.info(f"✅ BitBrowser 代理更新成功: {browser_id} -> {host}:{port}")
                        return True
                    else:
                        log.debug(f"BitBrowser /browser/update 返回: {data}")
            except Exception as e:
                log.debug(f"BitBrowser /browser/update 失败: {e}")
        
        # 方法2: 尝试 partial update (批量更新)
        _rate_limit()
        try:
            partial_body = {
                "ids": [browser_id],
                "proxyMethod": 2,
                "proxyType": proxy_type,
                "host": host,
                "port": str(port),
                "proxyUserName": username or "",
                "proxyPassword": password or ""
            }
            response = requests.post(f"{base_url}/browser/update/partial", headers=headers, json=partial_body, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    log.info(f"✅ BitBrowser 代理批量更新成功: {browser_id} -> {host}:{port}")
                    return True
                else:
                    log.debug(f"BitBrowser /browser/update/partial 返回: {data}")
        except Exception as e:
            log.debug(f"BitBrowser /browser/update/partial 失败: {e}")
        
        # 方法3: 将代理参数存储，在启动时通过命令行参数传递
        # 这是最可靠的备选方案
        log.warning(f"⚠️ BitBrowser 代理API更新失败，将在启动时通过命令行参数传递代理")
        return "use_args"  # 特殊返回值，表示需要在启动时使用 args
        
    except Exception as e:
        log.error(f"更新 BitBrowser 代理失败: {e}")
        return False


def _bitbrowser_msg_means_still_opening(msg):
    """BitBrowser often returns success=false while the profile is launching."""
    if not msg:
        return False
    s = str(msg)
    if "正在打开" in s or "打开中" in s:
        return True
    low = s.lower()
    return "opening" in low or "still starting" in low or "please wait" in low


def start_browser(browser_id, proxy_config=None):
    """启动浏览器
    Args:
        browser_id: 浏览器 ID
        proxy_config: 代理配置 (可选)
            {
                "proxy_type": "http",
                "proxy_host": "xxx.xxx.xxx.xxx",
                "proxy_port": "8080",
                "proxy_user": "username",
                "proxy_password": "password"
            }
    """
    try:
        base_url = get_bitbrowser_url()
        # Primary API for current BitBrowser builds (others often 404 — do not treat as fatal)
        primary_endpoint = "/browser/open"
        fallback_endpoints = [
            "/browser/start",
            "/api/browser/open",
            "/api/v1/browser/open",
        ]

        headers = {
            "Content-Type": "application/json"
        }

        body = {
            "id": browser_id
        }

        use_proxy_args = False

        # 如果有代理配置，转换为 BitBrowser 格式并更新浏览器配置
        if proxy_config:
            # 首先尝试更新浏览器的代理配置
            proxy_updated = update_browser_proxy(browser_id, proxy_config)
            if proxy_updated == True:
                log.info(f"✅ 代理配置已更新到浏览器 {browser_id}")
            elif proxy_updated == "use_args":
                # API 更新失败，使用命令行参数
                use_proxy_args = True
                log.info(f"💡 将通过命令行参数传递代理配置")
            else:
                log.warning(f"⚠️ 代理配置更新失败，继续尝试启动浏览器")

        # 如果需要通过命令行参数传递代理
        if use_proxy_args and proxy_config:
            proxy_type = proxy_config.get('proxy_type', 'http')
            host = proxy_config.get('proxy_host', '')
            port = proxy_config.get('proxy_port', '')
            username = proxy_config.get('proxy_user', '')
            password = proxy_config.get('proxy_password', '')

            if host and port:
                # 构建代理命令行参数
                if username and password:
                    # 带认证的代理需要使用扩展或其他方式，这里使用基本格式
                    proxy_arg = f"--proxy-server={proxy_type}://{host}:{port}"
                else:
                    proxy_arg = f"--proxy-server={proxy_type}://{host}:{port}"

                body["args"] = [proxy_arg]
                body["loadExtensions"] = False
                log.info(f"📡 添加代理命令行参数: {proxy_arg}")

        # Poll /browser/open: API returns success=false +「浏览器正在打开中」while launching — must wait, not switch endpoints.
        max_open_wait_rounds = 90
        poll_interval = 2.0
        open_request_timeout = 90

        for attempt in range(max_open_wait_rounds):
            try:
                _rate_limit()
                url = f"{base_url}{primary_endpoint}"
                if attempt == 0 or attempt % 10 == 9:
                    log.info(f"尝试 BitBrowser API: {url} (轮询 {attempt + 1}/{max_open_wait_rounds})")
                response = requests.post(
                    url, headers=headers, json=body, timeout=open_request_timeout
                )
                if attempt == 0 or attempt % 10 == 9:
                    log.info(f"BitBrowser API 响应状态: {response.status_code}")
                if response.status_code != 200:
                    break
                data = response.json()
                if attempt == 0 or data.get("success") or attempt % 10 == 9:
                    log.info(f"BitBrowser 启动响应: {data}")
                if data.get("success"):
                    log.info(f"✅ BitBrowser 启动成功: {browser_id}")
                    if use_proxy_args:
                        log.info(f"   代理已通过命令行参数应用")
                    return data
                msg = data.get("msg", "") or data.get("message", "")
                if _bitbrowser_msg_means_still_opening(msg):
                    log.debug(
                        f"BitBrowser 忙「{msg}」，{poll_interval:.0f}s 后重试 ({attempt + 1}/{max_open_wait_rounds})"
                    )
                    time.sleep(poll_interval)
                    continue
                log.warning(f"BitBrowser 启动返回失败: {msg or 'Unknown'}")
                break
            except requests.exceptions.Timeout:
                log.warning(
                    f"BitBrowser /browser/open 超时（{open_request_timeout}s），"
                    f"{poll_interval:.0f}s 后重试 ({attempt + 1}/{max_open_wait_rounds})"
                )
                time.sleep(poll_interval)
                continue
            except Exception as e:
                log.debug(f"BitBrowser API {primary_endpoint} 失败: {e}")
                time.sleep(poll_interval)
                continue

        # Legacy / alternate installs: only try fallbacks if primary did not succeed
        for endpoint in fallback_endpoints:
            try:
                _rate_limit()
                log.info(f"尝试备用 BitBrowser API: {base_url}{endpoint}")
                response = requests.post(
                    f"{base_url}{endpoint}",
                    headers=headers,
                    json=body,
                    timeout=open_request_timeout,
                )
                log.info(f"BitBrowser API 响应状态: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    log.info(f"BitBrowser 启动响应: {data}")
                    if data.get("success"):
                        log.info(f"✅ BitBrowser 启动成功: {browser_id}")
                        return data
                    msg = data.get("msg", "")
                    if _bitbrowser_msg_means_still_opening(msg):
                        time.sleep(poll_interval)
                        # one more try same fallback
                        continue
            except Exception as e:
                log.debug(f"BitBrowser API 端点 {endpoint} 失败: {e}")
                continue

        log.error(f"BitBrowser 启动失败: {browser_id} - 所有端点都失败")
        return None
    except Exception as e:
        log.error(f"启动 BitBrowser 失败: {e}")
        return None


def stop_browser(browser_id):
    """停止浏览器"""
    try:
        _rate_limit()  # Avoid rate limiting
        base_url = get_bitbrowser_url()
        # BitBrowser uses /browser/close, not /browser/stop
        endpoints = [
            '/browser/close',
            '/browser/stop',
            '/api/browser/close',
            '/api/v1/browser/close'
        ]
        
        headers = {
            "Content-Type": "application/json"
        }
        
        body = {
            "id": browser_id
        }
        
        for endpoint in endpoints:
            try:
                response = requests.post(f"{base_url}{endpoint}", headers=headers, json=body, timeout=10)
                if response.status_code == 200:
                    log.info(f"BitBrowser 停止成功: {browser_id}")
                    return True
            except:
                continue
        
        log.warning(f"BitBrowser 停止失败: {browser_id}")
        return False
    except Exception as e:
        log.error(f"停止 BitBrowser 失败: {e}")
        return False


def get_browser_detail(browser_id):
    """获取单个浏览器的详细信息，包括 browserFingerPrint
    
    这个信息用于更新浏览器配置
    """
    try:
        _rate_limit()
        base_url = get_bitbrowser_url()
        headers = {"Content-Type": "application/json"}
        
        # 尝试多个端点获取浏览器详情
        endpoints = [
            '/browser/detail',
            '/browser/info',
            '/api/browser/detail'
        ]
        
        for endpoint in endpoints:
            try:
                body = {"id": browser_id}
                response = requests.post(f"{base_url}{endpoint}", headers=headers, json=body, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success') and data.get('data'):
                        log.debug(f"获取浏览器详情成功: {browser_id}")
                        return data['data']
            except:
                continue
        
        log.warning(f"无法获取浏览器详情: {browser_id}")
        return None
    except Exception as e:
        log.error(f"获取浏览器详情失败: {e}")
        return None


def get_browser_ids(count=100):
    """获取浏览器 ID 列表"""
    try:
        browsers = get_browser_list()
        if not browsers:
            return []
        
        # 提取 ID 和 user_id
        browser_ids = []
        for browser in browsers[:count]:
            if isinstance(browser, dict):
                browser_id = browser.get('id') or browser.get('browserId') or browser.get('user_id')
                if browser_id:
                    browser_ids.append(browser_id)
        
        return browser_ids
    except Exception as e:
        log.error(f"获取 BitBrowser ID 列表失败: {e}")
        return []


def check_service():
    """检查 BitBrowser 服务是否运行"""
    return test_connection()


def get_full_status():
    """获取 BitBrowser 完整状态
    
    Returns:
        dict: {
            'service_running': bool,
            'logged_in': bool,
            'browser_count': int,
            'message': str
        }
    """
    status = {
        'service_running': False,
        'logged_in': False,
        'browser_count': 0,
        'message': ''
    }
    
    # 检查服务是否运行
    if not test_connection():
        status['message'] = 'BitBrowser 服务未运行，请启动 BitBrowser'
        return status
    
    status['service_running'] = True
    
    # 检查登录状态
    logged_in, login_msg = check_login_status()
    if not logged_in:
        status['message'] = f'BitBrowser 服务运行中，但 {login_msg}'
        return status
    
    status['logged_in'] = True
    
    # 获取浏览器数量
    browsers = get_browser_list()
    status['browser_count'] = len(browsers)
    
    if status['browser_count'] > 0:
        status['message'] = f'BitBrowser 正常运行，已登录，找到 {status["browser_count"]} 个浏览器配置'
    else:
        status['message'] = 'BitBrowser 正常运行，已登录，但未找到浏览器配置，请在 BitBrowser 中添加浏览器'
    
    return status

