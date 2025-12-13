# -*- coding: utf-8 -*-
"""
IP Pool Manager
Manages proxy IPs for browser automation
"""

import random
import threading
import requests
from autoads.log import log
from autoads.config import config


class IPPoolManager:
    """Manages a pool of proxy IPs for browser automation"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._proxies = []
        self._current_index = 0
        self._browser_proxy_map = {}  # Maps browser_id to proxy
        self._proxy_request_count = {}  # Track requests per proxy
        self._failed_proxies = set()  # Track failed proxies
        self._lock = threading.Lock()
        
        self.reload_proxies()
    
    def reload_proxies(self):
        """Reload proxy list from config"""
        with self._lock:
            self._proxies = config.ip_pool_proxies
            self._failed_proxies.clear()
            log.info(f"IP Pool loaded {len(self._proxies)} proxies")
    
    def is_enabled(self):
        """Check if IP pool is enabled"""
        return config.ip_pool_enabled and len(self._proxies) > 0
    
    def parse_proxy(self, proxy_str):
        """
        Parse proxy string to config dict
        Formats: 
        - host:port
        - host:port:user:password
        - http://host:port
        - http://user:pass@host:port
        - socks5://host:port
        - socks5://user:pass@host:port
        """
        proxy_str = proxy_str.strip()
        
        # Determine proxy type from URL scheme
        proxy_type = 'http'
        if proxy_str.startswith('socks5://'):
            proxy_type = 'socks5'
            proxy_str = proxy_str[9:]  # Remove 'socks5://'
        elif proxy_str.startswith('socks4://'):
            proxy_type = 'socks4'
            proxy_str = proxy_str[9:]
        elif proxy_str.startswith('http://'):
            proxy_type = 'http'
            proxy_str = proxy_str[7:]  # Remove 'http://'
        elif proxy_str.startswith('https://'):
            proxy_type = 'https'
            proxy_str = proxy_str[8:]
        
        result = {"proxy_type": proxy_type}
        
        # Check for user:pass@host:port format
        if '@' in proxy_str:
            auth_part, host_part = proxy_str.rsplit('@', 1)
            if ':' in auth_part:
                result["proxy_user"], result["proxy_password"] = auth_part.split(':', 1)
            else:
                result["proxy_user"] = auth_part
            proxy_str = host_part
        
        # Parse host:port
        parts = proxy_str.split(':')
        if len(parts) >= 2:
            result["proxy_host"] = parts[0]
            result["proxy_port"] = parts[1]
        elif len(parts) == 1:
            result["proxy_host"] = parts[0]
            result["proxy_port"] = "8080"  # Default port
        else:
            return None
        
        # Legacy format: host:port:user:password
        if len(parts) >= 4 and "proxy_user" not in result:
            result["proxy_user"] = parts[2]
            result["proxy_password"] = parts[3]
        
        return result
    
    def test_proxy(self, proxy_config, timeout=None):
        """Test if a proxy is working"""
        if timeout is None:
            timeout = config.ip_pool_timeout
        
        try:
            proxy_type = proxy_config.get('proxy_type', 'http')
            host = proxy_config.get('proxy_host')
            port = proxy_config.get('proxy_port')
            user = proxy_config.get('proxy_user')
            password = proxy_config.get('proxy_password')
            
            if user and password:
                proxy_url = f"{proxy_type}://{user}:{password}@{host}:{port}"
            else:
                proxy_url = f"{proxy_type}://{host}:{port}"
            
            proxies = {
                'http': proxy_url,
                'https': proxy_url
            }
            
            response = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=timeout)
            if response.status_code == 200:
                log.info(f"Proxy {host}:{port} is working")
                return True
        except Exception as e:
            log.warning(f"Proxy test failed for {proxy_config.get('proxy_host')}:{proxy_config.get('proxy_port')}: {e}")
        
        return False
    
    def get_proxy_for_browser(self, browser_id):
        """Get a proxy for a specific browser"""
        if not self.is_enabled():
            return None
        
        with self._lock:
            mode = config.ip_pool_assignment_mode
            
            # Sticky mode - use same proxy for same browser
            if mode == 'sticky' and browser_id in self._browser_proxy_map:
                proxy_str = self._browser_proxy_map[browser_id]
                if proxy_str not in self._failed_proxies:
                    return self.parse_proxy(proxy_str)
            
            # Get available proxies (not failed)
            available = [p for p in self._proxies if p not in self._failed_proxies]
            if not available:
                log.warning("No available proxies in pool")
                return None
            
            # Select proxy based on mode
            if mode == 'random':
                proxy_str = random.choice(available)
            else:  # round_robin
                self._current_index = self._current_index % len(available)
                proxy_str = available[self._current_index]
                self._current_index += 1
            
            # Store mapping for sticky mode
            self._browser_proxy_map[browser_id] = proxy_str
            
            # Parse and optionally test
            proxy_config = self.parse_proxy(proxy_str)
            
            if config.ip_pool_test_before_use:
                if not self.test_proxy(proxy_config):
                    self._failed_proxies.add(proxy_str)
                    # Try another proxy
                    return self.get_proxy_for_browser(browser_id)
            
            log.info(f"Assigned proxy {proxy_config.get('proxy_host')}:{proxy_config.get('proxy_port')} to browser {browser_id}")
            return proxy_config
    
    def mark_proxy_failed(self, browser_id):
        """Mark the proxy assigned to a browser as failed"""
        with self._lock:
            if browser_id in self._browser_proxy_map:
                proxy_str = self._browser_proxy_map[browser_id]
                self._failed_proxies.add(proxy_str)
                del self._browser_proxy_map[browser_id]
                log.warning(f"Proxy {proxy_str} marked as failed")
    
    def release_proxy(self, browser_id):
        """Release the proxy assigned to a browser"""
        with self._lock:
            if browser_id in self._browser_proxy_map:
                del self._browser_proxy_map[browser_id]
    
    def get_status(self):
        """Get current IP pool status"""
        return {
            'enabled': self.is_enabled(),
            'total_proxies': len(self._proxies),
            'available_proxies': len([p for p in self._proxies if p not in self._failed_proxies]),
            'failed_proxies': len(self._failed_proxies),
            'assigned_browsers': len(self._browser_proxy_map),
            'assignment_mode': config.ip_pool_assignment_mode,
        }
    
    def add_proxy(self, proxy_str):
        """Add a proxy to the pool"""
        with self._lock:
            if proxy_str not in self._proxies:
                self._proxies.append(proxy_str)
                # Update config
                config.set_option('ip_pool', 'proxies', str(self._proxies))
                log.info(f"Added proxy: {proxy_str}")
                return True
        return False
    
    def remove_proxy(self, proxy_str):
        """Remove a proxy from the pool"""
        with self._lock:
            if proxy_str in self._proxies:
                self._proxies.remove(proxy_str)
                self._failed_proxies.discard(proxy_str)
                # Update config
                config.set_option('ip_pool', 'proxies', str(self._proxies))
                log.info(f"Removed proxy: {proxy_str}")
                return True
        return False


# Global instance
ip_pool = IPPoolManager()

