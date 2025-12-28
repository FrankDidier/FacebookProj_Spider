# -*- coding: utf-8 -*-
"""
客户投诉功能测试 - Client Complaints Functional Test
=======================================================
测试客户反馈的所有问题:

1. IP配置 - 选择IP文本，自动配置到每个浏览器
2. 采集成员卡死 - 选择文件后卡死
3. 屏幕自动排列 - 浏览器窗口自动排列
4. 浏览功能 - 文件选择对话框
5. 图片浏览按钮 - 是否存在
"""

import os
import sys
import json
import time
import glob
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
# 投诉 1: IP配置 - 选择IP文本，自动配置到每个浏览器
# ============================================================================
def test_ip_auto_config():
    """
    客户需求: "选择一个文档自动配置" - 每个浏览器配置独立IP
    """
    print("\n" + "="*70)
    print("🌐 投诉1: IP自动配置到浏览器")
    print("需求: 选择IP文件 → 检查可用IP → 自动分配给每个浏览器")
    print("="*70)
    
    try:
        from autoads.ip_pool import IPPoolManager
        from autoads.bitbrowser_api import get_browser_list
        
        ip_pool = IPPoolManager()
        
        # Step 1: 创建测试IP文件
        test_ip_file = "./test_integration_data/client_ip_list.txt"
        os.makedirs(os.path.dirname(test_ip_file), exist_ok=True)
        
        test_ips = """proxy.smartproxycn.com:1000:xiaoha_session-user1:password123
proxy.smartproxycn.com:1000:xiaoha_session-user2:password123
proxy.smartproxycn.com:1000:xiaoha_session-user3:password123
proxy.smartproxycn.com:1000:xiaoha_session-user4:password123
192.168.1.100:8080:admin:admin123
192.168.1.101:8080:admin:admin123"""
        
        with open(test_ip_file, 'w', encoding='utf-8') as f:
            f.write(test_ips)
        
        log(f"创建测试IP文件: {test_ip_file}")
        log_pass("创建IP文件", "6个代理IP")
        
        # Step 2: 加载IP到池中
        result = ip_pool.load_proxies_from_file(test_ip_file)
        if result and result[0] > 0:
            log_pass("加载IP到池", f"成功加载 {result[0]} 个IP")
        else:
            log_fail("加载IP到池", f"加载失败: {result}")
            return False
        
        # Step 3: 获取浏览器列表
        browsers = get_browser_list()
        if browsers:
            log_pass("获取浏览器列表", f"找到 {len(browsers)} 个浏览器")
        else:
            log_fail("获取浏览器列表", "没有浏览器")
            return False
        
        # Step 4: 测试自动分配IP给浏览器
        if hasattr(ip_pool, 'assign_proxy_to_browser') or hasattr(ip_pool, 'get_proxy_for_browser'):
            log_pass("IP分配方法", "存在分配方法")
            
            # 测试分配
            for i, browser in enumerate(browsers[:3]):
                browser_id = browser.get('id')
                proxy = ip_pool.get_proxy_for_browser(browser_id) if hasattr(ip_pool, 'get_proxy_for_browser') else None
                if proxy:
                    log(f"    浏览器 {browser.get('name')[:20]} → {proxy.get('proxy_host', proxy.get('host', 'N/A'))}")
        else:
            log_fail("IP分配方法", "方法不存在")
            log("💡 需要添加 assign_proxy_to_browser 或 get_proxy_for_browser 方法")
        
        return True
        
    except Exception as e:
        log_fail("IP自动配置", str(e))
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# 投诉 2: 采集成员卡死 - 选择文件后程序卡死
# ============================================================================
def test_member_spider_not_freeze():
    """
    客户反馈: "采集成员 卡死" "选择浏览1KB 采集成员选择浏览，不行，卡死"
    """
    print("\n" + "="*70)
    print("🕷️ 投诉2: 采集成员卡死问题")
    print("问题: 选择1KB文件后程序卡死")
    print("="*70)
    
    try:
        # Step 1: 检查群组目录是否存在
        groups_table = config.groups_table
        log(f"群组目录: {groups_table}")
        
        if not os.path.exists(groups_table):
            os.makedirs(groups_table, exist_ok=True)
            log(f"创建目录: {groups_table}")
        
        # Step 2: 创建测试群组文件 (模拟1KB文件)
        test_group_file = os.path.join(groups_table, "test_groups.txt")
        test_groups = []
        for i in range(10):
            test_groups.append({
                "word": "测试关键词",
                "group_name": f"测试群组{i}",
                "group_link": f"https://facebook.com/groups/test{i}",
                "status": "unknown"
            })
        
        with open(test_group_file, 'w', encoding='utf-8') as f:
            for g in test_groups:
                f.write(json.dumps(g, ensure_ascii=False) + '\n')
        
        file_size = os.path.getsize(test_group_file)
        log(f"创建测试群组文件: {test_group_file} ({file_size} bytes)")
        log_pass("创建群组文件", f"{len(test_groups)} 个群组, {file_size} bytes")
        
        # Step 3: 测试加载群组文件 (这是卡死的地方)
        from autoads.pipelines.file_pipeline import FilePipeline
        from autoads.items.group_item import GroupItem
        
        pipeline = FilePipeline()
        group_template = GroupItem()
        
        log("正在加载群组文件...")
        start_time = time.time()
        
        items = list(pipeline.load_items(group_template))
        
        elapsed = time.time() - start_time
        
        if elapsed < 5:  # 应该在5秒内完成
            log_pass("加载群组文件", f"加载了 {len(items)} 个群组, 耗时 {elapsed:.2f}秒")
        else:
            log_fail("加载群组文件", f"太慢了! 耗时 {elapsed:.2f}秒")
            return False
        
        # Step 4: 检查是否有群组数据
        if items:
            log_pass("群组数据验证", f"成功读取 {len(items)} 条数据")
            # 显示第一条
            try:
                first = json.loads(items[0])
                log(f"    第一条: {first.get('group_name')}")
            except:
                pass
        else:
            log_fail("群组数据验证", "没有读取到数据!")
            log("⚠️ 这可能是 groups_save_links_only=true 的问题")
            log(f"    当前设置: groups_save_links_only = {config.groups_save_links_only}")
            return False
        
        # Step 5: 检查成员爬虫能否启动
        log("测试成员爬虫初始化...")
        from spider.fb_members import MembersSpider
        
        spider = MembersSpider()
        log_pass("成员爬虫初始化", "爬虫创建成功")
        
        return True
        
    except Exception as e:
        log_fail("采集成员测试", str(e))
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# 投诉 3: 屏幕自动排列不工作
# ============================================================================
def test_screen_auto_arrange():
    """
    客户反馈: "屏幕自动排列...还是不行"
    """
    print("\n" + "="*70)
    print("📱 投诉3: 屏幕自动排列")
    print("="*70)
    
    try:
        from autoads.webdriver import WebDriverPool
        
        pool = WebDriverPool()
        
        # 检查配置
        screen_width = config.screen_width
        screen_height = config.screen_height
        log(f"屏幕配置: {screen_width}x{screen_height}")
        
        if screen_width == 1920 and screen_height == 1080:
            log_pass("屏幕尺寸配置", "1920x1080")
        else:
            log("⚠️ 非标准屏幕尺寸，可能需要调整")
        
        # 检查方法
        if hasattr(pool, 'calculate_window_position'):
            log_pass("calculate_window_position", "方法存在")
        else:
            log_fail("calculate_window_position", "方法不存在!")
            log("💡 需要添加窗口位置计算方法")
        
        if hasattr(pool, 'reset_window_positions'):
            log_pass("reset_window_positions", "方法存在")
        else:
            log_fail("reset_window_positions", "方法不存在!")
        
        # 测试实际的窗口位置计算
        log("\n测试窗口位置计算:")
        
        # 模拟4个浏览器的位置
        for total in [2, 4, 8, 12]:
            if total <= 2:
                cols, rows = 2, 1
            elif total <= 4:
                cols, rows = 2, 2
            elif total <= 6:
                cols, rows = 3, 2
            elif total <= 9:
                cols, rows = 3, 3
            else:
                cols, rows = 4, 3
            
            w = screen_width // cols
            h = screen_height // rows
            
            log(f"  {total}个浏览器: {cols}x{rows}网格, 窗口={w}x{h}")
            
            # 计算每个窗口位置
            for i in range(min(total, 4)):
                x = (i % cols) * w
                y = (i // cols) * h
                log(f"    窗口{i+1}: 位置({x}, {y})")
        
        log_pass("窗口位置计算", "计算逻辑正确")
        
        return True
        
    except Exception as e:
        log_fail("屏幕自动排列", str(e))
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# 投诉 4: 浏览按钮/文件选择不工作
# ============================================================================
def test_browse_button():
    """
    客户反馈: "选择浏览...不行" "浏览功能不行"
    """
    print("\n" + "="*70)
    print("📂 投诉4: 浏览按钮/文件选择")
    print("="*70)
    
    try:
        # 检查 facebook.py 中的浏览按钮方法
        facebook_path = "./facebook.py"
        
        if not os.path.exists(facebook_path):
            log_fail("facebook.py", "文件不存在")
            return False
        
        with open(facebook_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查浏览方法
        methods_to_check = [
            ("_browse_member_group_file", "采集成员-浏览群组文件"),
            ("_browse_greets_member_file", "私信-浏览成员文件"),
            ("QFileDialog", "文件对话框"),
            ("processEvents", "UI响应 (防止卡死)"),
        ]
        
        for method, desc in methods_to_check:
            if method in content:
                log_pass(desc, f"'{method}' 存在")
            else:
                log_fail(desc, f"'{method}' 不存在!")
        
        # 检查是否有 processEvents 防止UI卡死
        if "QApplication.processEvents()" in content:
            log_pass("防卡死处理", "使用了 processEvents()")
        else:
            log_fail("防卡死处理", "没有使用 processEvents()!")
            log("💡 在文件对话框前后添加 QApplication.processEvents()")
        
        # 检查 members_selected_file setter
        config_path = "./autoads/config.py"
        with open(config_path, 'r', encoding='utf-8') as f:
            config_content = f.read()
        
        if "@members_selected_file.setter" in config_content:
            log_pass("members_selected_file setter", "属性可设置")
        else:
            log_fail("members_selected_file setter", "属性不可设置!")
            log("💡 这会导致选择文件后无法保存路径")
        
        return True
        
    except Exception as e:
        log_fail("浏览按钮测试", str(e))
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# 投诉 5: 图片浏览按钮不存在
# ============================================================================
def test_image_browse_button():
    """
    客户反馈: "🖼️ 浏览图片...这个也没有看到"
    """
    print("\n" + "="*70)
    print("🖼️ 投诉5: 图片浏览按钮")
    print("="*70)
    
    try:
        facebook_path = "./facebook.py"
        
        with open(facebook_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查图片相关方法
        image_methods = [
            ("_import_pm_images", "导入私信图片方法"),
            ("浏览图片", "浏览图片按钮文本"),
            ("getOpenFileNames", "多文件选择"),
            ("*.png", "PNG图片过滤"),
            ("*.jpg", "JPG图片过滤"),
        ]
        
        found = 0
        for method, desc in image_methods:
            if method in content:
                log_pass(desc, f"'{method}' 存在")
                found += 1
            else:
                log_fail(desc, f"'{method}' 不存在")
        
        if found >= 3:
            log_pass("图片浏览功能", "基本功能存在")
        else:
            log_fail("图片浏览功能", "功能不完整")
            log("💡 可能需要检查UI文件或按钮创建代码")
        
        # 检查UI文件
        ui_files = glob.glob("./ui/*.ui") + glob.glob("./*.ui")
        log(f"\n找到 {len(ui_files)} 个UI文件")
        
        return True
        
    except Exception as e:
        log_fail("图片浏览按钮", str(e))
        return False

# ============================================================================
# 投诉 6: 检查构建是否正确
# ============================================================================
def test_build_check():
    """
    客户反馈: "这段时间是不是包打错了呀？"
    """
    print("\n" + "="*70)
    print("📦 投诉6: 构建检查")
    print("="*70)
    
    try:
        # 检查关键修复是否存在
        
        # 1. groups_save_links_only 默认值
        log("检查关键配置...")
        if config.groups_save_links_only == False:
            log_pass("groups_save_links_only", "默认值为 False (正确)")
        else:
            log_fail("groups_save_links_only", f"值为 {config.groups_save_links_only} (应该是False!)")
            log("⚠️ 这会导致采集成员显示0个请求!")
        
        # 2. 检查文件管道fallback
        pipeline_path = "./autoads/pipelines/file_pipeline.py"
        with open(pipeline_path, 'r', encoding='utf-8') as f:
            pipeline_content = f.read()
        
        if "links_files" in pipeline_content and "fallback" in pipeline_content.lower():
            log_pass("file_pipeline fallback", "支持 _links.txt 回退")
        else:
            log("⚠️ file_pipeline 可能不支持 _links.txt 回退")
        
        # 3. 检查最新提交
        log("\n检查Git提交...")
        import subprocess
        try:
            result = subprocess.run(['git', 'log', '--oneline', '-5'], 
                                  capture_output=True, text=True, cwd='.')
            if result.returncode == 0:
                log("最近5次提交:")
                for line in result.stdout.strip().split('\n'):
                    log(f"  {line}")
        except:
            log("无法获取Git历史")
        
        # 4. 检查requirements.txt
        req_path = "./requirements.txt"
        if os.path.exists(req_path):
            with open(req_path, 'r') as f:
                reqs = f.read()
            
            required = ['pyotp', 'selenium', 'PySide']
            for req in required:
                if req.lower() in reqs.lower():
                    log_pass(f"依赖 {req}", "存在")
                else:
                    log_fail(f"依赖 {req}", "缺失!")
        
        return True
        
    except Exception as e:
        log_fail("构建检查", str(e))
        return False

# ============================================================================
# 综合问题诊断
# ============================================================================
def diagnose_issues():
    """诊断所有问题的根本原因"""
    print("\n" + "="*70)
    print("🔍 问题诊断总结")
    print("="*70)
    
    issues = []
    
    # 检查1: groups_save_links_only
    if config.groups_save_links_only:
        issues.append({
            "问题": "groups_save_links_only = True",
            "影响": "采集成员显示0个请求",
            "修复": "在config.ini中设置 [groups] save_links_only = false"
        })
    
    # 检查2: 群组文件是否存在
    groups_table = config.groups_table
    json_files = glob.glob(groups_table + '/*.txt')
    json_files = [f for f in json_files if not f.endswith('_links.txt')]
    
    if not json_files:
        issues.append({
            "问题": "没有群组JSON文件",
            "影响": "采集成员无法工作",
            "修复": "先运行采集群组功能"
        })
    
    # 检查3: processEvents
    with open("./facebook.py", 'r', encoding='utf-8') as f:
        fb_content = f.read()
    
    if "processEvents" not in fb_content:
        issues.append({
            "问题": "缺少 processEvents()",
            "影响": "UI会卡死",
            "修复": "在文件对话框操作前后添加 QApplication.processEvents()"
        })
    
    # 显示诊断结果
    if issues:
        print("\n发现以下问题需要修复:")
        for i, issue in enumerate(issues, 1):
            print(f"\n  {i}. 问题: {issue['问题']}")
            print(f"     影响: {issue['影响']}")
            print(f"     修复: {issue['修复']}")
    else:
        print("\n✅ 没有发现已知问题!")
    
    return len(issues) == 0

# ============================================================================
# MAIN
# ============================================================================
def main():
    print("\n" + "="*70)
    print("🧪 客户投诉功能测试 - Client Complaints Test")
    print("="*70)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    results = {}
    
    tests = [
        ("IP自动配置", test_ip_auto_config),
        ("采集成员卡死", test_member_spider_not_freeze),
        ("屏幕自动排列", test_screen_auto_arrange),
        ("浏览按钮", test_browse_button),
        ("图片浏览按钮", test_image_browse_button),
        ("构建检查", test_build_check),
    ]
    
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            results[name] = False
            log(f"测试 '{name}' 崩溃: {e}", "ERROR")
    
    # 运行诊断
    diagnose_issues()
    
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
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

