#!/anaconda3/bin python3.7
# -*- coding: utf-8 -*-
# ---
# @Software: PyCharm
# @File: ads_api.py
# @Author: James.Zhou
# @E-mail: 407360491@163.com
# @Site: 
# @Time: 七月 24, 2022
# ---
import os
import requests
import json
import subprocess
from subprocess import PIPE
import traceback
import codecs
from autoads.log import log
from autoads.config import config


def api_key():
    key = config.ads_key
    if key:
        return key
    else:
        log.info(f'ads_key没有配置！')
        return ''


def get_ads_id(ignore=[], domain_name='facebook.com'):
    temp = request_list(domain_name, ignore=ignore)
    if len(temp) > 0:
        return temp[0]
    else:
        return ''


def request_list(ignore=[], domain_name='facebook.com'):
    user_ids = get_ads_list(count=0)

    user_ids.sort(key=lambda k: int(k.get('serial_number')))
    user_ids = [item['user_id'] for item in user_ids if
                item['user_id'] not in ignore
                and domain_name == item['domain_name']]
    return user_ids


def expired_ads(ads_id):
    """Check if a browser/ads ID has expired. Returns True if expired, False otherwise."""
    from autoads.config import config
    browser_type = getattr(config, 'browser_type', 'adspower')
    
    if browser_type == 'bitbrowser':
        # For BitBrowser, check using bitbrowser_api
        try:
            from autoads import bitbrowser_api
            browsers = bitbrowser_api.get_browser_list()
            if browsers is None:
                return False  # Can't determine, assume not expired
            browser_ids = [b.get('id') or b.get('browserId') or b.get('user_id') for b in browsers]
            return ads_id not in browser_ids
        except Exception as e:
            log.debug(f"Error checking BitBrowser expired: {e}")
            return False  # Can't determine, assume not expired
    else:
        # For AdsPower
        user_ids = get_ads_list(count=0)
        if user_ids is None:
            return False  # Can't determine, assume not expired
        temp_id = [item['user_id'] for item in user_ids if item.get('user_id') == ads_id]
        return len(temp_id) == 0


def remove_expired_ads(ads_id):
    table = './ads-users.txt'
    split_index = table.rfind('.')
    new_table = table[:split_index] + '1' + table[split_index:]

    with codecs.open(table, 'r', encoding='utf-8') as fi, \
            codecs.open(new_table, 'w', encoding='utf-8') as fo:
        json_list = json.loads(fi.read())
        json_temp = []
        for data in json_list:
            if data['user_id'] == ads_id:
                continue
            json_temp.append(data)
        fo.write(json.dumps(json_temp, indent=1, ensure_ascii=False))

    # 通过删除原来的文件，再把新的临时表更改名称为原来的文件名
    os.remove(table)  # remove original
    os.rename(new_table, table)  # rename temp to original name


def get_ads_list(count):
    # 先从文件中去查找，找不到就从地址中去找
    json_data = None
    file = './ads-users.txt'
    if os.path.exists(file):
        with open(file, 'r', encoding='utf8')as fp:
            text = fp.read()
            if text:
                json_data = json.loads(text)
                # print(len(json_data))
    else:
        service_url = start_service()
        if service_url.find('http')>-1:
            url = service_url + '/api/v1/user/list?page=1&page_size=100'

            header = {
                "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
                "Content-Type": "application/json"
            }

            res = requests.get(url, headers=header)

            count += 1

            if res.status_code == 200:
                json_list = json.loads(res.text)
                if json_list['code'] == 0:
                    json_data = json_list['data']['list']
                else:
                    if count < 3:
                        restart_service()
                        json_data=get_ads_list(count)
                    else:
                        json_data = []
            else:
                if count < 3:
                    restart_service()
                    json_data=get_ads_list(count)
                else:
                    json_data = []

            if json_data and len(json_data) > 0:
                with open(file, 'w', encoding='utf8') as f:
                    f.write(json.dumps(json_data, indent=1, ensure_ascii=False))
    return json_data


