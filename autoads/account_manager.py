# -*- coding: utf-8 -*-
"""
Account Manager - 账号管理
Manage Facebook accounts for automation
"""
import json
import os
import codecs
import csv
from datetime import datetime
from autoads.log import log
from autoads.config import config


class Account:
    """账号数据结构"""
    def __init__(self, data=None):
        self.id = ''                    # 序号
        self.username = ''              # 账号 (email/phone)
        self.password = ''              # 密码
        self.two_fa = ''                # 2FA密钥
        self.cookie = ''                # Cookie
        self.proxy = ''                 # 代理
        self.browser_id = ''            # 浏览器ID (AdsPower/BitBrowser)
        self.status = 'unused'          # 状态: unused, in_use, used, banned, error
        self.stats = {}                 # 统计: {sent: 0, collected: 0, ...}
        self.last_used = ''             # 最后使用时间
        self.notes = ''                 # 备注
        
        if data:
            self.from_dict(data)
    
    def from_dict(self, data):
        """从字典加载"""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'password': self.password,
            'two_fa': self.two_fa,
            'cookie': self.cookie,
            'proxy': self.proxy,
            'browser_id': self.browser_id,
            'status': self.status,
            'stats': self.stats,
            'last_used': self.last_used,
            'notes': self.notes
        }
    
    def __str__(self):
        return f"Account({self.username}, status={self.status})"


