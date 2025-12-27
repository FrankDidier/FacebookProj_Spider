# -*- coding: utf-8 -*-
"""
Auto Login Module - Cookie注入和2FA自动填充
Supports:
- Cookie auto-injection for instant login
- 2FA TOTP code auto-generation
- Account-Browser binding
"""
import json
import time
import threading
from autoads.log import log
from autoads.config import config

# Try to import pyotp for 2FA
try:
    import pyotp
    PYOTP_AVAILABLE = True
except ImportError:
    PYOTP_AVAILABLE = False
    log.warning("pyotp not installed. Run: pip install pyotp")


class AutoLogin:
    """
    自动登录助手 - Auto Login Helper
    
    Features:
    - Cookie injection for Facebook login
    - 2FA TOTP code generation
    - Account-Browser binding management
    """
    
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
        self._browser_account_map = {}  # Maps browser_id to account
        self._lock = threading.Lock()
    
    # ==================== Cookie Methods ====================
    
    def inject_cookies(self, browser, cookie_string, domain='facebook.com'):
        """
        注入Cookie到浏览器 - Inject cookies into browser
        
        Args:
            browser: Selenium WebDriver instance
            cookie_string: Cookie string (JSON format or Netscape format)
            domain: Cookie domain (default: facebook.com)
        
        Returns:
            bool: True if successful
        """
        if not browser or not cookie_string:
            return False
        
        try:
            cookies = self._parse_cookies(cookie_string)
            if not cookies:
                log.warning("No cookies parsed from string")
                return False
            
            # First navigate to the domain
            current_url = browser.current_url
            if domain not in current_url:
                browser.get(f'https://{domain}/')
                time.sleep(2)
            
            # Delete existing cookies
            browser.delete_all_cookies()
            
            # Inject each cookie
            injected_count = 0
            for cookie in cookies:
                try:
                    # Ensure required fields
                    if 'name' not in cookie or 'value' not in cookie:
                        continue
                    
                    # Clean up cookie dict for Selenium
                    clean_cookie = {
                        'name': cookie['name'],
                        'value': cookie['value'],
                        'domain': cookie.get('domain', f'.{domain}'),
                        'path': cookie.get('path', '/'),
                    }
                    
                    # Add optional fields if present
                    if 'secure' in cookie:
                        clean_cookie['secure'] = cookie['secure']
                    if 'httpOnly' in cookie:
                        clean_cookie['httpOnly'] = cookie['httpOnly']
                    
                    browser.add_cookie(clean_cookie)
                    injected_count += 1
                except Exception as e:
                    log.debug(f"Cookie injection error for {cookie.get('name', 'unknown')}: {e}")
            
            log.info(f"Injected {injected_count}/{len(cookies)} cookies for {domain}")
            
            # Refresh to apply cookies
            browser.refresh()
            time.sleep(2)
            
            return injected_count > 0
            
        except Exception as e:
            log.error(f"Cookie injection failed: {e}")
            return False
    
    def _parse_cookies(self, cookie_string):
        """
        解析Cookie字符串 - Parse cookie string
        
        Supports:
        - JSON array format: [{"name": "c_user", "value": "xxx"}, ...]
        - Netscape/Header format: name1=value1; name2=value2
        - Base64 encoded JSON
        """
        if not cookie_string:
            return []
        
        cookie_string = cookie_string.strip()
        
        # Try JSON format first
        if cookie_string.startswith('[') or cookie_string.startswith('{'):
            try:
                parsed = json.loads(cookie_string)
                if isinstance(parsed, list):
                    return parsed
                elif isinstance(parsed, dict):
                    return [parsed]
            except json.JSONDecodeError:
                pass
        
        # Try Base64 encoded JSON
        try:
            import base64
            decoded = base64.b64decode(cookie_string).decode('utf-8')
            parsed = json.loads(decoded)
            if isinstance(parsed, list):
                return parsed
        except:
            pass
        
        # Try header format: name1=value1; name2=value2
        if '=' in cookie_string:
            cookies = []
            parts = cookie_string.split(';')
            for part in parts:
                part = part.strip()
                if '=' in part:
                    name, value = part.split('=', 1)
                    cookies.append({
                        'name': name.strip(),
                        'value': value.strip()
                    })
            return cookies
        
        return []
    
    def extract_cookies(self, browser):
        """
        从浏览器提取Cookie - Extract cookies from browser
        
        Returns:
            str: JSON formatted cookie string
        """
        if not browser:
            return ''
        
        try:
            cookies = browser.get_cookies()
            return json.dumps(cookies, ensure_ascii=False)
        except Exception as e:
            log.error(f"Cookie extraction failed: {e}")
            return ''
    
    def is_logged_in(self, browser):
        """
        检查是否已登录Facebook - Check if logged into Facebook
        
        Returns:
            bool: True if logged in
        """
        if not browser:
            return False
        
        try:
            current_url = browser.current_url.lower()
            
            # Check for login/checkpoint pages
            if 'login' in current_url or 'checkpoint' in current_url:
                return False
            
            # Check for c_user cookie (indicates logged in user)
            cookies = browser.get_cookies()
            for cookie in cookies:
                if cookie.get('name') == 'c_user':
                    log.info("Facebook login detected (c_user cookie found)")
                    return True
            
            return False
            
        except Exception as e:
            log.error(f"Login check failed: {e}")
            return False
    
    # ==================== 2FA Methods ====================
    
    def generate_2fa_code(self, two_fa_secret):
        """
        生成2FA验证码 - Generate 2FA TOTP code
        
        Args:
            two_fa_secret: 2FA secret key (base32 encoded)
        
        Returns:
            str: 6-digit TOTP code, or None if failed
        """
        if not PYOTP_AVAILABLE:
            log.error("pyotp not installed. Run: pip install pyotp")
            return None
        
        if not two_fa_secret:
            return None
        
        try:
            # Clean up secret
            secret = two_fa_secret.strip().replace(' ', '').upper()
            
            # Generate TOTP code
            totp = pyotp.TOTP(secret)
            code = totp.now()
            
            log.info(f"Generated 2FA code: {code}")
            return code
            
        except Exception as e:
            log.error(f"2FA code generation failed: {e}")
            return None
    
    def fill_2fa_code(self, browser, two_fa_secret):
        """
        自动填写2FA验证码 - Auto-fill 2FA code
        
        Args:
            browser: Selenium WebDriver
            two_fa_secret: 2FA secret key
        
        Returns:
            bool: True if successful
        """
        code = self.generate_2fa_code(two_fa_secret)
        if not code:
            return False
        
        try:
            # Common 2FA input selectors for Facebook
            input_selectors = [
                "//input[@id='approvals_code']",
                "//input[@name='approvals_code']",
                "//input[@type='text' and contains(@aria-label, 'code')]",
                "//input[@type='tel' and @autocomplete='one-time-code']",
                "//input[@type='text' and @autocomplete='one-time-code']",
                "//input[contains(@placeholder, 'code')]",
                "//input[contains(@placeholder, '验证码')]",
            ]
            
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            for selector in input_selectors:
                try:
                    input_elem = WebDriverWait(browser, 3).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    if input_elem:
                        input_elem.clear()
                        input_elem.send_keys(code)
                        log.info(f"2FA code filled using selector: {selector}")
                        
                        # Try to find and click submit button
                        submit_selectors = [
                            "//button[@type='submit']",
                            "//button[@id='checkpointSubmitButton']",
                            "//button[contains(text(), 'Continue')]",
                            "//button[contains(text(), '继续')]",
                        ]
                        
                        for submit_sel in submit_selectors:
                            try:
                                submit_btn = browser.find_element(By.XPATH, submit_sel)
                                if submit_btn:
                                    submit_btn.click()
                                    log.info("2FA submit button clicked")
                                    time.sleep(3)
                                    return True
                            except:
                                continue
                        
                        return True
                except:
                    continue
            
            log.warning("Could not find 2FA input field")
            return False
            
        except Exception as e:
            log.error(f"2FA auto-fill failed: {e}")
            return False
    
    # ==================== Account-Browser Binding ====================
    
    def bind_account_to_browser(self, browser_id, account):
        """
        绑定账号到浏览器 - Bind account to browser
        
        Args:
            browser_id: Browser ID
            account: Account object or dict
        """
        with self._lock:
            self._browser_account_map[browser_id] = account
            log.info(f"Bound account {getattr(account, 'username', account.get('username', 'unknown'))} to browser {browser_id}")
    
    def get_account_for_browser(self, browser_id):
        """
        获取浏览器绑定的账号 - Get account bound to browser
        
        Returns:
            Account object or None
        """
        with self._lock:
            return self._browser_account_map.get(browser_id)
    
    # Alias for compatibility
    def get_bound_account(self, browser_id):
        """Alias for get_account_for_browser"""
        return self.get_account_for_browser(browser_id)
    
    def unbind_browser(self, browser_id):
        """解除浏览器绑定 - Unbind browser"""
        with self._lock:
            if browser_id in self._browser_account_map:
                del self._browser_account_map[browser_id]
    
    def clear_bindings(self):
        """清除所有绑定 - Clear all bindings"""
        with self._lock:
            self._browser_account_map.clear()
    
    def auto_bind_accounts_to_browsers(self, browser_ids, accounts):
        """
        自动绑定账号到浏览器 - Auto-bind accounts to browsers
        
        Args:
            browser_ids: List of browser IDs
            accounts: List of Account objects
        
        Returns:
            dict: {browser_id: account, ...}
        """
        bindings = {}
        
        # First, use any existing browser_id assignments
        unassigned_browsers = list(browser_ids)
        unassigned_accounts = []
        
        for acc in accounts:
            if hasattr(acc, 'browser_id') and acc.browser_id in unassigned_browsers:
                self.bind_account_to_browser(acc.browser_id, acc)
                bindings[acc.browser_id] = acc
                unassigned_browsers.remove(acc.browser_id)
            else:
                unassigned_accounts.append(acc)
        
        # Then, assign remaining accounts to remaining browsers
        for browser_id, acc in zip(unassigned_browsers, unassigned_accounts):
            self.bind_account_to_browser(browser_id, acc)
            bindings[browser_id] = acc
            
            # Update account's browser_id
            if hasattr(acc, 'browser_id'):
                acc.browser_id = browser_id
        
        log.info(f"Auto-bound {len(bindings)} accounts to browsers")
        return bindings
    
    # ==================== Full Auto-Login Flow ====================
    
    def auto_login_with_cookie(self, browser, browser_id=None):
        """
        使用Cookie自动登录 - Auto login using saved cookie
        
        Args:
            browser: Selenium WebDriver
            browser_id: Optional browser ID to look up account
        
        Returns:
            bool: True if login successful
        """
        account = None
        
        # Get account from binding or account manager
        if browser_id:
            account = self.get_account_for_browser(browser_id)
        
        if not account:
            from autoads.account_manager import account_manager
            if browser_id:
                account = account_manager.get_account_by_browser_id(browser_id)
        
        if not account:
            log.warning(f"No account found for browser {browser_id}")
            return False
        
        # Get cookie from account
        cookie_string = getattr(account, 'cookie', None) or account.get('cookie', '')
        if not cookie_string:
            log.warning(f"No cookie found for account {getattr(account, 'username', 'unknown')}")
            return False
        
        # Inject cookies
        if self.inject_cookies(browser, cookie_string):
            # Check if login successful
            if self.is_logged_in(browser):
                log.info(f"Auto-login successful for {getattr(account, 'username', 'unknown')}")
                return True
            else:
                log.warning("Cookie injection didn't result in login")
        
        return False
    
    def handle_2fa_if_needed(self, browser, browser_id=None):
        """
        检测并处理2FA验证 - Detect and handle 2FA if needed
        
        Args:
            browser: Selenium WebDriver
            browser_id: Optional browser ID to look up account
        
        Returns:
            bool: True if 2FA handled or not needed
        """
        try:
            current_url = browser.current_url.lower()
            
            # Check if on 2FA page
            if 'checkpoint' not in current_url and 'two_factor' not in current_url:
                return True  # No 2FA needed
            
            # Get account
            account = None
            if browser_id:
                account = self.get_account_for_browser(browser_id)
            
            if not account:
                from autoads.account_manager import account_manager
                if browser_id:
                    account = account_manager.get_account_by_browser_id(browser_id)
            
            if not account:
                log.warning("No account found for 2FA handling")
                return False
            
            # Get 2FA secret
            two_fa_secret = getattr(account, 'two_fa', None) or account.get('two_fa', '')
            if not two_fa_secret:
                log.warning("2FA required but no secret configured")
                return False
            
            # Fill 2FA code
            return self.fill_2fa_code(browser, two_fa_secret)
            
        except Exception as e:
            log.error(f"2FA handling failed: {e}")
            return False
    
    def full_auto_login(self, browser, browser_id=None):
        """
        完整自动登录流程 - Full auto-login flow
        
        1. Inject cookies
        2. Check login status
        3. Handle 2FA if needed
        
        Args:
            browser: Selenium WebDriver
            browser_id: Browser ID
        
        Returns:
            bool: True if login successful
        """
        # Step 1: Try cookie login
        if self.auto_login_with_cookie(browser, browser_id):
            # Step 2: Handle 2FA if needed
            if self.handle_2fa_if_needed(browser, browser_id):
                return self.is_logged_in(browser)
        
        return False


# Global instance
auto_login = AutoLogin()

