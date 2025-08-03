#!/usr/bin/env python3
"""
Integration Tests for DexAgent Full Workflow
This module tests the complete end-to-end workflows of the DexAgent system.
"""

import asyncio
import json
import time
import uuid
import pytest
import requests
import websockets
from typing import Dict, Any, List
import psycopg2
from unittest.mock import Mock, patch

# Test configuration
TEST_CONFIG = {
    'backend_url': 'http://localhost:8080',
    'websocket_url': 'ws://localhost:8080/api/v1/ws',
    'database': {
        'host': 'localhost',
        'port': 5433,
        'database': 'dexagent_test',
        'user': 'postgres',
        'password': 'postgres123'
    },
    'test_user': {
        'username': 'admin',
        'password': 'admin123'
    }
}

class DexAgentIntegrationTest:
    """Main integration test class for DexAgent workflows"""
    
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_agent_id = None
        self.websocket = None
        
    def setup_method(self):
        """Setup method called before each test"""
        self.authenticate()
        self.cleanup_test_data()
        
    def teardown_method(self):
        """Cleanup method called after each test"""
        self.cleanup_test_data()
        if self.websocket:
            asyncio.run(self.websocket.close())
            
    def authenticate(self):
        """Authenticate with the API and get JWT token"""
        response = self.session.post(
            f"{TEST_CONFIG['backend_url']}/api/v1/auth/login",
            json=TEST_CONFIG['test_user']
        )
        assert response.status_code == 200
        
        data = response.json()
        self.auth_token = data['access_token']
        self.session.headers.update({
            'Authorization': f'Bearer {self.auth_token}'
        })
        
    def cleanup_test_data(self):
        """Clean up test data from database"""
        try:
            conn = psycopg2.connect(**TEST_CONFIG['database'])
            cursor = conn.cursor()
            
            # Clean up test agents, commands, etc.
            cursor.execute("DELETE FROM command_executions WHERE agent_id LIKE 'test_%'")
            cursor.execute("DELETE FROM agents WHERE id LIKE 'test_%'")
            cursor.execute("DELETE FROM saved_commands WHERE name LIKE 'Test_%'")
            
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Cleanup error: {e}")

class TestAgentRegistrationWorkflow(DexAgentIntegrationTest):
    """Test agent registration and connection workflow"""
    
    def test_agent_registration_complete_workflow(self):
        """Test complete agent registration workflow"""
        
        # Step 1: Simulate agent registration
        agent_data = {
            'id': f'test_agent_{uuid.uuid4().hex[:8]}',
            'name': 'Test Integration Agent',
            'hostname': 'test-machine',
            'ip_address': '192.168.1.100',
            'os': 'Windows 10',
            'version': '1.0.0',
            'capabilities': ['powershell', 'cmd']
        }
        
        # Register agent via WebSocket (simulating real agent)
        async def register_agent():
            uri = f"{TEST_CONFIG['websocket_url']}/agent"
            async with websockets.connect(uri) as websocket:
                # Send registration message
                registration_msg = {
                    'type': 'agent_register',
                    'id': str(uuid.uuid4()),
                    'timestamp': time.time(),
                    'payload': agent_data
                }
                
                await websocket.send(json.dumps(registration_msg))
                
                # Wait for response
                response = await websocket.recv()
                response_data = json.loads(response)
                
                assert response_data['type'] == 'auth_success'
                return response_data
                
        # Run async registration
        registration_result = asyncio.run(register_agent())
        self.test_agent_id = agent_data['id']
        
        # Step 2: Verify agent appears in API
        time.sleep(1)  # Allow time for registration to process
        
        response = self.session.get(f"{TEST_CONFIG['backend_url']}/api/v1/agents")
        assert response.status_code == 200
        
        agents = response.json()
        test_agent = next((a for a in agents if a['id'] == self.test_agent_id), None)
        assert test_agent is not None
        assert test_agent['name'] == agent_data['name']
        assert test_agent['status'] == 'online'
        
        # Step 3: Test agent heartbeat
        async def send_heartbeat():
            uri = f"{TEST_CONFIG['websocket_url']}/agent"
            async with websockets.connect(uri) as websocket:
                heartbeat_msg = {
                    'type': 'agent_heartbeat',
                    'id': str(uuid.uuid4()),
                    'timestamp': time.time(),
                    'payload': {
                        'agent_id': self.test_agent_id,
                        'status': 'idle',
                        'metrics': {
                            'cpu_usage': 25.5,
                            'memory_usage': 60.2,
                            'disk_usage': 45.8
                        }
                    }
                }
                
                await websocket.send(json.dumps(heartbeat_msg))
                
        asyncio.run(send_heartbeat())
        
        # Step 4: Verify agent metrics updated
        time.sleep(1)
        response = self.session.get(f"{TEST_CONFIG['backend_url']}/api/v1/agents/{self.test_agent_id}")
        assert response.status_code == 200
        
        agent_details = response.json()
        assert agent_details['last_seen'] is not None
        
    def test_agent_disconnection_workflow(self):
        """Test agent disconnection and status update"""
        
        # First register an agent
        self.test_agent_registration_complete_workflow()
        
        # Send disconnection message
        async def disconnect_agent():
            uri = f"{TEST_CONFIG['websocket_url']}/agent"
            async with websockets.connect(uri) as websocket:
                disconnect_msg = {
                    'type': 'agent_disconnect',
                    'id': str(uuid.uuid4()),
                    'timestamp': time.time(),
                    'payload': {
                        'agent_id': self.test_agent_id,
                        'reason': 'shutdown'
                    }
                }
                
                await websocket.send(json.dumps(disconnect_msg))
                
        asyncio.run(disconnect_agent())
        
        # Verify agent status updated to offline
        time.sleep(2)
        response = self.session.get(f"{TEST_CONFIG['backend_url']}/api/v1/agents/{self.test_agent_id}")
        assert response.status_code == 200
        
        agent_details = response.json()
        assert agent_details['status'] == 'offline'

