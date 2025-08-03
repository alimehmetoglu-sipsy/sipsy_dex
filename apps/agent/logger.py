#!/usr/bin/env python3
"""
DexAgents Logger - Advanced logging system with rotation and filtering
"""

import logging
import logging.handlers
import os
import sys
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import threading
import queue
import traceback

class Logger:
    def __init__(self, name: str = "DexAgents", log_dir: str = "logs"):
        self.name = name
        self.log_dir = log_dir
        self.log_file = os.path.join(log_dir, "dexagents.log")
        self.error_log_file = os.path.join(log_dir, "dexagents_errors.log")
        
        # Configuration
        self.max_log_size_mb = 10
        self.max_log_files = 5
        self.log_level = logging.INFO
        self.console_output = True
        
        # In-memory log storage for GUI
        self.memory_logs = []
        self.max_memory_logs = 1000
        self.memory_lock = threading.Lock()
        
        # Async logging queue
        self.log_queue = queue.Queue(maxsize=10000)
        self.queue_thread = None
        self.queue_running = False
        
        # Performance metrics
        self.log_stats = {
            'total_logs': 0,
            'debug_logs': 0,
            'info_logs': 0,
            'warning_logs': 0,
            'error_logs': 0,
            'critical_logs': 0,
            'start_time': datetime.now()
        }
        
        # Setup logging
        self._setup_logging()
        
        # Start background thread
        self._start_queue_processor()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        # Create log directory
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(self.log_level)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s() - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # File handler with rotation
        try:
            file_handler = logging.handlers.RotatingFileHandler(
                self.log_file,
                maxBytes=self.max_log_size_mb * 1024 * 1024,
                backupCount=self.max_log_files,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(detailed_formatter)
            self.logger.addHandler(file_handler)
        except Exception as e:
            print(f"Failed to setup file logging: {e}")
        
        # Error file handler
        try:
            error_handler = logging.handlers.RotatingFileHandler(
                self.error_log_file,
                maxBytes=self.max_log_size_mb * 1024 * 1024,
                backupCount=self.max_log_files,
                encoding='utf-8'
            )
            error_handler.setLevel(logging.WARNING)
            error_handler.setFormatter(detailed_formatter)
            self.logger.addHandler(error_handler)
        except Exception as e:
            print(f"Failed to setup error file logging: {e}")
        
        # Console handler
        if self.console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self.log_level)
            console_handler.setFormatter(simple_formatter)
            self.logger.addHandler(console_handler)
        
        # Memory handler for GUI
        memory_handler = MemoryHandler(self)
        memory_handler.setLevel(logging.DEBUG)
        memory_handler.setFormatter(detailed_formatter)
        self.logger.addHandler(memory_handler)
    
    def _start_queue_processor(self):
        """Start background thread for async logging"""
        if self.queue_running:
            return
        
        self.queue_running = True
        
        def process_queue():
            while self.queue_running:
                try:
                    # Get log record from queue with timeout
                    record = self.log_queue.get(timeout=1.0)
                    
                    if record is None:  # Shutdown signal
                        break
                    
                    # Process the log record
                    self.logger.handle(record)
                    
                except queue.Empty:
                    continue
                except Exception as e:
                    # Log errors in queue processing to stderr
                    print(f"Error in log queue processor: {e}", file=sys.stderr)
        
        self.queue_thread = threading.Thread(target=process_queue, daemon=True)
        self.queue_thread.start()
    
    def _stop_queue_processor(self):
        """Stop background queue processor"""
        if not self.queue_running:
            return
        
        self.queue_running = False
        
        # Send shutdown signal
        try:
            self.log_queue.put(None, timeout=1.0)
        except queue.Full:
            pass
        
        # Wait for thread to finish
        if self.queue_thread and self.queue_thread.is_alive():
            self.queue_thread.join(timeout=5.0)
    
    def _log_async(self, level: int, message: str, *args, **kwargs):
        """Log message asynchronously"""
        try:
            # Create log record
            record = self.logger.makeRecord(
                self.logger.name, level, "<unknown>", 0, message, args, None
            )
            
            # Add to queue
            self.log_queue.put(record, block=False)
            
        except queue.Full:
            # If queue is full, log synchronously as fallback
            self._log_sync(level, message, *args, **kwargs)
        except Exception as e:
            print(f"Error in async logging: {e}", file=sys.stderr)
    
    def _log_sync(self, level: int, message: str, *args, **kwargs):
        """Log message synchronously"""
        self.logger.log(level, message, *args, **kwargs)
    
    def _update_stats(self, level: int):
        """Update logging statistics"""
        self.log_stats['total_logs'] += 1
        
        if level == logging.DEBUG:
            self.log_stats['debug_logs'] += 1
        elif level == logging.INFO:
            self.log_stats['info_logs'] += 1
        elif level == logging.WARNING:
            self.log_stats['warning_logs'] += 1
        elif level == logging.ERROR:
            self.log_stats['error_logs'] += 1
        elif level == logging.CRITICAL:
            self.log_stats['critical_logs'] += 1
    
    # Public logging methods
    def debug(self, message: str, *args, **kwargs):
        """Log debug message"""
        self._update_stats(logging.DEBUG)
        self._log_async(logging.DEBUG, message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        """Log info message"""
        self._update_stats(logging.INFO)
        self._log_async(logging.INFO, message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """Log warning message"""
        self._update_stats(logging.WARNING)
        self._log_async(logging.WARNING, message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """Log error message"""
        self._update_stats(logging.ERROR)
        
        # Add stack trace for errors
        if 'exc_info' not in kwargs:
            kwargs['exc_info'] = False
        
        # Include current stack trace in debug mode
        if self.log_level <= logging.DEBUG:
            stack_trace = '\n'.join(traceback.format_stack()[:-1])
            message = f"{message}\nStack trace:\n{stack_trace}"
        
        self._log_async(logging.ERROR, message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        """Log critical message"""
        self._update_stats(logging.CRITICAL)
        self._log_async(logging.CRITICAL, message, *args, **kwargs)
    
    def exception(self, message: str, *args, **kwargs):
        """Log exception with traceback"""
        kwargs['exc_info'] = True
        self.error(message, *args, **kwargs)
    
    def log_performance(self, operation: str, duration: float, success: bool = True, **metadata):
        """Log performance metrics"""
        perf_data = {
            'operation': operation,
            'duration_ms': round(duration * 1000, 2),
            'success': success,
            'timestamp': datetime.now().isoformat(),
            **metadata
        }
        
        level = logging.INFO if success else logging.WARNING
        message = f"Performance: {operation} completed in {perf_data['duration_ms']}ms (success={success})"
        
        # Add metadata to message
        if metadata:
            message += f" - {json.dumps(metadata)}"
        
        self._log_async(level, message)
    
    def log_security_event(self, event_type: str, details: Dict[str, Any], severity: str = "INFO"):
        """Log security-related events"""
        security_data = {
            'event_type': event_type,
            'severity': severity,
            'timestamp': datetime.now().isoformat(),
            'details': details
        }
        
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        
        level = level_map.get(severity, logging.INFO)
        message = f"Security Event: {event_type} - {json.dumps(security_data)}"
        
        self._log_async(level, message)
    
    def set_level(self, level: str):
        """Set logging level"""
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        
        if level in level_map:
            self.log_level = level_map[level]
            self.logger.setLevel(self.log_level)
            
            # Update console handler level
            for handler in self.logger.handlers:
                if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stdout:
                    handler.setLevel(self.log_level)
            
            self.info(f"Log level set to {level}")
        else:
            self.warning(f"Invalid log level: {level}")
    
    def get_recent_logs(self, level: str = "INFO", limit: int = 100) -> List[str]:
        """Get recent log entries from memory"""
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        
        min_level = level_map.get(level, logging.INFO)
        
        with self.memory_lock:
            filtered_logs = [
                log for log in self.memory_logs 
                if log.get('level', logging.INFO) >= min_level
            ]
            
            # Sort by timestamp and get most recent
            filtered_logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            # Format for display
            formatted_logs = []
            for log in filtered_logs[:limit]:
                formatted_logs.append(log.get('formatted', str(log)))
            
            return formatted_logs
    
    def clear_logs(self):
        """Clear log files and memory logs"""
        # Clear memory logs
        with self.memory_lock:
            self.memory_logs.clear()
        
        # Clear file logs
        try:
            # Close file handlers temporarily
            handlers_to_remove = []
            for handler in self.logger.handlers:
                if isinstance(handler, (logging.FileHandler, logging.handlers.RotatingFileHandler)):
                    handlers_to_remove.append(handler)
            
            for handler in handlers_to_remove:
                handler.close()
                self.logger.removeHandler(handler)
            
            # Remove log files
            for log_file in [self.log_file, self.error_log_file]:
                if os.path.exists(log_file):
                    os.remove(log_file)
                
                # Remove rotated log files
                for i in range(1, self.max_log_files + 1):
                    rotated_file = f"{log_file}.{i}"
                    if os.path.exists(rotated_file):
                        os.remove(rotated_file)
            
            # Recreate handlers
            self._setup_logging()
            
            self.info("Log files cleared")
            
        except Exception as e:
            self.error(f"Error clearing log files: {e}")
    
    def export_logs(self, output_file: str, level: str = "INFO", hours: int = 24):
        """Export logs to file"""
        try:
            level_map = {
                'DEBUG': logging.DEBUG,
                'INFO': logging.INFO,
                'WARNING': logging.WARNING,
                'ERROR': logging.ERROR,
                'CRITICAL': logging.CRITICAL
            }
            
            min_level = level_map.get(level, logging.INFO)
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            exported_logs = []
            
            # Export from memory logs first
            with self.memory_lock:
                for log in self.memory_logs:
                    if (log.get('level', logging.INFO) >= min_level and
                        log.get('timestamp_obj', datetime.now()) > cutoff_time):
                        exported_logs.append(log.get('formatted', str(log)))
            
            # Read from log files if needed
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            exported_logs.append(line.strip())
            except (FileNotFoundError, PermissionError):
                pass
            
            # Write to output file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"DexAgents Log Export\n")
                f.write(f"Generated: {datetime.now().isoformat()}\n")
                f.write(f"Level: {level}\n")
                f.write(f"Hours: {hours}\n")
                f.write("-" * 80 + "\n\n")
                
                for log in exported_logs:
                    f.write(log + "\n")
            
            self.info(f"Logs exported to {output_file} ({len(exported_logs)} entries)")
            
        except Exception as e:
            self.error(f"Error exporting logs: {e}")
            raise
    
    def get_log_stats(self) -> Dict[str, Any]:
        """Get logging statistics"""
        runtime = datetime.now() - self.log_stats['start_time']
        
        stats = self.log_stats.copy()
        stats['runtime_seconds'] = runtime.total_seconds()
        stats['logs_per_minute'] = (stats['total_logs'] / (runtime.total_seconds() / 60)) if runtime.total_seconds() > 0 else 0
        stats['memory_logs_count'] = len(self.memory_logs)
        stats['queue_size'] = self.log_queue.qsize()
        stats['queue_running'] = self.queue_running
        
        return stats
    
    def cleanup(self):
        """Cleanup logger resources"""
        self.info("Logger cleanup started")
        
        # Stop queue processor
        self._stop_queue_processor()
        
        # Close all handlers
        for handler in self.logger.handlers:
            try:
                handler.close()
            except Exception as e:
                print(f"Error closing handler: {e}", file=sys.stderr)
        
        self.logger.handlers.clear()
        
        # Clear memory logs
        with self.memory_lock:
            self.memory_logs.clear()

class MemoryHandler(logging.Handler):
    """Custom handler to store logs in memory for GUI display"""
    
    def __init__(self, logger_instance):
        super().__init__()
        self.logger_instance = logger_instance
    
    def emit(self, record):
        try:
            formatted = self.format(record)
            
            log_entry = {
                'level': record.levelno,
                'level_name': record.levelname,
                'message': record.getMessage(),
                'timestamp': datetime.fromtimestamp(record.created).isoformat(),
                'timestamp_obj': datetime.fromtimestamp(record.created),
                'filename': record.filename,
                'lineno': record.lineno,
                'funcName': record.funcName,
                'formatted': formatted
            }
            
            with self.logger_instance.memory_lock:
                self.logger_instance.memory_logs.append(log_entry)
                
                # Limit memory usage
                if len(self.logger_instance.memory_logs) > self.logger_instance.max_memory_logs:
                    self.logger_instance.memory_logs.pop(0)
                    
        except Exception:
            self.handleError(record)

def main():
    """Test logger functionality"""
    logger = Logger("TestLogger", "test_logs")
    
    # Test various log levels
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
    
    # Test performance logging
    start_time = time.time()
    time.sleep(0.1)
    logger.log_performance("test_operation", time.time() - start_time, success=True, param1="value1")
    
    # Test security logging
    logger.log_security_event("login_attempt", {
        "username": "test_user",
        "ip_address": "192.168.1.100",
        "success": True
    }, "INFO")
    
    # Test exception logging
    try:
        raise ValueError("Test exception")
    except Exception:
        logger.exception("Test exception occurred")
    
    # Show stats
    print("\n=== Log Stats ===")
    stats = logger.get_log_stats()
    print(json.dumps(stats, indent=2, default=str))
    
    # Show recent logs
    print("\n=== Recent Logs ===")
    recent_logs = logger.get_recent_logs(level="DEBUG", limit=10)
    for log in recent_logs:
        print(log)
    
    # Cleanup
    logger.cleanup()
    
    # Clean up test directory
    import shutil
    try:
        shutil.rmtree("test_logs")
    except Exception:
        pass

if __name__ == "__main__":
    main()