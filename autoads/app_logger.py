# -*- coding: utf-8 -*-
"""
Application Logger - 应用日志记录系统
Captures ALL application actions, terminal output, and system events
Saves to file for debugging client issues
"""
import os
import sys
import io
import json
import traceback
import functools
from datetime import datetime
from loguru import logger
import threading
import atexit


class TeeOutput:
    """Capture stdout/stderr while still printing to console"""
    def __init__(self, original_stream, log_buffer):
        self.original_stream = original_stream
        self.log_buffer = log_buffer
    
    def write(self, message):
        if message.strip():  # Only log non-empty messages
            self.log_buffer.append({
                "type": "TERMINAL",
                "stream": "stdout" if self.original_stream == sys.__stdout__ else "stderr",
                "message": message.rstrip(),
                "timestamp": datetime.now().isoformat()
            })
        self.original_stream.write(message)
    
    def flush(self):
        self.original_stream.flush()


class AppLogger:
    """
    Comprehensive application logger that captures EVERYTHING:
    - All terminal output (stdout/stderr)
    - Button clicks
    - Spider actions (start, stop, progress)
    - File operations (create, delete, read)
    - Errors and exceptions
    - UI events
    - Configuration changes
    - Browser interactions
    - Network requests
    - Selenium actions
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
        self.default_log_dir = './logs/'
        self.log_file = None
        self.json_log_file = None
        self.actions = []
        self.terminal_output = []
        self.errors = []
        self.start_time = datetime.now()
        self.save_location = None  # User-chosen save location
        self._save_dialog_shown = False
        
        self._setup_logging()
        self._capture_terminal_output()
        self._log_session_start()
    
    def _setup_logging(self):
        """Setup loguru with file and console handlers"""
        # Create default logs directory
        os.makedirs(self.default_log_dir, exist_ok=True)
        
        # Default log file paths
        self.log_file = os.path.join(self.default_log_dir, f'session_{self.session_id}.log')
        self.json_log_file = os.path.join(self.default_log_dir, f'session_{self.session_id}.json')
        
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
    
    def _capture_terminal_output(self):
        """Capture all stdout/stderr output"""
        sys.stdout = TeeOutput(sys.__stdout__, self.terminal_output)
        sys.stderr = TeeOutput(sys.__stderr__, self.terminal_output)
        logger.info("📺 终端输出捕获已启动")
    
    def _log_session_start(self):
        """Log session start information with system details"""
        import platform
        
        session_info = {
            "event": "SESSION_START",
            "timestamp": self.start_time.isoformat(),
            "session_id": self.session_id,
            "system": {
                "platform": platform.system(),
                "platform_version": platform.version(),
                "platform_release": platform.release(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "python_version": sys.version,
                "python_executable": sys.executable,
            },
            "working_directory": os.getcwd(),
            "user": os.environ.get('USER', os.environ.get('USERNAME', 'unknown'))
        }
        
        self.actions.append(session_info)
        logger.info("=" * 80)
        logger.info(f"🚀 应用启动 | Session ID: {self.session_id}")
        logger.info(f"📍 系统: {platform.system()} {platform.release()} ({platform.machine()})")
        logger.info(f"🐍 Python: {sys.version.split()[0]}")
        logger.info(f"📂 工作目录: {os.getcwd()}")
        logger.info(f"👤 用户: {session_info['user']}")
        logger.info("=" * 80)
    
    def log_action(self, action_type, action_name, details=None, success=True):
        """
        Log any application action with full context
        """
        action = {
            "event": action_type,
            "action": action_name,
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "details": details or {},
            "thread": threading.current_thread().name,
            "thread_id": threading.current_thread().ident
        }
        
        self.actions.append(action)
        
        status = "✅" if success else "❌"
        details_str = json.dumps(details, ensure_ascii=False) if details else ""
        
        if success:
            logger.info(f"{status} [{action_type}] {action_name} | {details_str}")
        else:
            logger.error(f"{status} [{action_type}] {action_name} | {details_str}")
    
    def log_button_click(self, button_name, page_name=None, enabled=True):
        """Log button click event with context"""
        details = {
            "button": button_name,
            "page": page_name or "unknown",
            "enabled": enabled,
            "click_time": datetime.now().strftime("%H:%M:%S.%f")[:-3]
        }
        self.log_action("BUTTON_CLICK", button_name, details)
    
    def log_spider_start(self, spider_name, thread_count=1, ads_count=0, config_snapshot=None):
        """Log spider start event with configuration"""
        details = {
            "spider": spider_name,
            "thread_count": thread_count,
            "ads_count": ads_count,
            "start_time": datetime.now().isoformat()
        }
        if config_snapshot:
            details["config"] = config_snapshot
        self.log_action("SPIDER_START", f"Starting {spider_name}", details)
    
    def log_spider_stop(self, spider_name, reason="user_request", duration=None):
        """Log spider stop event"""
        details = {
            "spider": spider_name,
            "reason": reason,
            "stop_time": datetime.now().isoformat()
        }
        if duration:
            details["duration_seconds"] = duration
        self.log_action("SPIDER_STOP", f"Stopping {spider_name}", details)
    
    def log_spider_progress(self, spider_name, current, total, message="", extra_data=None):
        """Log spider progress with percentage"""
        percentage = (current / total * 100) if total > 0 else 0
        details = {
            "spider": spider_name,
            "current": current,
            "total": total,
            "progress": f"{current}/{total}",
            "percentage": f"{percentage:.1f}%",
            "message": message
        }
        if extra_data:
            details.update(extra_data)
        self.log_action("SPIDER_PROGRESS", f"{spider_name} progress", details)
    
    def log_file_operation(self, operation, file_path, success=True, details=None):
        """Log file operation with file info"""
        file_exists = os.path.exists(file_path) if success else False
        file_size = os.path.getsize(file_path) if file_exists else 0
        
        op_details = {
            "operation": operation,
            "file": file_path,
            "file_name": os.path.basename(file_path),
            "file_exists": file_exists,
            "file_size_bytes": file_size,
            **(details or {})
        }
        self.log_action("FILE_OP", f"{operation}: {os.path.basename(file_path)}", op_details, success)
    
    def log_config_change(self, section, key, old_value, new_value):
        """Log configuration change"""
        details = {
            "section": section,
            "key": key,
            "old_value": str(old_value)[:200],
            "new_value": str(new_value)[:200],
            "changed_at": datetime.now().isoformat()
        }
        self.log_action("CONFIG_CHANGE", f"{section}.{key}", details)
    
    def log_browser_action(self, browser_id, action, url=None, success=True, response_time=None):
        """Log browser automation action"""
        details = {
            "browser_id": browser_id,
            "action": action,
            "url": url,
            "response_time_ms": response_time
        }
        self.log_action("BROWSER", f"{action} on {browser_id}", details, success)
    
    def log_selenium_action(self, action, element=None, value=None, success=True, screenshot=None):
        """Log Selenium WebDriver action"""
        details = {
            "action": action,
            "element": element,
            "value": value[:100] if value else None,
            "screenshot": screenshot
        }
        self.log_action("SELENIUM", action, details, success)
    
    def log_api_call(self, api_name, endpoint, method="GET", request_data=None, response_code=None, response_time=None, success=True):
        """Log API call with request/response details"""
        details = {
            "api": api_name,
            "endpoint": endpoint,
            "method": method,
            "request_data": str(request_data)[:500] if request_data else None,
            "response_code": response_code,
            "response_time_ms": response_time
        }
        self.log_action("API_CALL", f"{api_name}: {method} {endpoint}", details, success)
    
    def log_error(self, error_type, message, exception=None, context=None):
        """Log error with full traceback and context"""
        error = {
            "event": "ERROR",
            "error_type": error_type,
            "message": str(message),
            "timestamp": datetime.now().isoformat(),
            "context": context or {},
            "thread": threading.current_thread().name,
            "thread_id": threading.current_thread().ident
        }
        
        if exception:
            error["exception_type"] = type(exception).__name__
            error["exception_message"] = str(exception)
            error["traceback"] = traceback.format_exc()
        
        self.errors.append(error)
        self.actions.append(error)
        
        logger.error(f"❌ [{error_type}] {message}")
        if exception:
            logger.exception(exception)
    
    def log_ui_event(self, event_type, widget_name, details=None):
        """Log UI event"""
        event_details = {
            "event_type": event_type,
            "widget": widget_name,
            "timestamp": datetime.now().isoformat(),
            **(details or {})
        }
        self.log_action("UI_EVENT", f"{event_type}: {widget_name}", event_details)
    
    def log_validation(self, check_name, passed, message="", details=None):
        """Log validation check result"""
        check_details = {
            "check": check_name,
            "passed": passed,
            "message": message,
            **(details or {})
        }
        self.log_action("VALIDATION", check_name, check_details, passed)
    
    def log_message_send(self, member_name, member_link, success=True, reason="", extra_data=None):
        """Log private message send attempt with full details"""
        details = {
            "member_name": member_name,
            "member_link": member_link,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        }
        if extra_data:
            details.update(extra_data)
        self.log_action("MESSAGE_SEND", f"Message to {member_name}", details, success)
    
    def log_data_collection(self, data_type, count, source="", file_path=None):
        """Log data collection"""
        details = {
            "data_type": data_type,
            "count": count,
            "source": source,
            "file_path": file_path
        }
        self.log_action("DATA_COLLECT", f"Collected {count} {data_type}", details)
    
    def log_network_request(self, url, method, status_code=None, response_time=None, error=None):
        """Log network request"""
        details = {
            "url": url,
            "method": method,
            "status_code": status_code,
            "response_time_ms": response_time,
            "error": str(error) if error else None
        }
        success = status_code and 200 <= status_code < 400
        self.log_action("NETWORK", f"{method} {url}", details, success)
    
    def get_session_summary(self):
        """Get complete session summary"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        # Count events by type
        event_counts = {}
        for action in self.actions:
            event_type = action.get('event', 'UNKNOWN')
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        return {
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
            "duration_formatted": f"{int(duration // 60)}m {int(duration % 60)}s",
            "total_actions": len(self.actions),
            "total_errors": len(self.errors),
            "total_terminal_output": len(self.terminal_output),
            "event_counts": event_counts,
            "log_file": self.log_file,
            "json_log_file": self.json_log_file
        }
    
    def save_logs(self, save_path=None):
        """
        Save all logs to specified location
        
        Args:
            save_path: Directory to save logs. If None, uses default ./logs/
        
        Returns:
            tuple: (log_file_path, json_file_path)
        """
        if save_path:
            os.makedirs(save_path, exist_ok=True)
            log_file = os.path.join(save_path, f'session_{self.session_id}.log')
            json_file = os.path.join(save_path, f'session_{self.session_id}.json')
        else:
            log_file = self.log_file
            json_file = self.json_log_file
        
        summary = self.get_session_summary()
        
        session_data = {
            **summary,
            "actions": self.actions,
            "errors": self.errors,
            "terminal_output": self.terminal_output
        }
        
        # Save JSON log
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)
        
        # Also write summary to text log
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write("\n" + "=" * 80 + "\n")
            f.write("📊 SESSION SUMMARY\n")
            f.write("=" * 80 + "\n")
            f.write(f"Session ID: {summary['session_id']}\n")
            f.write(f"Duration: {summary['duration_formatted']}\n")
            f.write(f"Total Actions: {summary['total_actions']}\n")
            f.write(f"Total Errors: {summary['total_errors']}\n")
            f.write(f"Terminal Output Lines: {summary['total_terminal_output']}\n")
            f.write("\nEvent Counts:\n")
            for event_type, count in summary['event_counts'].items():
                f.write(f"  - {event_type}: {count}\n")
            f.write("\n" + "=" * 80 + "\n")
            
            # Write terminal output
            f.write("\n📺 TERMINAL OUTPUT:\n")
            f.write("-" * 40 + "\n")
            for entry in self.terminal_output:
                f.write(f"[{entry['timestamp']}] [{entry['stream']}] {entry['message']}\n")
        
        logger.info(f"💾 日志已保存到: {save_path or self.default_log_dir}")
        
        return log_file, json_file
    
    def show_save_dialog(self):
        """Show dialog to let user choose save location (called from UI)"""
        # This will be called from the main window
        summary = self.get_session_summary()
        return summary
    
    def get_recent_actions(self, count=20):
        """Get recent actions for display"""
        return self.actions[-count:]
    
    def get_errors(self):
        """Get all errors from this session"""
        return self.errors
    
    def export_for_support(self, save_path=None):
        """Export logs in a format suitable for sending to support"""
        if save_path:
            export_file = os.path.join(save_path, f'support_export_{self.session_id}.txt')
        else:
            export_file = os.path.join(self.default_log_dir, f'support_export_{self.session_id}.txt')
        
        with open(export_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("🔧 SUPPORT LOG EXPORT - 技术支持日志导出\n")
            f.write("=" * 80 + "\n")
            f.write(f"Session: {self.session_id}\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write(f"Duration: {self.get_session_summary()['duration_formatted']}\n")
            f.write("=" * 80 + "\n\n")
            
            f.write("❌ ERRORS (错误):\n")
            f.write("-" * 40 + "\n")
            if self.errors:
                for error in self.errors:
                    f.write(f"\n[{error['timestamp']}] {error['error_type']}: {error['message']}\n")
                    if 'traceback' in error:
                        f.write("Traceback:\n")
                        f.write(error['traceback'] + "\n")
            else:
                f.write("No errors recorded.\n")
            
            f.write("\n📋 ALL ACTIONS (所有操作):\n")
            f.write("-" * 40 + "\n")
            for action in self.actions:
                event = action.get('event', 'UNKNOWN')
                action_name = action.get('action', '')
                timestamp = action.get('timestamp', '')
                success = action.get('success', True)
                status = "✅" if success else "❌"
                f.write(f"[{timestamp}] {status} [{event}] {action_name}\n")
                if action.get('details'):
                    f.write(f"    Details: {json.dumps(action['details'], ensure_ascii=False)}\n")
            
            f.write("\n📺 TERMINAL OUTPUT (终端输出):\n")
            f.write("-" * 40 + "\n")
            for entry in self.terminal_output[-100:]:  # Last 100 lines
                f.write(f"[{entry['timestamp']}] {entry['message']}\n")
        
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