class TestCommandExecutionWorkflow(DexAgentIntegrationTest):
    """Test PowerShell command execution workflow"""
    
def setup_method(self):
        super().setup_method()
        # Register a test agent for command testing
        agent_data = {
            'id': f'test_cmd_agent_{uuid.uuid4().hex[:8]}',
            'name': 'Test Command Agent',
            'hostname': 'test-cmd-machine',
            'ip_address': '192.168.1.101',
            'os': 'Windows 10',
            'version': '1.0.0',
            'capabilities': ['powershell', 'cmd']
        }
        
        async def register_test_agent():
            uri = f"{TEST_CONFIG['websocket_url']}/agent"
            async with websockets.connect(uri) as websocket:
                registration_msg = {
                    'type': 'agent_register',
                    'id': str(uuid.uuid4()),
                    'timestamp': time.time(),
                    'payload': agent_data
                }
                await websocket.send(json.dumps(registration_msg))
                response = await websocket.recv()
                return json.loads(response)
                
        asyncio.run(register_test_agent())
        self.test_agent_id = agent_data['id']
        time.sleep(1)  # Allow registration to complete
        
    def test_powershell_command_execution_workflow(self):
        """Test complete PowerShell command execution workflow"""
        
        # Step 1: Create a saved command
        command_data = {
            'name': 'Test_Get_Process_List',
            'command': 'Get-Process | Select-Object -First 5 Name, Id, CPU',
            'description': 'Test command to get process list',
            'category': 'system',
            'timeout': 30
        }
        
        response = self.session.post(
            f"{TEST_CONFIG['backend_url']}/api/v1/commands",
            json=command_data
        )
        assert response.status_code == 201
        command_id = response.json()['id']
        
        # Step 2: Execute command on agent
        execution_data = {
            'command': command_data['command'],
            'timeout': 30,
            'parameters': {}
        }
        
        response = self.session.post(
            f"{TEST_CONFIG['backend_url']}/api/v1/commands/agent/{self.test_agent_id}/execute",
            json=execution_data
        )
        assert response.status_code == 200
        execution_id = response.json()['execution_id']
        
        # Step 3: Simulate agent receiving and processing command
        async def simulate_command_execution():
            uri = f"{TEST_CONFIG['websocket_url']}/agent"
            async with websockets.connect(uri) as websocket:
                # Listen for command
                message = await websocket.recv()
                command_msg = json.loads(message)
                
                assert command_msg['type'] == 'command_execute'
                assert command_msg['payload']['command'] == command_data['command']
                
                # Send command result
                result_msg = {
                    'type': 'command_result',
                    'id': str(uuid.uuid4()),
                    'timestamp': time.time(),
                    'payload': {
                        'execution_id': execution_id,
                        'agent_id': self.test_agent_id,
                        'status': 'completed',
                        'output': 'Name    Id    CPU\n----    --    ---\nexplo   1234  12.5\nchrom   5678  25.3',
                        'error': None,
                        'exit_code': 0,
                        'execution_time': 2.5
                    }
                }
                
                await websocket.send(json.dumps(result_msg))
                
        asyncio.run(simulate_command_execution())
        
        # Step 4: Verify command execution result
        time.sleep(1)
        response = self.session.get(
            f"{TEST_CONFIG['backend_url']}/api/v1/commands/executions/{execution_id}"
        )
        assert response.status_code == 200
        
        execution_result = response.json()
        assert execution_result['status'] == 'completed'
        assert execution_result['exit_code'] == 0
        assert 'explo' in execution_result['output']
        
    def test_command_timeout_workflow(self):
        """Test command timeout handling"""
        
        # Execute a long-running command with short timeout
        execution_data = {
            'command': 'Start-Sleep -Seconds 60',  # 60 second sleep
            'timeout': 5,  # 5 second timeout
            'parameters': {}
        }
        
        response = self.session.post(
            f"{TEST_CONFIG['backend_url']}/api/v1/commands/agent/{self.test_agent_id}/execute",
            json=execution_data
        )
        assert response.status_code == 200
        execution_id = response.json()['execution_id']
        
        # Wait for timeout to occur
        time.sleep(7)
        
        # Verify command marked as timed out
        response = self.session.get(
            f"{TEST_CONFIG['backend_url']}/api/v1/commands/executions/{execution_id}"
        )
        assert response.status_code == 200
        
        execution_result = response.json()
        assert execution_result['status'] == 'timeout'