def is_running(process_name):
    """Check if a process is running. Works on Windows and macOS/Linux."""
    import platform
    system = platform.system()
    
    try:
        if system == 'Windows':
            match = os.popen('tasklist /FI "IMAGENAME eq %s"' % process_name)
            process_num = match.read().count(process_name)
            return process_num > 0
        else:  # macOS/Linux
            # Extract just the process name without path
            proc_name = os.path.basename(process_name).replace('.exe', '')
            match = os.popen(f'pgrep -f "{proc_name}"')
            result = match.read().strip()
            return len(result) > 0
    except Exception as e:
        log.debug(f"Error checking process: {e}")
        return False


def get_service_exe():
    """Get the browser service executable path. Cross-platform."""
    import platform
    system = platform.system()
    
    ads_install_path = config.service_app_path
    if ads_install_path and os.path.exists(ads_install_path):
        return ads_install_path
    
    # Check browser type
    browser_type = getattr(config, 'browser_type', 'adspower')
    
    if system == 'Darwin':  # macOS
        # Common macOS paths
        if browser_type == 'bitbrowser':
            common_paths = [
                '/Applications/BitBrowser.app/Contents/MacOS/BitBrowser',
                os.path.expanduser('~/Applications/BitBrowser.app/Contents/MacOS/BitBrowser'),
            ]
        else:  # AdsPower
            common_paths = [
                '/Applications/AdsPower.app/Contents/MacOS/AdsPower',
                os.path.expanduser('~/Applications/AdsPower.app/Contents/MacOS/AdsPower'),
            ]
        for path in common_paths:
            if os.path.exists(path):
                log.info(f'找到浏览器路径: {path}')
                return path
        return None
        
    elif system == 'Windows':
        # Windows-specific registry lookup
        try:
            import winreg
            software_name = []
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 'SOFTWARE', 0, winreg.KEY_ALL_ACCESS)
            for j in range(0, winreg.QueryInfoKey(key)[0] - 1):
                try:
                    key_name = winreg.EnumKey(key, j)
                    key_path = 'SOFTWARE\\' + key_name
                    each_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_ALL_ACCESS)
                    DisplayName, REG_SZ = winreg.QueryValueEx(each_key, 'InstallLocation')
                    software_name.append(DisplayName)
                except WindowsError:
                    pass

            software_name = list(set(software_name))
            software_name = sorted(software_name)

            search_term = 'bitbrowser' if browser_type == 'bitbrowser' else 'adspower'
            exe_name = 'BitBrowser.exe' if browser_type == 'bitbrowser' else 'AdsPower Global.exe'
            
            for result in software_name:
                if result.lower().find(search_term) > -1:
                    ads_install_path = result + '\\' + exe_name
                    log.info(f'本机安装的浏览器地址: {ads_install_path}，从注册表中获取')
                    config.set_option('ads', 'service_app_path', ads_install_path)
                    break
            if ads_install_path:
                return ads_install_path

            # Try desktop shortcuts
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                 r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
            desktop = winreg.QueryValueEx(key, 'Desktop')[0]
            from os import listdir
            from os.path import join
            from win32com.client import Dispatch
            shell = Dispatch('WScript.Shell')
            for fn in listdir(desktop):
                link = join(desktop, fn)
                if fn.endswith('.lnk') and fn.lower().find(search_term) > -1:
                    ads_install_path = shell.CreateShortCut(link).Targetpath
                    log.info(f'本机安装的浏览器地址: {ads_install_path}，从桌面快捷方式中获取')
                    config.set_option('ads', 'service_app_path', ads_install_path)
                    break
        except Exception as e:
            log.debug(f"Windows registry lookup failed: {e}")
        return ads_install_path
    
    else:  # Linux
        if browser_type == 'bitbrowser':
            common_paths = ['/opt/bitbrowser/BitBrowser', '/usr/bin/bitbrowser']
        else:
            common_paths = ['/opt/adspower/adspower', '/usr/bin/adspower']
        for path in common_paths:
            if os.path.exists(path):
                return path
        return None

