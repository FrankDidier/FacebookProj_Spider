# -*- coding: utf-8 -*-
"""
Application Logger - 应用日志记录系统
Captures all application actions, button clicks, spider events, and errors
Saves to file for debugging client issues
"""
import os
import sys
import json
import traceback
import functools
from datetime import datetime
from loguru import logger
import threading
import atexit


class AppLogger:
    """
    Comprehensive application logger that captures:
    - Button clicks
    - Spider actions (start, stop, progress)
    - File operations (create, delete, read)
    - Errors and exceptions
    - UI events
    - Configuration changes
    - Browser interactions
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(AppLogger, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_dir = './logs/'
        self.log_file = None
        self.actions = []
        self.errors = []
        self.start_time = datetime.now()
        
        self._setup_logging()
        self._log_session_start()
        
        # Register cleanup on exit
        atexit.register(self._save_session_log)
    
    def _setup_logging(self):
        """Setup loguru with file and console handlers"""
        # Create logs directory
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Log file path
        self.log_file = os.path.join(self.log_dir, f'session_{self.session_id}.log')
        self.json_log_file = os.path.join(self.log_dir, f'session_{self.session_id}.json')
        
        # Remove default handler
        logger.remove()
        
        # Add console handler (colored)
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level="DEBUG",
            colorize=True
        )
        
        # Add file handler (detailed)
        logger.add(
            self.log_file,
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
            level="DEBUG",
            rotation="50 MB",
            retention="7 days",
            encoding="utf-8"
        )
        
        logger.info(f"📝 日志系统初始化完成 | Log file: {self.log_file}")
    
    def _log_session_start(self):
        """Log session start information"""
        import platform
        
        session_info = {
            "event": "SESSION_START",
            "timestamp": self.start_time.isoformat(),
            "session_id": self.session_id,
            "platform": platform.system(),
            "platform_version": platform.version(),
            "python_version": sys.version,
            "cwd": os.getcwd()
        }
        
        self.actions.append(session_info)
        logger.info("=" * 80)
        logger.info(f"🚀 应用启动 | Session ID: {self.session_id}")
        logger.info(f"📍 Platform: {platform.system()} {platform.version()}")
        logger.info(f"🐍 Python: {sys.version.split()[0]}")
        logger.info("=" * 80)
    
    def log_action(self, action_type, action_name, details=None, success=True):
        """
        Log any application action
        
        Args:
            action_type: Type of action (BUTTON_CLICK, SPIDER, FILE, CONFIG, etc.)
            action_name: Name of the action
            details: Additional details dict
            success: Whether the action succeeded
        """
        action = {
            "event": action_type,
            "action": action_name,
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "details": details or {},
            "thread": threading.current_thread().name
        }
        
        self.actions.append(action)
        
        status = "✅" if success else "❌"
        details_str = json.dumps(details, ensure_ascii=False) if details else ""
        
        if success:
            logger.info(f"{status} [{action_type}] {action_name} | {details_str}")
        else:
            logger.error(f"{status} [{action_type}] {action_name} | {details_str}")
    
    def log_button_click(self, button_name, page_name=None, enabled=True):
        """Log button click event"""
        details = {
            "button": button_name,
            "page": page_name or "unknown",
            "enabled": enabled
        }
        self.log_action("BUTTON_CLICK", button_name, details)
    
    def log_spider_start(self, spider_name, thread_count=1, ads_count=0):
        """Log spider start event"""
        details = {
            "spider": spider_name,
            "thread_count": thread_count,
            "ads_count": ads_count
        }
        self.log_action("SPIDER_START", f"Starting {spider_name}", details)
    
    def log_spider_stop(self, spider_name, reason="user_request"):
        """Log spider stop event"""
        details = {
            "spider": spider_name,
            "reason": reason
        }
        self.log_action("SPIDER_STOP", f"Stopping {spider_name}", details)
    
    def log_spider_progress(self, spider_name, current, total, message=""):
        """Log spider progress"""
        details = {
            "spider": spider_name,
            "current": current,
            "total": total,
            "progress": f"{current}/{total}",
            "message": message
        }
        self.log_action("SPIDER_PROGRESS", f"{spider_name} progress", details)
    
    def log_file_operation(self, operation, file_path, success=True, details=None):
        """Log file operation (create, delete, read, write)"""
        op_details = {
            "operation": operation,
            "file": file_path,
            **(details or {})
        }
        self.log_action("FILE_OP", f"{operation}: {os.path.basename(file_path)}", op_details, success)
    
    def log_config_change(self, section, key, old_value, new_value):
        """Log configuration change"""
        details = {
            "section": section,
            "key": key,
            "old_value": str(old_value)[:100],  # Truncate long values
            "new_value": str(new_value)[:100]
        }
        self.log_action("CONFIG_CHANGE", f"{section}.{key}", details)
    
    def log_browser_action(self, browser_id, action, url=None, success=True):
        """Log browser automation action"""
        details = {
            "browser_id": browser_id,
            "action": action,
            "url": url
        }
        self.log_action("BROWSER", f"{action} on {browser_id}", details, success)
    
    def log_api_call(self, api_name, endpoint, response_code=None, success=True):
        """Log API call (AdsPower, BitBrowser, etc.)"""
        details = {
            "api": api_name,
            "endpoint": endpoint,
            "response_code": response_code
        }
        self.log_action("API_CALL", f"{api_name}: {endpoint}", details, success)
    
    def log_error(self, error_type, message, exception=None, context=None):
        """Log error with full traceback"""
        error = {
            "event": "ERROR",
            "error_type": error_type,
            "message": str(message),
            "timestamp": datetime.now().isoformat(),
            "context": context or {},
            "thread": threading.current_thread().name
        }
        
        if exception:
            error["exception"] = str(exception)
            error["traceback"] = traceback.format_exc()
        
        self.errors.append(error)
        self.actions.append(error)
        
        logger.error(f"❌ [{error_type}] {message}")
        if exception:
            logger.exception(exception)
    
    def log_ui_event(self, event_type, widget_name, details=None):
        """Log UI event (page change, dialog, etc.)"""
        event_details = {
            "event_type": event_type,
            "widget": widget_name,
            **(details or {})
        }
        self.log_action("UI_EVENT", f"{event_type}: {widget_name}", event_details)
    
    def log_validation(self, check_name, passed, message=""):
        """Log validation check result"""
        details = {
            "check": check_name,
            "passed": passed,
            "message": message
        }
        self.log_action("VALIDATION", check_name, details, passed)
    
    def log_message_send(self, member_name, member_link, success=True, reason=""):
        """Log private message send attempt"""
        details = {
            "member_name": member_name,
            "member_link": member_link,
            "reason": reason
        }
        self.log_action("MESSAGE_SEND", f"Message to {member_name}", details, success)
    
    def log_data_collection(self, data_type, count, source=""):
        """Log data collection (groups, members, etc.)"""
        details = {
            "data_type": data_type,
            "count": count,
            "source": source
        }
        self.log_action("DATA_COLLECT", f"Collected {count} {data_type}", details)
    
    def _save_session_log(self):
        """Save complete session log on exit"""
        try:
            end_time = datetime.now()
            duration = (end_time - self.start_time).total_seconds()
            
            session_summary = {
                "session_id": self.session_id,
                "start_time": self.start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": duration,
                "total_actions": len(self.actions),
                "total_errors": len(self.errors),
                "log_file": self.log_file,
                "actions": self.actions,
                "errors": self.errors
            }
            
            # Save JSON log
            with open(self.json_log_file, 'w', encoding='utf-8') as f:
                json.dump(session_summary, f, ensure_ascii=False, indent=2)
            
            logger.info("=" * 80)
            logger.info(f"📊 会话统计 | Session Summary")
            logger.info(f"⏱️  运行时长: {duration:.1f} 秒")
            logger.info(f"📝 总操作数: {len(self.actions)}")
            logger.info(f"❌ 错误数量: {len(self.errors)}")
            logger.info(f"💾 日志已保存: {self.log_file}")
            logger.info(f"📋 JSON日志: {self.json_log_file}")
            logger.info("=" * 80)
            
        except Exception as e:
            print(f"Error saving session log: {e}")
    
    def get_recent_actions(self, count=20):
        """Get recent actions for display"""
        return self.actions[-count:]
    
    def get_errors(self):
        """Get all errors from this session"""
        return self.errors
    
    def export_for_support(self):
        """Export logs in a format suitable for sending to support"""
        export_file = os.path.join(self.log_dir, f'support_export_{self.session_id}.txt')
        
        with open(export_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("SUPPORT LOG EXPORT\n")
            f.write(f"Session: {self.session_id}\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write("=" * 80 + "\n\n")
            
            f.write("ERRORS:\n")
            f.write("-" * 40 + "\n")
            for error in self.errors:
                f.write(f"{error['timestamp']} | {error['error_type']}: {error['message']}\n")
                if 'traceback' in error:
                    f.write(error['traceback'] + "\n")
            
            f.write("\nRECENT ACTIONS:\n")
            f.write("-" * 40 + "\n")
            for action in self.actions[-50:]:
                f.write(f"{action['timestamp']} | [{action['event']}] {action.get('action', '')}\n")
        
        logger.info(f"📤 Support export saved: {export_file}")
        return export_file


# Decorator for logging button clicks
def log_button(button_name, page_name=None):
    """Decorator to log button click events"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            app_logger.log_button_click(button_name, page_name)
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                app_logger.log_error("BUTTON_ERROR", f"Error in {button_name}", e)
                raise
        return wrapper
    return decorator


# Decorator for logging spider methods
def log_spider(spider_name):
    """Decorator to log spider execution"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            app_logger.log_spider_start(spider_name)
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                app_logger.log_error("SPIDER_ERROR", f"Error in {spider_name}", e)
                raise
        return wrapper
    return decorator


# Global instance
app_logger = AppLogger()