class TestMetricsCollectionWorkflow(DexAgentIntegrationTest):
    """Test real-time metrics collection workflow"""
    
    def setup_method(self):
        super().setup_method()
        # Register test agent for metrics
        agent_data = {
            'id': f'test_metrics_agent_{uuid.uuid4().hex[:8]}',
            'name': 'Test Metrics Agent',
            'hostname': 'test-metrics-machine',
            'ip_address': '192.168.1.102',
            'os': 'Windows 10',
            'version': '1.0.0',
            'capabilities': ['powershell', 'metrics']
        }
        
        async def register_metrics_agent():
            uri = f"{TEST_CONFIG['websocket_url']}/agent"
            async with websockets.connect(uri) as websocket:
                registration_msg = {
                    'type': 'agent_register',
                    'id': str(uuid.uuid4()),
                    'timestamp': time.time(),
                    'payload': agent_data
                }
                await websocket.send(json.dumps(registration_msg))
                await websocket.recv()
                
        asyncio.run(register_metrics_agent())
        self.test_agent_id = agent_data['id']
        time.sleep(1)
        
    def test_metrics_collection_workflow(self):
        """Test complete metrics collection and storage workflow"""
        
        # Send multiple metric updates
        metrics_data = [
            {
                'timestamp': time.time(),
                'cpu_usage': 25.5,
                'memory_usage': 60.2,
                'disk_usage': 45.8,
                'network_in': 1024,
                'network_out': 2048
            },
            {
                'timestamp': time.time() + 1,
                'cpu_usage': 28.3,
                'memory_usage': 62.1,
                'disk_usage': 45.9,
                'network_in': 1124,
                'network_out': 2148
            },
            {
                'timestamp': time.time() + 2,
                'cpu_usage': 22.1,
                'memory_usage': 58.7,
                'disk_usage': 46.0,
                'network_in': 1224,
                'network_out': 2248
            }
        ]
        
        async def send_metrics():
            uri = f"{TEST_CONFIG['websocket_url']}/agent"
            async with websockets.connect(uri) as websocket:
                for metrics in metrics_data:
                    metrics_msg = {
                        'type': 'agent_metrics',
                        'id': str(uuid.uuid4()),
                        'timestamp': metrics['timestamp'],
                        'payload': {
                            'agent_id': self.test_agent_id,
                            'metrics': metrics
                        }
                    }
                    
                    await websocket.send(json.dumps(metrics_msg))
                    await asyncio.sleep(0.1)  # Small delay between metrics
                    
        asyncio.run(send_metrics())
        
        # Verify metrics stored in database
        time.sleep(2)
        response = self.session.get(
            f"{TEST_CONFIG['backend_url']}/api/v1/agents/{self.test_agent_id}/metrics",
            params={'limit': 10}
        )
        assert response.status_code == 200
        
        stored_metrics = response.json()
        assert len(stored_metrics) >= 3
        
        # Verify metric values
        latest_metric = stored_metrics[0]
        assert latest_metric['cpu_usage'] is not None
        assert latest_metric['memory_usage'] is not None
        assert latest_metric['disk_usage'] is not None

