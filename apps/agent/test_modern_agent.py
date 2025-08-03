#!/usr/bin/env python3
"""
Test script for Modern DexAgents Windows Agent
Tests basic functionality without GUI
"""

import sys
import json
import requests
import psutil
import platform
from datetime import datetime
from pathlib import Path

def test_system_info():
    """Test system information collection"""
    print("🔍 Testing system information collection...")
    
    try:
        # Basic system info
        hostname = platform.node()
        os_info = platform.platform()
        python_version = platform.python_version()
        
        # Performance metrics
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        memory_usage = memory.percent
        
        # Disk usage
        disk_usage = {}
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_usage[partition.device] = {
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': (usage.used / usage.total) * 100
                }
            except PermissionError:
                continue
        
        system_info = {
            "hostname": hostname,
            "os_info": os_info,
            "python_version": python_version,
            "cpu_usage": cpu_usage,
            "memory_usage": memory_usage,
            "memory_total": memory.total,
            "memory_available": memory.available,
            "disk_usage": disk_usage,
            "timestamp": datetime.now().isoformat()
        }
        
        print("✅ System information collected successfully")
        print(f"   Hostname: {hostname}")
        print(f"   OS: {os_info}")
        print(f"   CPU Usage: {cpu_usage:.1f}%")
        print(f"   Memory Usage: {memory_usage:.1f}%")
        
        return system_info
        
    except Exception as e:
        print(f"❌ Error collecting system info: {e}")
        return None

def test_config_loading():
    """Test configuration loading"""
    print("\n⚙️ Testing configuration loading...")
    
    default_config = {
        "server_url": "http://localhost:8000",
        "api_token": "",
        "agent_name": f"test_agent_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "tags": ["windows", "test", "modern"],
        "auto_start": True,
        "run_as_service": False,
        "version": "3.0.0",
        "created_at": datetime.now().isoformat(),
        "update_interval": 30,
        "connection_timeout": 10
    }
    
    try:
        # Test saving config
        config_path = Path("test_config.json")
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=4, ensure_ascii=False)
        
        # Test loading config
        with open(config_path, 'r', encoding='utf-8') as f:
            loaded_config = json.load(f)
        
        # Cleanup
        config_path.unlink()
        
        print("✅ Configuration loading/saving works correctly")
        return True
        
    except Exception as e:
        print(f"❌ Error with configuration: {e}")
        return False

def test_network_connectivity():
    """Test network connectivity"""
    print("\n🌐 Testing network connectivity...")
    
    test_urls = [
        "http://localhost:8000",
        "https://httpbin.org/get",
        "https://www.google.com"
    ]
    
    for url in test_urls:
        try:
            response = requests.get(url, timeout=5)
            print(f"✅ {url} - Status: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"❌ {url} - Connection refused")
        except requests.exceptions.Timeout:
            print(f"⏰ {url} - Timeout")
        except Exception as e:
            print(f"❌ {url} - Error: {e}")

def test_dependencies():
    """Test required dependencies"""
    print("\n📦 Testing dependencies...")
    
    required_modules = [
        "tkinter", "requests", "psutil", "json", "threading", 
        "queue", "logging", "datetime", "pathlib", "platform",
        "webbrowser", "subprocess", "shutil", "os", "sys", "time"
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            missing_modules.append(module)
            print(f"❌ {module} - missing")
    
    if missing_modules:
        print(f"\n⚠️ Missing modules: {', '.join(missing_modules)}")
        return False
    else:
        print("✅ All required modules available")
        return True

def test_logging():
    """Test logging functionality"""
    print("\n📝 Testing logging...")
    
    try:
        import logging
        from pathlib import Path
        
        # Setup logging
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "test.log"),
                logging.StreamHandler()
            ]
        )
        
        logger = logging.getLogger(__name__)
        logger.info("Test log message")
        
        print("✅ Logging functionality works")
        return True
        
    except Exception as e:
        print(f"❌ Error with logging: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Modern DexAgents Windows Agent Test Suite")
    print("=" * 50)
    
    tests = [
        ("Dependencies", test_dependencies),
        ("System Information", test_system_info),
        ("Configuration", test_config_loading),
        ("Network Connectivity", test_network_connectivity),
        ("Logging", test_logging)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} test failed: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Modern agent is ready to use.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 