class AccountManager:
    """
    账号管理器
    Account Manager for importing, exporting, and managing accounts
    """
    
    def __init__(self, accounts_file='./accounts.json'):
        self.accounts_file = accounts_file
        self.accounts = []
        self._load_accounts()
    
    def _load_accounts(self):
        """Load accounts from file"""
        try:
            if os.path.exists(self.accounts_file):
                with codecs.open(self.accounts_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.accounts = [Account(acc) for acc in data]
                log.info(f"Loaded {len(self.accounts)} accounts")
        except Exception as e:
            log.error(f"Error loading accounts: {e}")
            self.accounts = []
    
    def _save_accounts(self):
        """Save accounts to file"""
        try:
            # Ensure directory exists
            dir_path = os.path.dirname(self.accounts_file)
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path)
            
            with codecs.open(self.accounts_file, 'w', encoding='utf-8') as f:
                json.dump([acc.to_dict() for acc in self.accounts], f, ensure_ascii=False, indent=2)
            log.info(f"Saved {len(self.accounts)} accounts")
            return True
        except Exception as e:
            log.error(f"Error saving accounts: {e}")
            return False
    
    def import_accounts(self, file_path, file_format='auto'):
        """
        导入账号
        Import accounts from file
        
        Supported formats:
        - json: [{"username": "", "password": "", ...}, ...]
        - csv: username,password,two_fa,cookie,proxy
        - txt: username----password----2fa----cookie----proxy (one per line)
        
        Args:
            file_path: Path to import file
            file_format: 'json', 'csv', 'txt', or 'auto' to detect
        
        Returns:
            dict: {success: bool, count: int, message: str}
        """
        try:
            if not os.path.exists(file_path):
                return {'success': False, 'count': 0, 'message': f'文件不存在: {file_path}'}
            
            # Auto-detect format
            if file_format == 'auto':
                ext = os.path.splitext(file_path)[1].lower()
                if ext == '.json':
                    file_format = 'json'
                elif ext == '.csv':
                    file_format = 'csv'
                else:
                    file_format = 'txt'
            
            imported = []
            
            if file_format == 'json':
                imported = self._import_json(file_path)
            elif file_format == 'csv':
                imported = self._import_csv(file_path)
            else:
                imported = self._import_txt(file_path)
            
            # Add to existing accounts
            start_id = len(self.accounts) + 1
            for i, acc in enumerate(imported):
                acc.id = str(start_id + i)
                if not acc.status:
                    acc.status = 'unused'
                self.accounts.append(acc)
            
            self._save_accounts()
            
            return {
                'success': True,
                'count': len(imported),
                'message': f'成功导入 {len(imported)} 个账号'
            }
        
        except Exception as e:
            log.error(f"Import error: {e}")
            return {'success': False, 'count': 0, 'message': f'导入失败: {str(e)}'}
    
    def _import_json(self, file_path):
        """Import from JSON file"""
        with codecs.open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            return [Account(item) for item in data]
        return []
    
    def _import_csv(self, file_path):
        """Import from CSV file"""
        accounts = []
        with codecs.open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                acc = Account()
                acc.username = row.get('username', row.get('账号', ''))
                acc.password = row.get('password', row.get('密码', ''))
                acc.two_fa = row.get('two_fa', row.get('2fa', row.get('2FA', '')))
                acc.cookie = row.get('cookie', row.get('Cookie', ''))
                acc.proxy = row.get('proxy', row.get('代理', ''))
                acc.browser_id = row.get('browser_id', row.get('浏览器ID', ''))
                acc.notes = row.get('notes', row.get('备注', ''))
                if acc.username:
                    accounts.append(acc)
        return accounts
    
    def _import_txt(self, file_path):
        """Import from TXT file (delimiter: ----)"""
        accounts = []
        with codecs.open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Support multiple delimiters
                if '----' in line:
                    parts = line.split('----')
                elif '\t' in line:
                    parts = line.split('\t')
                elif ',' in line:
                    parts = line.split(',')
                else:
                    parts = [line]
                
                acc = Account()
                if len(parts) >= 1:
                    acc.username = parts[0].strip()
                if len(parts) >= 2:
                    acc.password = parts[1].strip()
                if len(parts) >= 3:
                    acc.two_fa = parts[2].strip()
                if len(parts) >= 4:
                    acc.cookie = parts[3].strip()
                if len(parts) >= 5:
                    acc.proxy = parts[4].strip()
                if len(parts) >= 6:
                    acc.browser_id = parts[5].strip()
                
                if acc.username:
                    accounts.append(acc)
        return accounts
    
    def export_accounts(self, file_path, file_format='json', filter_status=None):
        """
        导出账号
        Export accounts to file
        
        Args:
            file_path: Path to export file
            file_format: 'json', 'csv', or 'txt'
            filter_status: Only export accounts with this status (None = all)
        
        Returns:
            dict: {success: bool, count: int, message: str}
        """
        try:
            accounts_to_export = self.accounts
            if filter_status:
                accounts_to_export = [acc for acc in self.accounts if acc.status == filter_status]
            
            if file_format == 'json':
                self._export_json(file_path, accounts_to_export)
            elif file_format == 'csv':
                self._export_csv(file_path, accounts_to_export)
            else:
                self._export_txt(file_path, accounts_to_export)
            
            return {
                'success': True,
                'count': len(accounts_to_export),
                'message': f'成功导出 {len(accounts_to_export)} 个账号'
            }
        
        except Exception as e:
            log.error(f"Export error: {e}")
            return {'success': False, 'count': 0, 'message': f'导出失败: {str(e)}'}
    
    def _export_json(self, file_path, accounts):
        """Export to JSON"""
        with codecs.open(file_path, 'w', encoding='utf-8') as f:
            json.dump([acc.to_dict() for acc in accounts], f, ensure_ascii=False, indent=2)
    
    def _export_csv(self, file_path, accounts):
        """Export to CSV"""
        with codecs.open(file_path, 'w', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['序号', '账号', '密码', '2FA', 'Cookie', '代理', '浏览器ID', '状态', '最后使用', '备注'])
            for acc in accounts:
                writer.writerow([
                    acc.id, acc.username, acc.password, acc.two_fa, acc.cookie,
                    acc.proxy, acc.browser_id, acc.status, acc.last_used, acc.notes
                ])
    
    def _export_txt(self, file_path, accounts):
        """Export to TXT"""
        with codecs.open(file_path, 'w', encoding='utf-8') as f:
            for acc in accounts:
                parts = [acc.username, acc.password, acc.two_fa, acc.cookie, acc.proxy, acc.browser_id]
                f.write('----'.join(parts) + '\n')
    
    def export_unused(self, file_path, file_format='txt'):
        """
        导出未使用的账号
        Export unused accounts
        """
        return self.export_accounts(file_path, file_format, filter_status='unused')
    
    def export_used(self, file_path, file_format='txt'):
        """
        导出已使用的账号
        Export used accounts
        """
        return self.export_accounts(file_path, file_format, filter_status='used')
    
    def clear_accounts(self):
        """
        清空所有账号
        Clear all accounts
        
        Returns:
            dict: {success: bool, count: int, message: str}
        """
        count = len(self.accounts)
        self.accounts = []
        self._save_accounts()
        return {
            'success': True,
            'count': count,
            'message': f'已清空 {count} 个账号'
        }
    
    # Aliases for compatibility
    clear_all = clear_accounts
    import_from_file = import_accounts  # Used by enhanced_dashboard.py
    
    def add_account(self, account_data):
        """
        添加单个账号
        Add a single account
        """
        acc = Account(account_data)
        acc.id = str(len(self.accounts) + 1)
        if not acc.status:
            acc.status = 'unused'
        self.accounts.append(acc)
        self._save_accounts()
        return acc
    
    def update_account(self, account_id, update_data):
        """
        更新账号信息
        Update account information
        """
        for acc in self.accounts:
            if acc.id == str(account_id):
                for key, value in update_data.items():
                    if hasattr(acc, key):
                        setattr(acc, key, value)
                self._save_accounts()
                return acc
        return None
    
    def delete_account(self, account_id):
        """
        删除账号
        Delete an account
        """
        for i, acc in enumerate(self.accounts):
            if acc.id == str(account_id):
                deleted = self.accounts.pop(i)
                # Re-index remaining accounts
                for j, acc in enumerate(self.accounts):
                    acc.id = str(j + 1)
                self._save_accounts()
                return deleted
        return None
    
    def get_account(self, account_id):
        """获取单个账号"""
        for acc in self.accounts:
            if acc.id == str(account_id):
                return acc
        return None
    
    def get_all_accounts(self):
        """获取所有账号"""
        return self.accounts
    
    def get_unused_accounts(self):
        """获取未使用的账号"""
        return [acc for acc in self.accounts if acc.status == 'unused']
    
    def get_account_by_browser_id(self, browser_id):
        """根据浏览器ID获取账号"""
        for acc in self.accounts:
            if acc.browser_id == browser_id:
                return acc
        return None
    
    def mark_in_use(self, account_id):
        """标记为使用中"""
        return self.update_account(account_id, {
            'status': 'in_use',
            'last_used': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    def mark_used(self, account_id):
        """标记为已使用"""
        return self.update_account(account_id, {'status': 'used'})
    
    def mark_unused(self, account_id):
        """标记为未使用"""
        return self.update_account(account_id, {'status': 'unused'})
    
    def mark_banned(self, account_id):
        """标记为已封禁"""
        return self.update_account(account_id, {'status': 'banned'})
    
    def mark_error(self, account_id, error_msg=''):
        """标记为错误"""
        return self.update_account(account_id, {
            'status': 'error',
            'notes': error_msg
        })
    
    def increment_stat(self, account_id, stat_name, value=1):
        """增加统计数据"""
        acc = self.get_account(account_id)
        if acc:
            if not acc.stats:
                acc.stats = {}
            acc.stats[stat_name] = acc.stats.get(stat_name, 0) + value
            self._save_accounts()
            return acc
        return None
    
    def get_stats(self):
        """
        获取账号统计
        Get account statistics
        """
        total = len(self.accounts)
        by_status = {}
        for acc in self.accounts:
            by_status[acc.status] = by_status.get(acc.status, 0) + 1
        
        return {
            'total': total,
            'unused': by_status.get('unused', 0),
            'in_use': by_status.get('in_use', 0),
            'used': by_status.get('used', 0),
            'banned': by_status.get('banned', 0),
            'error': by_status.get('error', 0),
            'by_status': by_status
        }
    
    def skip_used_accounts(self, skip=True):
        """
        设置是否跳过已使用的账号
        Set whether to skip used accounts
        """
        config.set_option('accounts', 'skip_used', str(skip))
    
    def should_skip_used(self):
        """检查是否应跳过已使用的账号"""
        try:
            return config.get_option('accounts', 'skip_used', 'True').lower() == 'true'
        except:
            return True


# Global instance
account_manager = AccountManager()

