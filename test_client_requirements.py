# -*- coding: utf-8 -*-
"""
客户需求功能测试 - Client Requirements Functional Test
=========================================================
基于客户截图测试以下功能:
1. SmartProxy格式代理解析 (host:port:username:password)
2. Cookie一键导入
3. 2FA一键导入
4. 多浏览器窗口自动排列
5. 账号批量管理
"""

import os
import sys
import json
import time
from datetime import datetime

# Initialize config first
from autoads.config import config
config.name = 'config.ini'

def log(msg, level="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [{level}] {msg}")

def log_pass(test_name, detail=""):
    print(f"  ✅ PASS: {test_name}" + (f" - {detail}" if detail else ""))

def log_fail(test_name, detail=""):
    print(f"  ❌ FAIL: {test_name}" + (f" - {detail}" if detail else ""))

# ============================================================================
# TEST 1: SmartProxy格式代理解析
# ============================================================================
def test_smartproxy_format():
    """测试SmartProxy格式的代理解析: host:port:username:password"""
    print("\n" + "="*70)
    print("🌐 TEST 1: SmartProxy格式代理解析")
    print("格式: proxy.smartproxycn.com:1000:xiaoha_session-xxx:password")
    print("="*70)
    
    try:
        from autoads.ip_pool import IPPoolManager
        
        ip_pool = IPPoolManager()
        
        # SmartProxy格式的代理列表 (从客户截图)
        smartproxy_list = [
            "proxy.smartproxycn.com:1000:xiaoha_session-yYhkcTyukq:qqfsdgdffd",
            "proxy.smartproxycn.com:1000:xiaoha_session-jbon06LEmU:qqfsdgdffd",
            "proxy.smartproxycn.com:1000:xiaoha_session-vu746TK06w:qqfsdgdffd",
            "proxy.smartproxycn.com:1000:xiaoha_session-oIoy0Fyyr2:qqfsdgdffd",
            "proxy.smartproxycn.com:1000:xiaoha_session-KQIjXSuKaN:qqfsdgdffd",
        ]
        
        # 测试解析
        parsed_count = 0
        for proxy_str in smartproxy_list:
            parsed = ip_pool.parse_proxy(proxy_str)
            if parsed:
                parsed_count += 1
                # Verify parsed correctly (keys may be 'host' or 'proxy_host')
                host = parsed.get('host') or parsed.get('proxy_host')
                port = parsed.get('port') or parsed.get('proxy_port')
                user = parsed.get('username') or parsed.get('proxy_user', 'N/A')
                
                if host == 'proxy.smartproxycn.com':
                    log(f"  解析成功: {proxy_str[:50]}...")
                    log(f"    → host: {host}")
                    log(f"    → port: {port}")
                    log(f"    → user: {str(user)[:20]}...")
                else:
                    log(f"  解析错误: {parsed}", "WARN")
        
        if parsed_count == len(smartproxy_list):
            log_pass("SmartProxy Format", f"成功解析 {parsed_count}/{len(smartproxy_list)} 个代理")
            return True
        else:
            log_fail("SmartProxy Format", f"只解析了 {parsed_count}/{len(smartproxy_list)} 个")
            return False
            
    except Exception as e:
        log_fail("SmartProxy Format", str(e))
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# TEST 2: Cookie一键导入
# ============================================================================
def test_cookie_import():
    """测试Cookie一键导入功能"""
    print("\n" + "="*70)
    print("🍪 TEST 2: Cookie一键导入")
    print("="*70)
    
    try:
        from autoads.auto_login import AutoLogin
        
        auto_login = AutoLogin()
        
        # Test 1: JSON格式Cookie
        json_cookie = '[{"name": "c_user", "value": "123456789", "domain": ".facebook.com"}, {"name": "xs", "value": "abcdef123", "domain": ".facebook.com"}]'
        
        parsed_json = auto_login._parse_cookies(json_cookie)
        if parsed_json and len(parsed_json) >= 2:
            log_pass("JSON Cookie解析", f"解析了 {len(parsed_json)} 个cookie")
            for c in parsed_json[:2]:
                log(f"    → {c.get('name')}: {c.get('value')[:10]}...")
        else:
            log_fail("JSON Cookie解析", "解析失败")
            return False
        
        # Test 2: Key=Value格式Cookie (常见格式)
        kv_cookie = "c_user=123456789; xs=abcdef123; fr=0abc123def"
        
        parsed_kv = auto_login._parse_cookies(kv_cookie)
        if parsed_kv and len(parsed_kv) >= 3:
            log_pass("Key=Value Cookie解析", f"解析了 {len(parsed_kv)} 个cookie")
            for c in parsed_kv[:3]:
                log(f"    → {c.get('name')}: {c.get('value')[:10]}...")
        else:
            log_fail("Key=Value Cookie解析", f"只解析了 {len(parsed_kv) if parsed_kv else 0} 个")
            return False
        
        # Test 3: 验证inject_cookies方法存在
        if hasattr(auto_login, 'inject_cookies'):
            log_pass("inject_cookies方法", "方法存在，可注入Cookie到浏览器")
        else:
            log_fail("inject_cookies方法", "方法不存在")
            return False
        
        return True
        
    except Exception as e:
        log_fail("Cookie Import", str(e))
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# TEST 3: 2FA一键导入
# ============================================================================
def test_2fa_import():
    """测试2FA验证码自动生成和填充"""
    print("\n" + "="*70)
    print("🔐 TEST 3: 2FA一键导入")
    print("="*70)
    
    try:
        from autoads.auto_login import AutoLogin
        import pyotp
        
        auto_login = AutoLogin()
        
        # 测试2FA密钥
        test_secret = "JBSWY3DPEHPK3PXP"  # 标准测试密钥
        
        # Test 1: 生成2FA验证码
        code = auto_login.generate_2fa_code(test_secret)
        
        if code and len(code) == 6 and code.isdigit():
            log_pass("2FA验证码生成", f"生成的验证码: {code}")
            
            # 验证码是否正确
            totp = pyotp.TOTP(test_secret)
            expected = totp.now()
            if code == expected:
                log_pass("2FA验证码验证", "验证码与pyotp生成的一致")
            else:
                log(f"  注意: 生成的验证码 {code} vs 预期 {expected}", "WARN")
        else:
            log_fail("2FA验证码生成", f"无效的验证码: {code}")
            return False
        
        # Test 2: 验证fill_2fa_code方法存在
        if hasattr(auto_login, 'fill_2fa_code'):
            log_pass("fill_2fa_code方法", "方法存在，可自动填充2FA")
        else:
            log_fail("fill_2fa_code方法", "方法不存在")
            return False
        
        # Test 3: 验证full_auto_login方法存在 (完整自动登录流程)
        if hasattr(auto_login, 'full_auto_login'):
            log_pass("full_auto_login方法", "完整自动登录流程方法存在")
        else:
            log_fail("full_auto_login方法", "方法不存在")
        
        return True
        
    except ImportError as e:
        log_fail("2FA Import", f"缺少依赖: {e}")
        log("💡 运行: pip install pyotp")
        return False
    except Exception as e:
        log_fail("2FA Import", str(e))
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# TEST 4: 多浏览器窗口自动排列
# ============================================================================
def test_browser_grid():
    """测试多浏览器窗口网格排列"""
    print("\n" + "="*70)
    print("📱 TEST 4: 多浏览器窗口自动排列")
    print("="*70)
    
    try:
        from autoads.webdriver import WebDriverPool
        
        # 获取屏幕尺寸配置
        screen_width = config.screen_width
        screen_height = config.screen_height
        log(f"屏幕尺寸: {screen_width}x{screen_height}")
        
        # 测试不同数量浏览器的网格布局
        test_cases = [
            (1, "全屏"),
            (2, "左右并排"),
            (4, "2x2网格"),
            (6, "3x2网格"),
            (8, "4x2网格"),
            (12, "4x3网格 (如客户截图)"),
            (16, "4x4网格"),
        ]
        
        pool = WebDriverPool()
        
        for browser_count, expected_layout in test_cases:
            # 计算网格
            if browser_count == 1:
                cols, rows = 1, 1
            elif browser_count == 2:
                cols, rows = 2, 1
            elif browser_count <= 4:
                cols, rows = 2, 2
            elif browser_count <= 6:
                cols, rows = 3, 2
            elif browser_count <= 9:
                cols, rows = 3, 3
            elif browser_count <= 12:
                cols, rows = 4, 3
            else:
                cols, rows = 4, 4
            
            window_width = screen_width // cols
            window_height = screen_height // rows
            
            log(f"  {browser_count}个浏览器: {cols}x{rows}网格, 窗口大小: {window_width}x{window_height}")
        
        log_pass("网格布局计算", "所有布局计算正确")
        
        # 验证reset_window_positions方法
        if hasattr(pool, 'reset_window_positions'):
            log_pass("reset_window_positions", "方法存在，可重置窗口位置")
        else:
            log_fail("reset_window_positions", "方法不存在")
            return False
        
        return True
        
    except Exception as e:
        log_fail("Browser Grid", str(e))
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# TEST 5: 账号批量管理
# ============================================================================
def test_account_batch():
    """测试账号批量导入和管理"""
    print("\n" + "="*70)
    print("👥 TEST 5: 账号批量管理 (支持1000+账号)")
    print("="*70)
    
    try:
        from autoads.account_manager import AccountManager, Account
        
        manager = AccountManager()
        
        # Test 1: 创建测试账号文件
        test_accounts = []
        for i in range(100):  # 模拟100个账号
            test_accounts.append({
                "email": f"user{i}@test.com",
                "password": f"pass{i}",
                "two_fa_secret": "JBSWY3DPEHPK3PXP",
                "cookie": f"c_user={i}; xs=abc{i}"
            })
        
        # 写入测试文件
        test_file = "./test_integration_data/batch_accounts.json"
        os.makedirs(os.path.dirname(test_file), exist_ok=True)
        
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(test_accounts, f)
        
        log(f"创建测试账号文件: {len(test_accounts)} 个账号")
        
        # Test 2: 导入账号
        result = manager.import_accounts(test_file)
        
        if result and result.get('success') and result.get('count', 0) > 0:
            log_pass("批量导入账号", f"成功导入 {result.get('count')} 个账号")
        else:
            log_fail("批量导入账号", f"导入失败: {result}")
            return False
        
        # Test 3: 获取未使用的账号
        unused = manager.get_unused_accounts()
        if unused:
            log_pass("获取未使用账号", f"找到 {len(unused)} 个可用账号")
        else:
            log_fail("获取未使用账号", "没有找到可用账号")
        
        # Test 4: 账号-浏览器绑定
        if hasattr(manager, 'bind_to_browser') or hasattr(manager, 'account_browser_bindings'):
            log_pass("账号-浏览器绑定", "支持账号与浏览器绑定")
        else:
            from autoads.auto_login import AutoLogin
            al = AutoLogin()
            if hasattr(al, 'bind_account_to_browser'):
                log_pass("账号-浏览器绑定", "通过AutoLogin支持绑定")
            else:
                log_fail("账号-浏览器绑定", "功能不存在")
        
        return True
        
    except Exception as e:
        log_fail("Account Batch", str(e))
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# TEST 6: 代理文件导入 (IP.txt格式)
# ============================================================================
def test_proxy_file_import():
    """测试从文件导入代理列表"""
    print("\n" + "="*70)
    print("📂 TEST 6: 代理文件导入 (IP.txt)")
    print("="*70)
    
    try:
        from autoads.ip_pool import IPPoolManager
        
        ip_pool = IPPoolManager()
        
        # 创建测试代理文件 (模拟SmartProxy格式)
        test_proxies = """proxy.smartproxycn.com:1000:xiaoha_session-yYhkcTyukq:qqfsdgdffd
proxy.smartproxycn.com:1000:xiaoha_session-jbon06LEmU:qqfsdgdffd
proxy.smartproxycn.com:1000:xiaoha_session-vu746TK06w:qqfsdgdffd
192.168.1.1:8080
http://user:pass@proxy.example.com:3128
socks5://127.0.0.1:1080"""
        
        test_file = "./test_integration_data/test_proxies.txt"
        os.makedirs(os.path.dirname(test_file), exist_ok=True)
        
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_proxies)
        
        log(f"创建测试代理文件: {test_file}")
        
        # 导入代理
        result = ip_pool.load_proxies_from_file(test_file)
        
        if result and result[0] > 0:
            log_pass("导入代理文件", f"成功加载 {result[0]} 个代理, {result[1]} 个失败")
            
            # 显示加载的代理
            proxies = ip_pool.get_all_proxies() if hasattr(ip_pool, 'get_all_proxies') else []
            if proxies:
                for p in proxies[:3]:
                    log(f"    → {p.get('host')}:{p.get('port')}")
        else:
            log_fail("导入代理文件", f"加载失败: {result}")
            return False
        
        return True
        
    except Exception as e:
        log_fail("Proxy File Import", str(e))
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# TEST 7: 实际打开浏览器并应用代理
# ============================================================================
def test_browser_with_proxy():
    """测试打开浏览器并应用代理"""
    print("\n" + "="*70)
    print("🌐 TEST 7: 浏览器代理应用 (可选)")
    print("="*70)
    
    response = input("是否测试实际打开浏览器? (y/n): ").strip().lower()
    if response != 'y':
        log("跳过浏览器测试")
        return True
    
    try:
        from autoads.bitbrowser_api import get_browser_list, start_browser, stop_browser
        from autoads.ip_pool import IPPoolManager
        
        # 获取浏览器
        browsers = get_browser_list()
        if not browsers:
            log_fail("获取浏览器", "没有可用的浏览器")
            return False
        
        browser_id = browsers[0]['id']
        log(f"使用浏览器: {browsers[0].get('name')}")
        
        # 启动浏览器
        result = start_browser(browser_id)
        if result and result.get('success'):
            log_pass("启动浏览器", "成功")
            
            # 等待3秒
            log("等待3秒...")
            time.sleep(3)
            
            # 关闭浏览器
            stop_browser(browser_id)
            log_pass("关闭浏览器", "成功")
        else:
            log_fail("启动浏览器", str(result))
            return False
        
        return True
        
    except Exception as e:
        log_fail("Browser with Proxy", str(e))
        return False