def start_service():
    """Start the browser service and return the service URL. Cross-platform, multi-browser."""
    browser_type = getattr(config, 'browser_type', 'adspower')
    
    # For BitBrowser, just return the local API URL
    if browser_type == 'bitbrowser':
        port = getattr(config, 'bitbrowser_port', '54345')
        service_url = f"http://127.0.0.1:{port}"
        try:
            from autoads import bitbrowser_api
            if bitbrowser_api.test_connection():
                log.info(f'BitBrowser 服务运行正常: {service_url}')
                return service_url
            else:
                log.warning('BitBrowser 服务未运行，请手动启动 BitBrowser')
                return service_url  # Return URL anyway, let caller handle
        except Exception as e:
            log.debug(f"BitBrowser check failed: {e}")
            return service_url
    
    # For AdsPower
    process_name = 'AdsPower Global.exe' if os.name == 'nt' else 'AdsPower'
    if is_running(process_name):
        log.info(f'{process_name} 后台已经运行了')
        return "http://127.0.0.1:50325"
    
    # Try to start AdsPower
    service_exe = get_service_exe()
    if not service_exe:
        log.warning('未找到浏览器可执行文件，请手动启动浏览器')
        return "http://127.0.0.1:50325"  # Return default URL
    
    service_url = ''
    key = api_key()
    cmd = f'"{service_exe}" --headless=true --api-key={key} --api-port=50325'

    try:
        proc = subprocess.Popen(cmd, stdout=PIPE, shell=True)
        error_mesage = []
        try:
            while True:
                buff = proc.stdout.readline()
                buff = str(buff, encoding='utf-8')
                log.info(buff)
                url_index = buff.find('local:')
                if url_index > -1:
                    service_url = buff[url_index + 6:].replace('\r\n', '').replace(' ', '').replace(
                        'local.adspower.net', '127.0.0.1')
                    break
                if buff.find('ERROR') > -1:
                    error_mesage.append(buff[url_index + 6:].replace('\r\n', '').replace('-', ''))

                if len(error_mesage) > 1:
                    break

                if buff == '' and proc.poll() is not None:
                    break
        except Exception as e:
            log.error(e)
            error_mesage.append('启动ads服务异常')
        finally:
            proc.stdout.close()

        if len(error_mesage):
            return ' '.join(error_mesage)
    except Exception as e:
        log.error(f"Failed to start service: {e}")
        return "http://127.0.0.1:50325"

    return service_url if service_url else "http://127.0.0.1:50325"


def restart_service():
    """Restart the browser service. Cross-platform, multi-browser."""
    import platform
    browser_type = getattr(config, 'browser_type', 'adspower')
    
    # For BitBrowser, just check/return the service URL
    if browser_type == 'bitbrowser':
        port = getattr(config, 'bitbrowser_port', '54345')
        return f"http://127.0.0.1:{port}"
    
    # For AdsPower - kill and restart
    system = platform.system()
    service_exe = get_service_exe()
    
    if system == 'Windows':
        os.system('chcp 65001')
        os.system('taskkill /f /im "AdsPower Global.exe"')
    else:  # macOS/Linux
        os.system('pkill -f "AdsPower" 2>/dev/null || true')
    
    if not service_exe:
        log.warning('未找到浏览器可执行文件')
        return "http://127.0.0.1:50325"
    
    service_url = None
    key = api_key()
    cmd = f'"{service_exe}" --headless=true --api-key={key} --api-port=50325'

    try:
        proc = subprocess.Popen(cmd, stdout=PIPE, shell=True)
        try:
            while True:
                buff = proc.stdout.readline()
                buff = str(buff, encoding='utf-8')
                log.info(buff)
                url_index = buff.find('local:')
                if url_index > -1:
                    service_url = buff[url_index + 6:].replace('\r\n', '').replace(' ', '')
                    break

                if buff == '' and proc.poll() is not None:
                    break
        except Exception as e:
            log.error(f"Error during restart: {e}")
        finally:
            proc.stdout.close()
    except Exception as e:
        log.error(f"Failed to restart service: {e}")
    
    return service_url if service_url else "http://127.0.0.1:50325"
