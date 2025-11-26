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
    user_ids = get_ads_list(count=0)
    temp_id = [item['user_id'] for item in user_ids if item['user_id'] == ads_id]
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
    match = os.popen('tasklist /FI "IMAGENAME eq %s"' % process_name)
    process_num = match.read().count(process_name)
    return True if process_num > 0 else False


def get_service_exe():
    ads_install_path = config.service_app_path
    if ads_install_path:
        return ads_install_path
    else:
        import winreg
        # 先从注册表中找，如果没有就从桌面快捷方式找，再没有就让界面中输入
        software_name = []
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 'SOFTWARE', 0, winreg.KEY_ALL_ACCESS)
        for j in range(0, winreg.QueryInfoKey(key)[0] - 1):
            try:
                key_name = winreg.EnumKey(key, j)
                key_path = 'SOFTWARE\\' + key_name
                each_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_ALL_ACCESS)
                DisplayName, REG_SZ = winreg.QueryValueEx(each_key, 'InstallLocation')
                # DisplayName = DisplayName.encode('utf-8')
                software_name.append(DisplayName)
            except WindowsError:
                pass

        # 去重排序
        software_name = list(set(software_name))
        software_name = sorted(software_name)

        for result in software_name:
            log.info(result)
            if result.lower().find('adspower')>-1:
                ads_install_path=result+'\\AdsPower Global.exe'
                log.info(f'本机安装的adspower浏览器的地址:{ads_install_path}，从注册表中获取')
                config.set_option('ads', 'service_app_path', ads_install_path)
                break
        if ads_install_path:
            return ads_install_path

        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')

        desktop = winreg.QueryValueEx(key, 'Desktop')[0]
        from os import listdir
        from os.path import join
        from win32com.client import Dispatch
        shell = Dispatch('WScript.Shell')
        for fn in listdir(desktop):
            link = join(desktop, fn)
            if fn.endswith('.lnk') and fn.lower().find('adspower')>-1:
                ads_install_path=shell.CreateShortCut(link).Targetpath
                log.info(f'本机安装的adspower浏览器的地址:{ads_install_path},从桌面快捷方式中获取')
                config.set_option('ads', 'service_app_path', ads_install_path)
                break
        return ads_install_path

def start_service():
    if is_running('AdsPower Global.exe'):
        log.info('AdsPower Global.exe 后台已经运行了')
        return "http://127.0.0.1:50325"
    else:
        # 在维护浏览器池的类里面，重新启动一下adspower gloabl进程，因为每次的请求都只会初始化一次，所以放到这里来开启一个后台进程
        service_url = ''
        cmd = f'"{get_service_exe()}" --headless=true --api-key={api_key()} --api-port=50325'

        # os.system('chcp 65001')
        # os.system('taskkill /f /im "AdsPower Global.exe"')  # 删掉已经运行的进程

        proc = subprocess.Popen(cmd, stdout=PIPE, shell=True)
        error_mesage=[]
        try:
            while True:
                buff = proc.stdout.readline()
                buff = str(buff, encoding='utf-8')
                # print(buff)
                log.info(buff)
                url_index = buff.find('local:')
                if url_index > -1:
                    service_url = buff[url_index + 6:].replace('\r\n', '').replace(' ', '').replace(
                        'local.adspower.net', '127.0.0.1')
                    break
                if buff.find('ERROR')>-1:
                    # 说明出现异常了
                    error_mesage.append(buff[url_index + 6:].replace('\r\n', '').replace('-', ''))

                if len(error_mesage)>1: # 一般出现错误会有两行，一个是代码，一个是信息
                    break

                if buff == '' and proc.poll() != None:
                    break
        except Exception as e:
            log.error(e)
            error_mesage.append('启动ads服务异常')
            pass
        finally:
            proc.stdout.close()

        if len(error_mesage):
            return ' '.join(error_mesage)

        return service_url


def restart_service():
    # 在维护浏览器池的类里面，重新启动一下adspower gloabl进程，因为每次的请求都只会初始化一次，所以放到这里来开启一个后台进程
    service_url = None
    cmd = f'"C:\Program Files\AdsPower Global\AdsPower Global.exe" --headless=true --api-key={api_key()} --api-port=50325'

    os.system('chcp 65001')
    os.system('taskkill /f /im "AdsPower Global.exe"')  # 删掉已经运行的进程

    proc = subprocess.Popen(cmd, stdout=PIPE, shell=True)
    try:
        while True:
            buff = proc.stdout.readline()
            buff = str(buff, encoding='utf-8')
            print(buff)
            url_index = buff.find('local:')
            if url_index > -1:
                service_url = buff[url_index + 6:].replace('\r\n', '').replace(' ', '')
                break

            if buff == '' and proc.poll() != None:
                break
    except Exception as e:
        print(traceback.format_exc())
    finally:
        proc.stdout.close()
    return service_url
