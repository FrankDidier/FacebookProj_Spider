# -*- coding: utf-8 -*-
"""
Cloud Deduplication Service - 云端去重复
Allows checking and marking items as processed across multiple instances
"""
import hashlib
import json
import os
import sqlite3
import requests
import threading
from datetime import datetime
from autoads.log import log
from autoads.config import config


class CloudDeduplication:
    """
    云端去重复服务
    Supports both local SQLite and remote API modes
    """
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(CloudDeduplication, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        self.enabled = False
        self.db_name = 'default'
        self.mode = 'local'  # 'local' or 'remote'
        self.remote_url = ''
        self.local_db_path = './dedup_cache/'
        self._connection = None
        
        # Load config
        self._load_config()
    
    def _load_config(self):
        """Load configuration from config.ini"""
        try:
            # get_option doesn't support default values, use try/except
            try:
                self.enabled = config.get_option('cloud_dedup', 'enabled').lower() == 'true'
            except:
                self.enabled = False
            
            try:
                self.db_name = config.get_option('cloud_dedup', 'db_name')
            except:
                self.db_name = 'default'
            
            try:
                self.mode = config.get_option('cloud_dedup', 'mode')
            except:
                self.mode = 'local'
            
            try:
                self.remote_url = config.get_option('cloud_dedup', 'remote_url')
            except:
                self.remote_url = ''
            
            try:
                self.local_db_path = config.get_option('cloud_dedup', 'local_db_path')
            except:
                self.local_db_path = './dedup_cache/'
                
            log.debug(f"Cloud dedup config loaded: enabled={self.enabled}, mode={self.mode}, db={self.db_name}")
        except Exception as e:
            log.debug(f"Cloud dedup config error: {e}")
    
    def _get_local_db(self):
        """Get local SQLite connection"""
        if not os.path.exists(self.local_db_path):
            os.makedirs(self.local_db_path)
        
        db_file = os.path.join(self.local_db_path, f'{self.db_name}.db')
        
        if self._connection is None:
            self._connection = sqlite3.connect(db_file, check_same_thread=False)
            self._create_tables()
        
        return self._connection
    
    def _create_tables(self):
        """Create necessary tables"""
        cursor = self._connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS processed_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_hash TEXT UNIQUE NOT NULL,
                item_type TEXT NOT NULL,
                item_key TEXT,
                created_at TEXT NOT NULL,
                source TEXT
            )
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_item_hash ON processed_items(item_hash)
        ''')
        self._connection.commit()
    
    def _hash_item(self, item_key, item_type='member'):
        """Generate hash for an item"""
        hash_input = f"{self.db_name}:{item_type}:{item_key}"
        return hashlib.md5(hash_input.encode()).hexdigest()
    
    def is_processed(self, item_key, item_type='member'):
        """
        Check if an item has been processed
        检查一个项目是否已经处理过
        
        Args:
            item_key: Unique identifier (e.g., member_link, group_link)
            item_type: Type of item ('member', 'group', 'message', etc.)
        
        Returns:
            bool: True if already processed, False otherwise
        """
        if not self.enabled:
            return False
        
        item_hash = self._hash_item(item_key, item_type)
        
        try:
            if self.mode == 'local':
                return self._local_is_processed(item_hash)
            else:
                return self._remote_is_processed(item_hash, item_key, item_type)
        except Exception as e:
            log.error(f"Error checking processed status: {e}")
            return False
    
    def _local_is_processed(self, item_hash):
        """Check locally"""
        conn = self._get_local_db()
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM processed_items WHERE item_hash = ?', (item_hash,))
        return cursor.fetchone() is not None
    
    def _remote_is_processed(self, item_hash, item_key, item_type):
        """Check via remote API"""
        try:
            response = requests.post(
                f"{self.remote_url}/check",
                json={
                    'db_name': self.db_name,
                    'item_hash': item_hash,
                    'item_key': item_key,
                    'item_type': item_type
                },
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                return data.get('exists', False)
        except Exception as e:
            log.warning(f"Remote dedup check failed, falling back to local: {e}")
            # Fallback to local
            return self._local_is_processed(item_hash)
        return False
    
    def mark_processed(self, item_key, item_type='member', source=''):
        """
        Mark an item as processed
        标记一个项目为已处理
        
        Args:
            item_key: Unique identifier
            item_type: Type of item
            source: Source identifier (e.g., ads_id)
        
        Returns:
            bool: True if marked successfully
        """
        if not self.enabled:
            return True
        
        item_hash = self._hash_item(item_key, item_type)
        
        try:
            if self.mode == 'local':
                return self._local_mark_processed(item_hash, item_key, item_type, source)
            else:
                return self._remote_mark_processed(item_hash, item_key, item_type, source)
        except Exception as e:
            log.error(f"Error marking processed: {e}")
            return False
    
    def _local_mark_processed(self, item_hash, item_key, item_type, source):
        """Mark locally"""
        conn = self._get_local_db()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO processed_items 
                (item_hash, item_type, item_key, created_at, source)
                VALUES (?, ?, ?, ?, ?)
            ''', (item_hash, item_type, item_key, datetime.now().isoformat(), source))
            conn.commit()
            return True
        except Exception as e:
            log.error(f"Error inserting to local db: {e}")
            return False
    
    def _remote_mark_processed(self, item_hash, item_key, item_type, source):
        """Mark via remote API"""
        try:
            response = requests.post(
                f"{self.remote_url}/mark",
                json={
                    'db_name': self.db_name,
                    'item_hash': item_hash,
                    'item_key': item_key,
                    'item_type': item_type,
                    'source': source
                },
                timeout=5
            )
            if response.status_code == 200:
                return True
        except Exception as e:
            log.warning(f"Remote dedup mark failed, falling back to local: {e}")
            # Fallback to local
            return self._local_mark_processed(item_hash, item_key, item_type, source)
        return False
    
    def test_connection(self):
        """
        Test connection to deduplication service
        测试连接
        
        Returns:
            dict: {success: bool, message: str, count: int}
        """
        try:
            if self.mode == 'local':
                conn = self._get_local_db()
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM processed_items')
                count = cursor.fetchone()[0]
                return {
                    'success': True,
                    'message': f'本地数据库连接成功，已记录 {count} 条数据',
                    'count': count,
                    'mode': 'local'
                }
            else:
                response = requests.get(
                    f"{self.remote_url}/status",
                    params={'db_name': self.db_name},
                    timeout=5
                )
                if response.status_code == 200:
                    data = response.json()
                    return {
                        'success': True,
                        'message': f'云端数据库连接成功，已记录 {data.get("count", 0)} 条数据',
                        'count': data.get('count', 0),
                        'mode': 'remote'
                    }
                else:
                    return {
                        'success': False,
                        'message': f'云端连接失败: HTTP {response.status_code}',
                        'count': 0,
                        'mode': 'remote'
                    }
        except Exception as e:
            return {
                'success': False,
                'message': f'连接失败: {str(e)}',
                'count': 0,
                'mode': self.mode
            }
    
    def clear_database(self):
        """
        Clear all records from the database
        清空数据库
        """
        try:
            if self.mode == 'local':
                conn = self._get_local_db()
                cursor = conn.cursor()
                cursor.execute('DELETE FROM processed_items')
                conn.commit()
                log.info(f"Cleared local dedup database: {self.db_name}")
                return True
            else:
                response = requests.post(
                    f"{self.remote_url}/clear",
                    json={'db_name': self.db_name},
                    timeout=10
                )
                return response.status_code == 200
        except Exception as e:
            log.error(f"Error clearing database: {e}")
            return False
    
    def get_stats(self):
        """Get statistics"""
        try:
            conn = self._get_local_db()
            cursor = conn.cursor()
            
            # Total count
            cursor.execute('SELECT COUNT(*) FROM processed_items')
            total = cursor.fetchone()[0]
            
            # By type
            cursor.execute('SELECT item_type, COUNT(*) FROM processed_items GROUP BY item_type')
            by_type = dict(cursor.fetchall())
            
            # Today's count
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute('SELECT COUNT(*) FROM processed_items WHERE created_at LIKE ?', (f'{today}%',))
            today_count = cursor.fetchone()[0]
            
            return {
                'total': total,
                'by_type': by_type,
                'today': today_count
            }
        except Exception as e:
            log.error(f"Error getting stats: {e}")
            return {'total': 0, 'by_type': {}, 'today': 0}
    
    def set_config(self, enabled=None, db_name=None, mode=None, remote_url=None):
        """Update configuration"""
        if enabled is not None:
            self.enabled = enabled
            config.set_option('cloud_dedup', 'enabled', str(enabled))
        
        if db_name is not None:
            self.db_name = db_name
            config.set_option('cloud_dedup', 'db_name', db_name)
            self._connection = None  # Reset connection for new db
        
        if mode is not None:
            self.mode = mode
            config.set_option('cloud_dedup', 'mode', mode)
        
        if remote_url is not None:
            self.remote_url = remote_url
            config.set_option('cloud_dedup', 'remote_url', remote_url)
    
    def close(self):
        """Close connections"""
        if self._connection:
            self._connection.close()
            self._connection = None


# Global instance
cloud_dedup = CloudDeduplication()

