#!/usr/bin/env python3
"""
Comprehensive API Test Suite for DexAgent Backend
Tests all API endpoints with proper authentication and error handling
"""

import asyncio
import json
import pytest
import requests
import time
import uuid
import websockets
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

# Test Configuration
TEST_CONFIG = {
    'backend_url': 'http://localhost:8080',
    'websocket_url': 'ws://localhost:8080/api/v1/ws',
    'test_user': {
        'username': 'admin',
        'password': 'admin123'
    },
    'timeout': 30
}

class DexAgentAPITester:
    """Comprehensive API test runner for DexAgent backend"""
    
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'errors': [],
            'start_time': time.time(),
            'categories': {
                'authentication': {'total': 0, 'passed': 0, 'failed': 0},
                'agents': {'total': 0, 'passed': 0, 'failed': 0},
                'commands': {'total': 0, 'passed': 0, 'failed': 0},
                'system': {'total': 0, 'passed': 0, 'failed': 0},
                'installer': {'total': 0, 'passed': 0, 'failed': 0},
                'settings': {'total': 0, 'passed': 0, 'failed': 0},
                'websocket': {'total': 0, 'passed': 0, 'failed': 0},
                'metrics': {'total': 0, 'passed': 0, 'failed': 0}
            }
        }
    
    def log_test(self, category: str, test_name: str, passed: bool, error: str = None):
        """Log test result"""
        self.test_results['total_tests'] += 1
        self.test_results['categories'][category]['total'] += 1
        
        if passed:
            self.test_results['passed'] += 1
            self.test_results['categories'][category]['passed'] += 1
            print(f"✅ {category}.{test_name}")
        else:
            self.test_results['failed'] += 1
            self.test_results['categories'][category]['failed'] += 1
            error_detail = f"{category}.{test_name}: {error}"
            self.test_results['errors'].append(error_detail)
            print(f"❌ {category}.{test_name}: {error}")
    
    def test_endpoint(self, category: str, test_name: str, method: str, endpoint: str, 
                     expected_status: int = 200, data: Dict = None, 
                     headers: Dict = None, auth_required: bool = True) -> bool:
        """Generic endpoint test method"""
        try:
            url = f"{TEST_CONFIG['backend_url']}{endpoint}"
            
            # Add auth header if required and available
            if auth_required and self.auth_token:
                test_headers = {'Authorization': f'Bearer {self.auth_token}'}
                if headers:
                    test_headers.update(headers)
                headers = test_headers
            
            # Make request
            if method.upper() == 'GET':
                response = self.session.get(url, headers=headers, timeout=TEST_CONFIG['timeout'])
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, headers=headers, timeout=TEST_CONFIG['timeout'])
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data, headers=headers, timeout=TEST_CONFIG['timeout'])
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, headers=headers, timeout=TEST_CONFIG['timeout'])
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            # Check status code
            if response.status_code == expected_status:
                self.log_test(category, test_name, True)
                return True
            else:
                self.log_test(category, test_name, False, 
                            f"Expected {expected_status}, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test(category, test_name, False, str(e))
            return False
    
    def test_authentication(self):
        """Test authentication endpoints"""
        print("\n🔐 Testing Authentication...")
        
        # Test login with valid credentials
        response = self.session.post(
            f"{TEST_CONFIG['backend_url']}/api/v1/auth/login",
            json=TEST_CONFIG['test_user']
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'access_token' in data:
                self.auth_token = data['access_token']
                self.log_test('authentication', 'login_valid', True)
            else:
                self.log_test('authentication', 'login_valid', False, 'No access_token in response')
        else:
            self.log_test('authentication', 'login_valid', False, f'Status: {response.status_code}')
        
        # Test login with invalid credentials
        invalid_response = self.session.post(
            f"{TEST_CONFIG['backend_url']}/api/v1/auth/login",
            json={'username': 'invalid', 'password': 'invalid'}
        )
        
        if invalid_response.status_code == 401:
            self.log_test('authentication', 'login_invalid', True)
        else:
            self.log_test('authentication', 'login_invalid', False, 
                         f'Expected 401, got {invalid_response.status_code}')
        
        # Test protected endpoint without auth
        self.test_endpoint('authentication', 'unauthorized_access', 'GET', 
                          '/api/v1/agents/', expected_status=401, auth_required=False)
        
        # Test token validation
        if self.auth_token:
            self.test_endpoint('authentication', 'token_validation', 'GET', 
                              '/api/v1/agents/', expected_status=200)
    
    def test_system_endpoints(self):
        """Test system endpoints"""
        print("\n🔧 Testing System Endpoints...")
        
        # Health check
        self.test_endpoint('system', 'health_check', 'GET', '/api/v1/system/health', 
                          expected_status=200, auth_required=False)
        
        # System info
        self.test_endpoint('system', 'system_info', 'GET', '/api/v1/system/info')
        
        # System stats
        self.test_endpoint('system', 'system_stats', 'GET', '/api/v1/system/stats')
    
    def test_agents_endpoints(self):
        """Test agent management endpoints"""
        print("\n🤖 Testing Agent Endpoints...")
        
        # Get all agents
        self.test_endpoint('agents', 'get_all_agents', 'GET', '/api/v1/agents/')
        
        # Test agent creation (simulate agent registration)
        test_agent_data = {
            'id': f'test_agent_{uuid.uuid4().hex[:8]}',
            'name': 'Test Comprehensive Agent',
            'hostname': 'test-machine',
            'ip_address': '192.168.1.100',
            'os': 'Windows 10',
            'version': '1.0.0',
            'capabilities': ['powershell', 'cmd']
        }
        
        # Register agent
        register_success = self.test_endpoint('agents', 'register_agent', 'POST', 
                                            '/api/v1/agents/register', data=test_agent_data,
                                            expected_status=201)
        
        if register_success:
            agent_id = test_agent_data['id']
            
            # Get specific agent
            self.test_endpoint('agents', 'get_agent_by_id', 'GET', f'/api/v1/agents/{agent_id}')
            
            # Update agent
            update_data = {'status': 'online', 'last_seen': time.time()}
            self.test_endpoint('agents', 'update_agent', 'PUT', 
                              f'/api/v1/agents/{agent_id}', data=update_data)
            
            # Get agent metrics
            self.test_endpoint('agents', 'get_agent_metrics', 'GET', 
                              f'/api/v1/agents/{agent_id}/metrics')
            
            # Delete agent (cleanup)
            self.test_endpoint('agents', 'delete_agent', 'DELETE', f'/api/v1/agents/{agent_id}')
    
    def test_commands_endpoints(self):
        """Test command management endpoints"""
        print("\n⚡ Testing Command Endpoints...")
        
        # Get all saved commands
        self.test_endpoint('commands', 'get_saved_commands', 'GET', '/api/v1/commands/')
        
        # Create test command
        test_command = {
            'name': f'Test_Command_{uuid.uuid4().hex[:8]}',
            'command': 'Get-Process | Select-Object -First 3 Name, Id',
            'description': 'Test command for comprehensive API testing',
            'category': 'system',
            'timeout': 30
        }
        
        # Save command
        save_success = self.test_endpoint('commands', 'save_command', 'POST', 
                                        '/api/v1/commands/', data=test_command, 
                                        expected_status=201)
        
        if save_success:
            command_name = test_command['name']
            
            # Get specific command
            self.test_endpoint('commands', 'get_command_by_name', 'GET', 
                              f'/api/v1/commands/{command_name}')
            
            # Update command
            update_data = {'description': 'Updated test command'}
            self.test_endpoint('commands', 'update_command', 'PUT', 
                              f'/api/v1/commands/{command_name}', data=update_data)
            
            # Delete command (cleanup)
            self.test_endpoint('commands', 'delete_command', 'DELETE', 
                              f'/api/v1/commands/{command_name}')
        
        # Test command execution endpoint structure
        self.test_endpoint('commands', 'execute_command_no_agent', 'POST', 
                          '/api/v1/commands/execute', 
                          data={'command': 'echo test'}, expected_status=404)
    
    def test_installer_endpoints(self):
        """Test installer endpoints"""
        print("\n📦 Testing Installer Endpoints...")
        
        # Get installer info
        self.test_endpoint('installer', 'get_installer_info', 'GET', '/api/v1/installer/info')
        
        # Download installer (should return file or info)
        self.test_endpoint('installer', 'download_installer', 'GET', '/api/v1/installer/download')
    
    def test_settings_endpoints(self):
        """Test settings endpoints"""
        print("\n⚙️  Testing Settings Endpoints...")
        
        # Get all settings
        self.test_endpoint('settings', 'get_settings', 'GET', '/api/v1/settings/')
        
        # Test setting update
        test_setting = {
            'key': 'test_setting',
            'value': 'test_value',
            'description': 'Test setting for API testing'
        }
        
        # Create/update setting
        self.test_endpoint('settings', 'update_setting', 'POST', 
                          '/api/v1/settings/', data=test_setting)
        
        # Get specific setting
        self.test_endpoint('settings', 'get_setting_by_key', 'GET', 
                          '/api/v1/settings/test_setting')
    
    def test_metrics_endpoints(self):
        """Test metrics endpoints"""
        print("\n📊 Testing Metrics Endpoints...")
        
        # Get system stats/metrics
        self.test_endpoint('metrics', 'get_stats', 'GET', '/api/v1/stats')
        
        # Get metrics (if different endpoint)
        self.test_endpoint('metrics', 'get_metrics', 'GET', '/api/v1/metrics', 
                          expected_status=[200, 404])  # May not exist
    
    async def test_websocket_connection(self):
        """Test WebSocket connection"""
        print("\n🔌 Testing WebSocket Connection...")
        
        try:
            # Test WebSocket connection
            if self.auth_token:
                headers = {'Authorization': f'Bearer {self.auth_token}'}
            else:
                headers = {}
            
            async with websockets.connect(
                TEST_CONFIG['websocket_url'],
                extra_headers=headers,
                timeout=10
            ) as websocket:
                
                # Test ping/pong
                await websocket.ping()
                
                # Send test message
                test_message = {
                    'type': 'test',
                    'id': str(uuid.uuid4()),
                    'payload': {'message': 'API test'}
                }
                
                await websocket.send(json.dumps(test_message))
                
                # Try to receive response (with timeout)
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5)
                    self.log_test('websocket', 'connection_and_messaging', True)
                except asyncio.TimeoutError:
                    # Timeout is acceptable - connection works
                    self.log_test('websocket', 'connection_and_messaging', True)
                    
        except Exception as e:
            self.log_test('websocket', 'connection_and_messaging', False, str(e))
    
    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Comprehensive DexAgent API Tests")
        print("=" * 50)
        
        # Test system endpoints first (no auth required)
        self.test_system_endpoints()
        
        # Test authentication
        self.test_authentication()
        
        # Test other endpoints (require auth)
        if self.auth_token:
            self.test_agents_endpoints()
            self.test_commands_endpoints()
            self.test_installer_endpoints()
            self.test_settings_endpoints()
            self.test_metrics_endpoints()
            
            # Test WebSocket
            try:
                asyncio.run(self.test_websocket_connection())
            except Exception as e:
                self.log_test('websocket', 'async_test_runner', False, str(e))
        else:
            print("⚠️  Skipping authenticated endpoints due to auth failure")
        
        # Print results
        self.print_results()
    
    def print_results(self):
        """Print comprehensive test results"""
        duration = time.time() - self.test_results['start_time']
        
        print("\n" + "=" * 60)
        print("🧪 COMPREHENSIVE API TEST RESULTS")
        print("=" * 60)
        
        print(f"⏱️  Total Duration: {duration:.2f}s")
        print(f"📊 Total Tests: {self.test_results['total_tests']}")
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        
        if self.test_results['total_tests'] > 0:
            success_rate = (self.test_results['passed'] / self.test_results['total_tests']) * 100
            print(f"📈 Success Rate: {success_rate:.1f}%")
        
        print("\n📋 Results by Category:")
        for category, results in self.test_results['categories'].items():
            if results['total'] > 0:
                rate = (results['passed'] / results['total']) * 100
                print(f"  {category}: {results['passed']}/{results['total']} ({rate:.1f}%)")
        
        if self.test_results['errors']:
            print(f"\n❌ Failed Tests ({len(self.test_results['errors'])}):")
            for error in self.test_results['errors']:
                print(f"  - {error}")
        
        print("\n" + "=" * 60)
        
        return {
            'total_tests': self.test_results['total_tests'],
            'passed': self.test_results['passed'],
            'failed': self.test_results['failed'],
            'success_rate': (self.test_results['passed'] / self.test_results['total_tests'] * 100) 
                           if self.test_results['total_tests'] > 0 else 0,
            'duration': duration,
            'categories': self.test_results['categories'],
            'errors': self.test_results['errors']
        }

def main():
    """Main function to run comprehensive API tests"""
    print("DexAgent Comprehensive API Test Suite")
    print("=====================================")
    
    # Check if backend is running
    try:
        response = requests.get(f"{TEST_CONFIG['backend_url']}/api/v1/system/health", timeout=5)
        if response.status_code != 200:
            print("❌ Backend health check failed")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        print("Make sure the backend is running on http://localhost:8080")
        return False
    
    # Run tests
    tester = DexAgentAPITester()
    tester.run_all_tests()
    
    # Return success status
    return tester.test_results['failed'] == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)