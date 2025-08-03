#!/usr/bin/env python3
"""
DexAgents System Monitor - Comprehensive system monitoring and reporting
"""

import psutil
import platform
import socket
import time
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import os
import subprocess

class SystemMonitor:
    def __init__(self):
        self.monitoring_active = False
        self.monitoring_thread = None
        self.monitoring_interval = 5  # seconds
        self.history_limit = 1000
        
        # Historical data storage
        self.cpu_history = []
        self.memory_history = []
        self.disk_history = []
        self.network_history = []
        
        # System information cache
        self._system_info_cache = None
        self._cache_timestamp = None
        self._cache_duration = 300  # 5 minutes
        
        # Import logger
        from logger import Logger
        self.logger = Logger()
        
        self.logger.info("System monitor initialized")
    
    def get_current_stats(self) -> Dict[str, Any]:
        """Get current system statistics"""
        try:
            # CPU usage
            cpu_usage = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Memory usage
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk usage
            disk_usage = {}
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_usage[partition.mountpoint] = {
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'percentage': round((usage.used / usage.total) * 100, 1)
                    }
                except (PermissionError, OSError):
                    continue
            
            # Network statistics
            network = psutil.net_io_counters()
            network_interfaces = self._get_network_interfaces()
            
            # Process count
            process_count = len(psutil.pids())
            
            # Load average (Unix systems)
            load_avg = None
            try:
                if hasattr(os, 'getloadavg'):
                    load_avg = os.getloadavg()
            except (OSError, AttributeError):
                pass
            
            stats = {
                'timestamp': datetime.now().isoformat(),
                'hostname': socket.gethostname(),
                'cpu': {
                    'usage_percent': cpu_usage,
                    'count': cpu_count,
                    'frequency': cpu_freq._asdict() if cpu_freq else None
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'used': memory.used,
                    'percentage': memory.percent,
                    'swap_total': swap.total,
                    'swap_used': swap.used,
                    'swap_percentage': swap.percent
                },
                'disk': disk_usage,
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv,
                    'interfaces': network_interfaces
                },
                'processes': {
                    'count': process_count
                },
                'load_average': load_avg,
                'uptime_seconds': self._get_uptime()
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting current stats: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def get_detailed_info(self) -> Dict[str, Any]:
        """Get detailed system information with caching"""
        now = time.time()
        
        # Check cache
        if (self._system_info_cache and self._cache_timestamp and 
            (now - self._cache_timestamp) < self._cache_duration):
            return self._system_info_cache
        
        try:
            # Basic system info
            system_info = {
                'timestamp': datetime.now().isoformat(),
                'hostname': socket.gethostname(),
                'platform': {
                    'system': platform.system(),
                    'release': platform.release(),
                    'version': platform.version(),
                    'machine': platform.machine(),
                    'processor': platform.processor(),
                    'architecture': platform.architecture(),
                    'python_version': platform.python_version()
                }
            }
            
            # CPU information
            cpu_info = {
                'physical_cores': psutil.cpu_count(logical=False),
                'logical_cores': psutil.cpu_count(logical=True),
                'max_frequency': None,
                'min_frequency': None,
                'current_frequency': None
            }
            
            cpu_freq = psutil.cpu_freq()
            if cpu_freq:
                cpu_info.update({
                    'max_frequency': cpu_freq.max,
                    'min_frequency': cpu_freq.min,
                    'current_frequency': cpu_freq.current
                })
            
            system_info['cpu'] = cpu_info
            
            # Memory information
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            system_info['memory'] = {
                'total_ram': memory.total,
                'total_swap': swap.total,
                'ram_slots': self._get_memory_slots()
            }
            
            # Disk information
            disk_info = []
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_info.append({
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'filesystem': partition.fstype,
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'percentage': round((usage.used / usage.total) * 100, 1)
                    })
                except (PermissionError, OSError):
                    continue
            
            system_info['disks'] = disk_info
            
            # Network information
            network_info = []
            for interface, addresses in psutil.net_if_addrs().items():
                interface_info = {
                    'interface': interface,
                    'addresses': []
                }
                
                for addr in addresses:
                    interface_info['addresses'].append({
                        'family': str(addr.family),
                        'address': addr.address,
                        'netmask': addr.netmask,
                        'broadcast': addr.broadcast
                    })
                
                # Get interface statistics
                try:
                    stats = psutil.net_if_stats()[interface]
                    interface_info['stats'] = {
                        'is_up': stats.isup,
                        'duplex': str(stats.duplex),
                        'speed': stats.speed,
                        'mtu': stats.mtu
                    }
                except KeyError:
                    pass
                
                network_info.append(interface_info)
            
            system_info['network_interfaces'] = network_info
            
            # Process information
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by CPU usage and get top 10
            processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
            system_info['top_processes'] = processes[:10]
            
            # Windows-specific information
            if platform.system() == 'Windows':
                system_info['windows'] = self._get_windows_info()
            
            # Linux-specific information
            elif platform.system() == 'Linux':
                system_info['linux'] = self._get_linux_info()
            
            # macOS-specific information
            elif platform.system() == 'Darwin':
                system_info['macos'] = self._get_macos_info()
            
            # Boot time and uptime
            boot_time = psutil.boot_time()
            system_info['boot_time'] = datetime.fromtimestamp(boot_time).isoformat()
            system_info['uptime_seconds'] = time.time() - boot_time
            
            # Current stats
            system_info['current_stats'] = self.get_current_stats()
            
            # Cache the result
            self._system_info_cache = system_info
            self._cache_timestamp = now
            
            return system_info
            
        except Exception as e:
            self.logger.error(f"Error getting detailed system info: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def _get_network_interfaces(self) -> List[Dict[str, Any]]:
        """Get network interface information"""
        interfaces = []
        
        try:
            for interface, stats in psutil.net_if_stats().items():
                interface_info = {
                    'name': interface,
                    'is_up': stats.isup,
                    'duplex': str(stats.duplex),
                    'speed': stats.speed,
                    'mtu': stats.mtu
                }
                
                # Get IP addresses
                addresses = psutil.net_if_addrs().get(interface, [])
                interface_info['addresses'] = []
                
                for addr in addresses:
                    if addr.family == socket.AF_INET:  # IPv4
                        interface_info['addresses'].append({
                            'type': 'IPv4',
                            'address': addr.address,
                            'netmask': addr.netmask
                        })
                    elif addr.family == socket.AF_INET6:  # IPv6
                        interface_info['addresses'].append({
                            'type': 'IPv6',
                            'address': addr.address
                        })
                
                interfaces.append(interface_info)
                
        except Exception as e:
            self.logger.error(f"Error getting network interfaces: {e}")
        
        return interfaces
    
    def _get_memory_slots(self) -> Optional[int]:
        """Get number of memory slots (Windows only)"""
        if platform.system() != 'Windows':
            return None
        
        try:
            result = subprocess.run(
                ['wmic', 'memorychip', 'get', 'capacity'],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\\n')
                # Count non-empty lines excluding header
                slots = len([line for line in lines[1:] if line.strip()])
                return slots
                
        except Exception as e:
            self.logger.debug(f"Could not get memory slots: {e}")
        
        return None
    
    def _get_windows_info(self) -> Dict[str, Any]:
        """Get Windows-specific system information"""
        windows_info = {}
        
        try:
            # Windows version
            result = subprocess.run(
                ['wmic', 'os', 'get', 'Caption,Version,BuildNumber', '/format:csv'],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\\n')
                if len(lines) > 1:
                    parts = lines[1].split(',')
                    if len(parts) >= 4:
                        windows_info['build_number'] = parts[1]
                        windows_info['caption'] = parts[2]
                        windows_info['version'] = parts[3]
            
            # System manufacturer and model
            result = subprocess.run(
                ['wmic', 'computersystem', 'get', 'Manufacturer,Model', '/format:csv'],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\\n')
                if len(lines) > 1:
                    parts = lines[1].split(',')
                    if len(parts) >= 3:
                        windows_info['manufacturer'] = parts[1]
                        windows_info['model'] = parts[2]
            
            # Windows services
            windows_info['services'] = self._get_windows_services()
            
        except Exception as e:
            self.logger.error(f"Error getting Windows info: {e}")
        
        return windows_info
    
    def _get_windows_services(self) -> List[Dict[str, Any]]:
        """Get Windows services information"""
        services = []
        
        try:
            for service in psutil.win_service_iter():
                try:
                    service_info = service.as_dict()
                    services.append({
                        'name': service_info.get('name'),
                        'display_name': service_info.get('display_name'),
                        'status': service_info.get('status')
                    })
                except Exception:
                    continue
        except (AttributeError, OSError):
            # Not on Windows or no access
            pass
        except Exception as e:
            self.logger.error(f"Error getting Windows services: {e}")
        
        return services[:20]  # Limit to first 20 services
    
    def _get_linux_info(self) -> Dict[str, Any]:
        """Get Linux-specific system information"""
        linux_info = {}
        
        try:
            # Distribution information
            if os.path.exists('/etc/os-release'):
                with open('/etc/os-release', 'r') as f:
                    for line in f:
                        if line.startswith('PRETTY_NAME='):
                            linux_info['distribution'] = line.split('=')[1].strip('"\\n')
                            break
            
            # Kernel version
            linux_info['kernel'] = platform.release()
            
            # Load average
            if hasattr(os, 'getloadavg'):
                linux_info['load_average'] = os.getloadavg()
            
            # Memory information from /proc/meminfo
            if os.path.exists('/proc/meminfo'):
                with open('/proc/meminfo', 'r') as f:
                    meminfo = {}
                    for line in f:
                        parts = line.split(':')
                        if len(parts) == 2:
                            key = parts[0].strip()
                            value = parts[1].strip().split()[0]
                            if value.isdigit():
                                meminfo[key] = int(value) * 1024  # Convert KB to bytes
                    linux_info['meminfo'] = meminfo
            
        except Exception as e:
            self.logger.error(f"Error getting Linux info: {e}")
        
        return linux_info
    
    def _get_macos_info(self) -> Dict[str, Any]:
        """Get macOS-specific system information"""
        macos_info = {}
        
        try:
            # macOS version
            result = subprocess.run(
                ['sw_vers', '-productVersion'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                macos_info['version'] = result.stdout.strip()
            
            # Hardware information
            result = subprocess.run(
                ['system_profiler', 'SPHardwareDataType'],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                # Parse hardware info (simplified)
                lines = result.stdout.split('\\n')
                for line in lines:
                    if 'Model Name:' in line:
                        macos_info['model_name'] = line.split(':')[1].strip()
                    elif 'Processor Name:' in line:
                        macos_info['processor_name'] = line.split(':')[1].strip()
                    elif 'Memory:' in line:
                        macos_info['memory'] = line.split(':')[1].strip()
            
        except Exception as e:
            self.logger.error(f"Error getting macOS info: {e}")
        
        return macos_info
    
    def _get_uptime(self) -> float:
        """Get system uptime in seconds"""
        try:
            return time.time() - psutil.boot_time()
        except Exception:
            return 0.0
    
    def start_monitoring(self, interval: int = 5):
        """Start background monitoring"""
        if self.monitoring_active:
            return
        
        self.monitoring_interval = max(1, interval)
        self.monitoring_active = True
        
        def monitoring_loop():
            while self.monitoring_active:
                try:
                    stats = self.get_current_stats()
                    timestamp = datetime.now()
                    
                    # Store in history
                    self.cpu_history.append({
                        'timestamp': timestamp,
                        'value': stats['cpu']['usage_percent']
                    })
                    
                    self.memory_history.append({
                        'timestamp': timestamp,
                        'value': stats['memory']['percentage']
                    })
                    
                    # Disk usage (average of all drives)
                    disk_avg = 0
                    if stats['disk']:
                        disk_avg = sum(d['percentage'] for d in stats['disk'].values()) / len(stats['disk'])
                    
                    self.disk_history.append({
                        'timestamp': timestamp,
                        'value': disk_avg
                    })
                    
                    # Network I/O
                    self.network_history.append({
                        'timestamp': timestamp,
                        'bytes_sent': stats['network']['bytes_sent'],
                        'bytes_recv': stats['network']['bytes_recv']
                    })
                    
                    # Limit history size
                    self._trim_history()
                    
                except Exception as e:
                    self.logger.error(f"Error in monitoring loop: {e}")
                
                time.sleep(self.monitoring_interval)
        
        self.monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        self.logger.info(f"System monitoring started (interval: {self.monitoring_interval}s)")
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        if not self.monitoring_active:
            return
        
        self.monitoring_active = False
        
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5)
        
        self.logger.info("System monitoring stopped")
    
    def _trim_history(self):
        """Trim history to prevent memory bloat"""
        for history in [self.cpu_history, self.memory_history, self.disk_history, self.network_history]:
            if len(history) > self.history_limit:
                history[:] = history[-self.history_limit:]
    
    def get_monitoring_history(self, hours: int = 1) -> Dict[str, List[Dict[str, Any]]]:
        """Get monitoring history for the specified hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        def filter_history(history):
            return [item for item in history if item['timestamp'] > cutoff_time]
        
        return {
            'cpu': filter_history(self.cpu_history),
            'memory': filter_history(self.memory_history),
            'disk': filter_history(self.disk_history),
            'network': filter_history(self.network_history)
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        if not self.cpu_history:
            return {'error': 'No monitoring data available'}
        
        # Calculate averages from recent history
        recent_cpu = [item['value'] for item in self.cpu_history[-60:]]  # Last 60 samples
        recent_memory = [item['value'] for item in self.memory_history[-60:]]
        recent_disk = [item['value'] for item in self.disk_history[-60:]]
        
        return {
            'timestamp': datetime.now().isoformat(),
            'cpu': {
                'current': recent_cpu[-1] if recent_cpu else 0,
                'average': sum(recent_cpu) / len(recent_cpu) if recent_cpu else 0,
                'max': max(recent_cpu) if recent_cpu else 0,
                'min': min(recent_cpu) if recent_cpu else 0
            },
            'memory': {
                'current': recent_memory[-1] if recent_memory else 0,
                'average': sum(recent_memory) / len(recent_memory) if recent_memory else 0,
                'max': max(recent_memory) if recent_memory else 0,
                'min': min(recent_memory) if recent_memory else 0
            },
            'disk': {
                'current': recent_disk[-1] if recent_disk else 0,
                'average': sum(recent_disk) / len(recent_disk) if recent_disk else 0,
                'max': max(recent_disk) if recent_disk else 0,
                'min': min(recent_disk) if recent_disk else 0
            },
            'monitoring_active': self.monitoring_active,
            'sample_count': len(self.cpu_history),
            'uptime_hours': round(self._get_uptime() / 3600, 1)
        }

def main():
    """Test system monitor"""
    monitor = SystemMonitor()
    
    print("=== Current Stats ===")
    stats = monitor.get_current_stats()
    print(json.dumps(stats, indent=2, default=str))
    
    print("\\n=== Performance Summary ===")
    # Start monitoring briefly
    monitor.start_monitoring(1)
    time.sleep(5)
    
    summary = monitor.get_performance_summary()
    print(json.dumps(summary, indent=2, default=str))
    
    monitor.stop_monitoring()
    
    print("\\n=== System Info (Basic) ===")
    info = monitor.get_detailed_info()
    # Print only basic info to avoid too much output
    basic_info = {
        'hostname': info.get('hostname'),
        'platform': info.get('platform'),
        'cpu': info.get('cpu'),
        'memory': info.get('memory'),
        'uptime_seconds': info.get('uptime_seconds')
    }
    print(json.dumps(basic_info, indent=2, default=str))

if __name__ == "__main__":
    main()