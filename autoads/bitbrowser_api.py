#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BitBrowser API - 比特浏览器 API 适配器
BitBrowser 不需要 API 密钥，使用本地 demo 模式
"""
import os
import requests
import json
from autoads.log import log
from autoads.config import config


def get_bitbrowser_url():
    """获取 BitBrowser API URL"""
    port = getattr(config, 'bitbrowser_port', '54345') if hasattr(config, 'bitbrowser_port') else '54345'
    custom_url = getattr(config, 'bitbrowser_api_url', '') if hasattr(config, 'bitbrowser_api_url') else ''
    
    if custom_url:
        return custom_url
    return f'http://127.0.0.1:{port}'


def test_connection():
    """测试 BitBrowser 连接"""
    try:
        base_url = get_bitbrowser_url()
        # Try multiple common endpoints
        endpoints = [
            '/api/v1/browser/list',
            '/api/browser/list',
            '/browser/list',
            '/'
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{base_url}{endpoint}", timeout=2)
                if response.status_code == 200:
                    log.info(f"BitBrowser 连接成功: {base_url}{endpoint}")
                    return True
            except:
                continue
        
        log.warning(f"BitBrowser 连接失败: {base_url}")
        return False
    except Exception as e:
        log.error(f"测试 BitBrowser 连接失败: {e}")
        return False


def get_browser_list():
    """获取浏览器列表 - 不需要 API 密钥"""
    try:
        base_url = get_bitbrowser_url()
        endpoints = [
            '/api/v1/browser/list',
            '/api/browser/list',
            '/browser/list'
        ]
        
        for endpoint in endpoints:
            try:
                # BitBrowser 使用 POST 请求，JSON body 格式
                headers = {
                    "Content-Type": "application/json"
                }
                # 尝试 GET 和 POST
                for method in ['GET', 'POST']:
                    try:
                        if method == 'GET':
                            response = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=5)
                        else:
                            response = requests.post(f"{base_url}{endpoint}", headers=headers, json={}, timeout=5)
                        
                        if response.status_code == 200:
                            data = response.json()
                            # 尝试不同的数据结构
                            browsers = []
                            if isinstance(data, dict):
                                if 'data' in data:
                                    if isinstance(data['data'], dict) and 'list' in data['data']:
                                        browsers = data['data']['list']
                                    elif isinstance(data['data'], list):
                                        browsers = data['data']
                                elif 'list' in data:
                                    browsers = data['list']
                                elif 'rows' in data:
                                    browsers = data['rows']
                            elif isinstance(data, list):
                                browsers = data
                            
                            if browsers:
                                log.info(f"获取到 {len(browsers)} 个 BitBrowser 浏览器")
                                return browsers
                    except:
                        continue
            except:
                continue
        
        log.warning("未能获取 BitBrowser 浏览器列表")
        return []
    except Exception as e:
        log.error(f"获取 BitBrowser 浏览器列表失败: {e}")
        return []


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
        endpoints = [
            '/api/v1/browser/start',
            '/api/browser/start',
            '/browser/start'
        ]
        
        headers = {
            "Content-Type": "application/json"
        }
        
        body = {
            "id": browser_id
        }
        
        # 如果有代理配置，添加到请求中
        if proxy_config:
            body.update(proxy_config)
        
        for endpoint in endpoints:
            try:
                response = requests.post(f"{base_url}{endpoint}", headers=headers, json=body, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    log.info(f"BitBrowser 启动成功: {browser_id}")
                    return data
            except:
                continue
        
        log.error(f"BitBrowser 启动失败: {browser_id}")
        return None
    except Exception as e:
        log.error(f"启动 BitBrowser 失败: {e}")
        return None


def stop_browser(browser_id):
    """停止浏览器"""
    try:
        base_url = get_bitbrowser_url()
        endpoints = [
            '/api/v1/browser/stop',
            '/api/browser/stop',
            '/browser/stop'
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