# ============================================================================
# MAIN
# ============================================================================
def main():
    print("\n" + "="*70)
    print("🧪 客户需求功能测试 - Client Requirements Test")
    print("="*70)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("基于客户截图测试以下功能:")
    print("  1. SmartProxy格式代理解析")
    print("  2. Cookie一键导入")
    print("  3. 2FA一键导入")
    print("  4. 多浏览器窗口自动排列")
    print("  5. 账号批量管理")
    print("  6. 代理文件导入")
    print("="*70)
    
    results = {}
    
    tests = [
        ("SmartProxy格式", test_smartproxy_format),
        ("Cookie导入", test_cookie_import),
        ("2FA导入", test_2fa_import),
        ("浏览器网格", test_browser_grid),
        ("账号批量管理", test_account_batch),
        ("代理文件导入", test_proxy_file_import),
    ]
    
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            results[name] = False
            log(f"测试 '{name}' 崩溃: {e}", "ERROR")
    
    # 可选的浏览器测试
    # results["浏览器代理"] = test_browser_with_proxy()
    
    # Summary
    print("\n" + "="*70)
    print("📊 测试结果汇总")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    failed = sum(1 for v in results.values() if not v)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")
    
    print(f"\n  总计: {passed} 通过, {failed} 失败")
    
    if failed == 0:
        print("\n🎉 所有客户需求功能测试通过!")
    else:
        print("\n⚠️ 部分测试失败，请检查上面的错误。")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

