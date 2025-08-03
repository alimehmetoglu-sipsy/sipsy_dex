#!/usr/bin/env python3
"""
DexAgents PowerShell Execution Engine
Secure and robust PowerShell command execution with advanced features
"""

import asyncio
import subprocess
import platform
import os
import sys
import time
import signal
import threading
from datetime import datetime
from typing import Dict, Any, Optional, List
import tempfile
import shlex
import json

class PowerShellExecutor:
    def __init__(self):
        self.is_windows = platform.system() == "Windows"
        self.default_timeout = 30
        self.max_output_size = 10 * 1024 * 1024  # 10MB
        self.active_processes = {}
        self.execution_history = []
        self.max_history_size = 1000
        
        # Import logger
        from logger import Logger
        self.logger = Logger()
        
        # Detect PowerShell availability
        self.powershell_path = self._detect_powershell()
        self.logger.info(f"PowerShell detected: {self.powershell_path}")
        
        # Security settings
        self.restricted_commands = [
            'format',  # Disk formatting
            'del /f /s /q c:',  # Dangerous deletions
            'rd /s /q c:',  # Directory removals
            'shutdown',  # System shutdown
            'restart-computer',
            'remove-item -recurse -force c:',
            'get-credential',  # Credential harvesting
            'invoke-expression',  # Dynamic code execution
            'iex',  # Alias for invoke-expression
            'start-process -verb runas',  # Elevation attempts
        ]
        
        self.blocked_paths = [
            'c:\\windows\\system32',
            'c:\\windows\\syswow64',
            'c:\\program files',
            'c:\\users\\*\\desktop',
        ]
    
    def _detect_powershell(self) -> Optional[str]:
        """Detect available PowerShell executable"""
        if self.is_windows:
            # Try PowerShell Core first (pwsh), then Windows PowerShell
            candidates = [
                'pwsh.exe',  # PowerShell 7+
                'powershell.exe',  # Windows PowerShell 5.1
            ]
            
            for candidate in candidates:
                try:
                    result = subprocess.run(
                        [candidate, '-Command', 'Write-Host "PowerShell Available"'],
                        capture_output=True,
                        timeout=5,
                        text=True
                    )
                    if result.returncode == 0:
                        return candidate
                except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
                    continue
        else:
            # On Linux/Mac, try PowerShell Core
            candidates = ['pwsh', 'powershell']
            
            for candidate in candidates:
                try:
                    result = subprocess.run(
                        [candidate, '-Command', 'Write-Host "PowerShell Available"'],
                        capture_output=True,
                        timeout=5,
                        text=True
                    )
                    if result.returncode == 0:
                        return candidate
                except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
                    continue
        
        # Fallback to system shell
        if self.is_windows:
            return 'cmd.exe'
        else:
            return '/bin/bash'
    
    def _is_command_safe(self, command: str) -> bool:
        """Check if command is safe to execute"""
        command_lower = command.lower().strip()
        
        # Check for restricted commands
        for restricted in self.restricted_commands:
            if restricted in command_lower:
                self.logger.warning(f"Blocked restricted command: {restricted}")
                return False
        
        # Check for dangerous patterns
        dangerous_patterns = [
            'rm -rf /',
            'del /f /s /q',
            'format ',
            'mkfs.',
            'dd if=',
            '> /dev/',
            'chmod 777',
            'chown root',
            'sudo rm',
            'su -',
        ]
        
        for pattern in dangerous_patterns:
            if pattern in command_lower:
                self.logger.warning(f"Blocked dangerous pattern: {pattern}")
                return False
        
        return True
    
    def _sanitize_working_directory(self, working_directory: Optional[str]) -> Optional[str]:
        """Sanitize and validate working directory"""
        if not working_directory:
            return None
        
        try:
            # Resolve absolute path
            abs_path = os.path.abspath(working_directory)
            
            # Check if path exists
            if not os.path.exists(abs_path):
                self.logger.warning(f"Working directory does not exist: {abs_path}")
                return None
            
            # Check if it's a directory
            if not os.path.isdir(abs_path):
                self.logger.warning(f"Working directory is not a directory: {abs_path}")
                return None
            
            # Check against blocked paths
            abs_path_lower = abs_path.lower()
            for blocked in self.blocked_paths:
                if abs_path_lower.startswith(blocked.lower().replace('*', '')):
                    self.logger.warning(f"Blocked access to protected path: {abs_path}")
                    return None
            
            return abs_path
            
        except Exception as e:
            self.logger.error(f"Error sanitizing working directory: {e}")
            return None
    
    def _prepare_command(self, command: str) -> List[str]:
        """Prepare command for execution"""
        if not self.powershell_path:
            raise RuntimeError("No PowerShell executable available")
        
        if self.powershell_path.endswith('.exe') and 'powershell' in self.powershell_path.lower():
            # PowerShell command
            return [
                self.powershell_path,
                '-ExecutionPolicy', 'Bypass',
                '-NoProfile',
                '-NonInteractive',
                '-Command',
                command
            ]
        elif self.powershell_path == 'cmd.exe':
            # Windows CMD fallback
            return ['cmd.exe', '/c', command]
        else:
            # Unix shell
            return [self.powershell_path, '-c', command]
    
    def _create_process_info(self, command: str, process_id: str) -> Dict[str, Any]:
        """Create process tracking information"""
        return {
            'command': command,
            'process_id': process_id,
            'start_time': datetime.now(),
            'status': 'running',
            'pid': None
        }
    
    def _add_to_history(self, execution_result: Dict[str, Any]):
        """Add execution result to history"""
        self.execution_history.append({
            'timestamp': datetime.now().isoformat(),
            'command': execution_result.get('command', ''),
            'success': execution_result.get('success', False),
            'exit_code': execution_result.get('exit_code', -1),
            'execution_time': execution_result.get('execution_time', 0),
            'output_length': len(execution_result.get('output', '')),
            'error_length': len(execution_result.get('error', ''))
        })
        
        # Limit history size
        if len(self.execution_history) > self.max_history_size:
            self.execution_history = self.execution_history[-self.max_history_size:]
    
    def execute_command(self, command: str, timeout: int = None, working_directory: Optional[str] = None) -> Dict[str, Any]:
        """Execute PowerShell command synchronously"""
        try:
            # Use asyncio for consistent execution
            loop = None
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            if loop.is_running():
                # If we're already in an event loop, run in thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run,
                        self.execute_command_async(command, timeout, working_directory)
                    )
                    return future.result()
            else:
                return loop.run_until_complete(
                    self.execute_command_async(command, timeout, working_directory)
                )
                
        except Exception as e:
            self.logger.error(f"Error in synchronous command execution: {e}")
            return {
                'command': command,
                'success': False,
                'output': '',
                'error': str(e),
                'exit_code': -1,
                'execution_time': 0
            }
    
    async def execute_command_async(self, command: str, timeout: int = None, working_directory: Optional[str] = None) -> Dict[str, Any]:
        """Execute PowerShell command asynchronously"""
        start_time = datetime.now()
        process_id = f"{int(time.time())}-{hash(command) % 10000}"
        
        # Default timeout
        if timeout is None:
            timeout = self.default_timeout
        
        # Validate timeout
        timeout = max(1, min(timeout, 300))  # 1 second to 5 minutes
        
        self.logger.info(f"Executing command [{process_id}]: {command[:100]}...")
        
        try:
            # Security check
            if not self._is_command_safe(command):
                return {
                    'command': command,
                    'success': False,
                    'output': '',
                    'error': 'Command blocked by security policy',
                    'exit_code': -1,
                    'execution_time': 0
                }
            
            # Sanitize working directory
            safe_working_dir = self._sanitize_working_directory(working_directory)
            
            # Prepare command
            cmd_args = self._prepare_command(command)
            
            # Track process
            process_info = self._create_process_info(command, process_id)
            self.active_processes[process_id] = process_info
            
            try:
                # Create subprocess
                process = await asyncio.create_subprocess_exec(
                    *cmd_args,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=safe_working_dir,
                    limit=self.max_output_size
                )
                
                process_info['pid'] = process.pid
                
                try:
                    # Wait for completion with timeout
                    stdout, stderr = await asyncio.wait_for(
                        process.communicate(),
                        timeout=timeout
                    )
                    
                    execution_time = (datetime.now() - start_time).total_seconds()
                    
                    # Decode output
                    output = stdout.decode('utf-8', errors='ignore') if stdout else ''
                    error = stderr.decode('utf-8', errors='ignore') if stderr else ''
                    
                    # Truncate if too large
                    if len(output) > self.max_output_size:
                        output = output[:self.max_output_size] + '\n[Output truncated...]'
                    
                    if len(error) > self.max_output_size:
                        error = error[:self.max_output_size] + '\n[Error output truncated...]'
                    
                    result = {
                        'command': command,
                        'success': process.returncode == 0,
                        'output': output,
                        'error': error,
                        'exit_code': process.returncode,
                        'execution_time': execution_time,
                        'working_directory': safe_working_dir,
                        'process_id': process_id
                    }
                    
                    # Log result
                    self.logger.info(f"Command [{process_id}] completed: exit_code={process.returncode}, time={execution_time:.3f}s")
                    
                    # Add to history
                    self._add_to_history(result)
                    
                    return result
                    
                except asyncio.TimeoutError:
                    # Kill process on timeout
                    try:
                        process.kill()
                        await process.wait()
                    except Exception:
                        pass
                    
                    execution_time = timeout
                    
                    result = {
                        'command': command,
                        'success': False,
                        'output': '',
                        'error': f'Command timed out after {timeout} seconds',
                        'exit_code': -1,
                        'execution_time': execution_time,
                        'working_directory': safe_working_dir,
                        'process_id': process_id
                    }
                    
                    self.logger.warning(f"Command [{process_id}] timed out after {timeout}s")
                    self._add_to_history(result)
                    
                    return result
                    
            finally:
                # Clean up process tracking
                if process_id in self.active_processes:
                    del self.active_processes[process_id]
                    
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                'command': command,
                'success': False,
                'output': '',
                'error': str(e),
                'exit_code': -1,
                'execution_time': execution_time,
                'working_directory': safe_working_dir if 'safe_working_dir' in locals() else None,
                'process_id': process_id
            }
            
            self.logger.error(f"Command [{process_id}] failed: {e}")
            self._add_to_history(result)
            
            return result
    
    def kill_process(self, process_id: str) -> bool:
        """Kill a running process by process ID"""
        if process_id not in self.active_processes:
            return False
        
        process_info = self.active_processes[process_id]
        pid = process_info.get('pid')
        
        if not pid:
            return False
        
        try:
            if self.is_windows:
                subprocess.run(['taskkill', '/F', '/PID', str(pid)], check=True)
            else:
                os.kill(pid, signal.SIGTERM)
                time.sleep(1)
                try:
                    os.kill(pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            
            self.logger.info(f"Killed process [{process_id}] with PID {pid}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to kill process [{process_id}]: {e}")
            return False
    
    def get_active_processes(self) -> Dict[str, Dict[str, Any]]:
        """Get information about active processes"""
        return self.active_processes.copy()
    
    def get_execution_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent execution history"""
        return self.execution_history[-limit:] if limit else self.execution_history.copy()
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        if not self.execution_history:
            return {
                'total_executions': 0,
                'successful_executions': 0,
                'failed_executions': 0,
                'success_rate': 0.0,
                'average_execution_time': 0.0
            }
        
        total = len(self.execution_history)
        successful = sum(1 for h in self.execution_history if h.get('success', False))
        failed = total - successful
        success_rate = (successful / total) * 100 if total > 0 else 0.0
        
        total_time = sum(h.get('execution_time', 0) for h in self.execution_history)
        avg_time = total_time / total if total > 0 else 0.0
        
        return {
            'total_executions': total,
            'successful_executions': successful,
            'failed_executions': failed,
            'success_rate': success_rate,
            'average_execution_time': avg_time,
            'active_processes': len(self.active_processes)
        }
    
    def test_powershell_availability(self) -> Dict[str, Any]:
        """Test PowerShell availability and capabilities"""
        test_commands = [
            'Write-Host "PowerShell Test"',
            'Get-Date',
            '$PSVersionTable.PSVersion',
            'Get-ComputerInfo | Select-Object WindowsProductName, TotalPhysicalMemory'
        ]
        
        results = {
            'powershell_path': self.powershell_path,
            'is_available': False,
            'version_info': None,
            'test_results': []
        }
        
        for cmd in test_commands:
            try:
                result = self.execute_command(cmd, timeout=10)
                results['test_results'].append({
                    'command': cmd,
                    'success': result['success'],
                    'output': result['output'][:200],  # Truncate for brevity
                    'execution_time': result['execution_time']
                })
                
                if result['success'] and cmd == '$PSVersionTable.PSVersion':
                    results['version_info'] = result['output'].strip()
                    
            except Exception as e:
                results['test_results'].append({
                    'command': cmd,
                    'success': False,
                    'error': str(e),
                    'execution_time': 0
                })
        
        # Consider available if at least the first test passed
        results['is_available'] = (len(results['test_results']) > 0 and 
                                 results['test_results'][0].get('success', False))
        
        return results

def main():
    """Test PowerShell executor"""
    executor = PowerShellExecutor()
    
    # Test availability
    availability = executor.test_powershell_availability()
    print(f"PowerShell Available: {availability['is_available']}")
    print(f"PowerShell Path: {availability['powershell_path']}")
    
    if availability['version_info']:
        print(f"Version: {availability['version_info']}")
    
    # Test basic command
    result = executor.execute_command('Get-Date')
    print(f"\nTest Command Result:")
    print(f"Success: {result['success']}")
    print(f"Output: {result['output'][:200]}")
    print(f"Execution Time: {result['execution_time']:.3f}s")
    
    # Show stats
    stats = executor.get_execution_stats()
    print(f"\nExecution Stats: {stats}")

if __name__ == "__main__":
    main()