class TestWebSocketCommunication(DexAgentIntegrationTest):
    """Test WebSocket communication patterns"""
    
    def test_websocket_connection_and_messaging(self):
        """Test WebSocket connection establishment and message handling"""
        
        async def test_websocket_flow():
            # Test agent WebSocket connection
            agent_uri = f"{TEST_CONFIG['websocket_url']}/agent"
            async with websockets.connect(agent_uri) as agent_ws:
                
                # Test dashboard WebSocket connection
                dashboard_uri = f"{TEST_CONFIG['websocket_url']}/dashboard"
                async with websockets.connect(dashboard_uri) as dashboard_ws:
                    
                    # Send agent registration
                    agent_data = {
                        'id': f'test_ws_agent_{uuid.uuid4().hex[:8]}',
                        'name': 'Test WebSocket Agent',
                        'hostname': 'test-ws-machine',
                        'ip_address': '192.168.1.103',
                        'os': 'Windows 10',
                        'version': '1.0.0'
                    }
                    
                    registration_msg = {
                        'type': 'agent_register',
                        'id': str(uuid.uuid4()),
                        'timestamp': time.time(),
                        'payload': agent_data
                    }
                    
                    await agent_ws.send(json.dumps(registration_msg))
                    
                    # Verify registration response
                    response = await agent_ws.recv()
                    response_data = json.loads(response)
                    assert response_data['type'] == 'auth_success'
                    
                    # Dashboard should receive agent connection notification
                    dashboard_notification = await dashboard_ws.recv()
                    notification_data = json.loads(dashboard_notification)
                    assert notification_data['type'] == 'agent_connected'
                    assert notification_data['payload']['agent_id'] == agent_data['id']
                    
                    return agent_data['id']
                    
        test_agent_id = asyncio.run(test_websocket_flow())
        self.test_agent_id = test_agent_id
        
    def test_websocket_error_handling(self):
        """Test WebSocket error handling and recovery"""
        
        async def test_error_scenarios():
            uri = f"{TEST_CONFIG['websocket_url']}/agent"
            
            # Test invalid message format
            async with websockets.connect(uri) as websocket:
                await websocket.send("invalid json")
                
                error_response = await websocket.recv()
                error_data = json.loads(error_response)
                assert error_data['type'] == 'error'
                assert 'validation_error' in error_data['payload']['code']
                
            # Test missing required fields
            async with websockets.connect(uri) as websocket:
                invalid_msg = {
                    'type': 'agent_register',
                    # Missing required fields
                }
                
                await websocket.send(json.dumps(invalid_msg))
                
                error_response = await websocket.recv()
                error_data = json.loads(error_response)
                assert error_data['type'] == 'validation_error'
                
        asyncio.run(test_error_scenarios())

class TestSystemHealthAndMonitoring(DexAgentIntegrationTest):
    """Test system health checks and monitoring"""
    
    def test_health_check_endpoints(self):
        """Test system health check endpoints"""
        
        # Test basic health check
        response = self.session.get(f"{TEST_CONFIG['backend_url']}/api/v1/system/health")
        assert response.status_code == 200
        
        health_data = response.json()
        assert health_data['status'] == 'healthy'
        assert 'database' in health_data['checks']
        assert 'websocket' in health_data['checks']
        
    def test_system_info_endpoint(self):
        """Test system information endpoint"""
        
        response = self.session.get(f"{TEST_CONFIG['backend_url']}/api/v1/system/info")
        assert response.status_code == 200
        
        info_data = response.json()
        assert 'version' in info_data
        assert 'uptime' in info_data
        assert 'agents_connected' in info_data

# Test runner configuration
if __name__ == '__main__':
    import sys
    
    # Run with pytest
    sys.exit(pytest.main([__file__, '-v', '--tb=short']))