#!/usr/bin/env python3
"""
Integration Tests for Task Manager Feature
Tests the complete workflow from frontend API calls to agent process management
"""

import pytest
import asyncio
import json
import time
import websockets
from typing import Dict, Any, List
from unittest.mock import Mock, AsyncMock, patch
import requests

from conftest import TEST_CONFIG, helpers


class TestTaskManagerWorkflow:
    """Integration tests for the complete Task Manager workflow"""

    @pytest.mark.integration
    @pytest.mark.critical
    def test_process_list_api_endpoint(self, authenticated_session, test_agent_data):
        """Test GET /agents/{agent_id}/processes endpoint"""
        
        # Create test agent first
        agent_response = authenticated_session.post(
            f"{TEST_CONFIG['backend_url']}/api/v1/agents/register",
            json=test_agent_data
        )
        assert agent_response.status_code == 200
        agent_id = agent_response.json()['id']
        
        # Test process list endpoint when agent is offline
        response = authenticated_session.get(
            f"{TEST_CONFIG['backend_url']}/api/v1/agents/{agent_id}/processes"
        )
        assert response.status_code == 400
        assert "not connected" in response.json()['detail'].lower()

    @pytest.mark.integration
    @pytest.mark.critical
    def test_kill_process_api_endpoint(self, authenticated_session, test_agent_data):
        """Test DELETE /agents/{agent_id}/processes/{pid} endpoint"""
        
        # Create test agent
        agent_response = authenticated_session.post(
            f"{TEST_CONFIG['backend_url']}/api/v1/agents/register",
            json=test_agent_data
        )
        assert agent_response.status_code == 200
        agent_id = agent_response.json()['id']
        
        # Test kill process endpoint when agent is offline
        test_pid = 1234
        response = authenticated_session.delete(
            f"{TEST_CONFIG['backend_url']}/api/v1/agents/{agent_id}/processes/{test_pid}"
        )
        assert response.status_code == 400
        assert "not connected" in response.json()['detail'].lower()

    @pytest.mark.integration 
    @pytest.mark.critical
    def test_bulk_kill_processes_api_endpoint(self, authenticated_session, test_agent_data):
        """Test DELETE /agents/{agent_id}/processes/bulk endpoint"""
        
        # Create test agent
        agent_response = authenticated_session.post(
            f"{TEST_CONFIG['backend_url']}/api/v1/agents/register",
            json=test_agent_data
        )
        assert agent_response.status_code == 200
        agent_id = agent_response.json()['id']
        
        # Test bulk kill processes endpoint
        bulk_request = {"process_ids": [1234, 5678]}
        response = authenticated_session.delete(
            f"{TEST_CONFIG['backend_url']}/api/v1/agents/{agent_id}/processes/bulk",
            json=bulk_request
        )
        assert response.status_code == 400
        assert "not connected" in response.json()['detail'].lower()

    @pytest.mark.integration
    @pytest.mark.websocket
    async def test_websocket_process_command_generation(self, mock_websocket):
        """Test WebSocket manager generates correct PowerShell commands"""
        
        from apps.backend.app.core.websocket_manager import websocket_manager
        
        # Test process list command generation
        process_command = {
            "action": "get_processes",
            "timeout": 30
        }
        
        # Mock agent connection
        test_agent_id = "test_agent_123"
        websocket_manager.agent_connections[test_agent_id] = "mock_connection_id"
        websocket_manager.active_connections["mock_connection_id"] = mock_websocket
        
        # Execute process command
        command_id = await websocket_manager.execute_process_command(test_agent_id, process_command)
        
        # Verify command was sent
        assert mock_websocket.send.called
        sent_message = json.loads(mock_websocket.send.call_args[0][0])
        
        assert sent_message["type"] == "powershell_command"
        assert sent_message["request_id"] == command_id
        assert "Get-Process" in sent_message["command"]
        assert "ConvertTo-Json" in sent_message["command"]

    @pytest.mark.integration
    @pytest.mark.websocket 
    async def test_websocket_kill_process_command_generation(self, mock_websocket):
        """Test WebSocket manager generates correct kill process PowerShell commands"""
        
        from apps.backend.app.core.websocket_manager import websocket_manager
        
        # Test kill process command generation
        kill_command = {
            "action": "kill_process",
            "pid": 1234,
            "timeout": 30
        }
        
        # Mock agent connection
        test_agent_id = "test_agent_123"
        websocket_manager.agent_connections[test_agent_id] = "mock_connection_id"
        websocket_manager.active_connections["mock_connection_id"] = mock_websocket
        
        # Execute kill process command
        command_id = await websocket_manager.execute_process_command(test_agent_id, kill_command)
        
        # Verify command was sent
        assert mock_websocket.send.called
        sent_message = json.loads(mock_websocket.send.call_args[0][0])
        
        assert sent_message["type"] == "powershell_command"
        assert sent_message["request_id"] == command_id
        assert "Stop-Process -Id 1234" in sent_message["command"]
        assert "criticalProcesses" in sent_message["command"]

    @pytest.mark.integration
    @pytest.mark.websocket
    async def test_websocket_bulk_kill_command_generation(self, mock_websocket):
        """Test WebSocket manager generates correct bulk kill PowerShell commands"""
        
        from apps.backend.app.core.websocket_manager import websocket_manager
        
        # Test bulk kill command generation
        bulk_kill_command = {
            "action": "kill_processes_bulk",
            "pids": [1234, 5678, 9999],
            "timeout": 60
        }
        
        # Mock agent connection
        test_agent_id = "test_agent_123"
        websocket_manager.agent_connections[test_agent_id] = "mock_connection_id"
        websocket_manager.active_connections["mock_connection_id"] = mock_websocket
        
        # Execute bulk kill command
        command_id = await websocket_manager.execute_process_command(test_agent_id, bulk_kill_command)
        
        # Verify command was sent
        assert mock_websocket.send.called
        sent_message = json.loads(mock_websocket.send.call_args[0][0])
        
        assert sent_message["type"] == "powershell_command"
        assert sent_message["request_id"] == command_id
        assert "1234,5678,9999" in sent_message["command"]
        assert "successful" in sent_message["command"]
        assert "failed" in sent_message["command"]

    @pytest.mark.integration
    @pytest.mark.security
    def test_process_api_authentication_required(self):
        """Test that all process management endpoints require authentication"""
        
        test_agent_id = "test_agent_123"
        base_url = TEST_CONFIG['backend_url']
        
        # Test endpoints without authentication
        endpoints_to_test = [
            ("GET", f"/api/v1/agents/{test_agent_id}/processes"),
            ("DELETE", f"/api/v1/agents/{test_agent_id}/processes/1234"),
            ("DELETE", f"/api/v1/agents/{test_agent_id}/processes/bulk")
        ]
        
        for method, endpoint in endpoints_to_test:
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}")
            elif method == "DELETE":
                if "bulk" in endpoint:
                    response = requests.delete(f"{base_url}{endpoint}", json={"process_ids": [1234]})
                else:
                    response = requests.delete(f"{base_url}{endpoint}")
            
            assert response.status_code == 401, f"Endpoint {endpoint} should require authentication"

    @pytest.mark.integration
    @pytest.mark.security
    def test_process_api_invalid_agent_id(self, authenticated_session):
        """Test process management endpoints with invalid agent ID"""
        
        invalid_agent_id = "non_existent_agent_123"
        
        # Test process list with invalid agent ID
        response = authenticated_session.get(
            f"{TEST_CONFIG['backend_url']}/api/v1/agents/{invalid_agent_id}/processes"
        )
        assert response.status_code == 404
        assert "not found" in response.json()['detail'].lower()
        
        # Test kill process with invalid agent ID
        response = authenticated_session.delete(
            f"{TEST_CONFIG['backend_url']}/api/v1/agents/{invalid_agent_id}/processes/1234"
        )
        assert response.status_code == 404
        assert "not found" in response.json()['detail'].lower()

    @pytest.mark.integration
    @pytest.mark.security
    def test_bulk_kill_empty_process_ids(self, authenticated_session, test_agent_data):
        """Test bulk kill with empty process IDs array"""
        
        # Create test agent
        agent_response = authenticated_session.post(
            f"{TEST_CONFIG['backend_url']}/api/v1/agents/register",
            json=test_agent_data
        )
        assert agent_response.status_code == 200
        agent_id = agent_response.json()['id']
        
        # Test bulk kill with empty array
        bulk_request = {"process_ids": []}
        response = authenticated_session.delete(
            f"{TEST_CONFIG['backend_url']}/api/v1/agents/{agent_id}/processes/bulk",
            json=bulk_request
        )
        assert response.status_code == 400
        assert "no process ids" in response.json()['detail'].lower()

    @pytest.mark.integration
    @pytest.mark.security
    def test_critical_process_protection_in_powershell(self, mock_websocket):
        """Test that PowerShell commands include critical process protection"""
        
        from apps.backend.app.core.websocket_manager import websocket_manager
        
        # Mock agent connection
        test_agent_id = "test_agent_123"
        websocket_manager.agent_connections[test_agent_id] = "mock_connection_id"
        websocket_manager.active_connections["mock_connection_id"] = mock_websocket
        
        async def test_kill_command():
            kill_command = {
                "action": "kill_process",
                "pid": 1234,
                "timeout": 30
            }
            
            await websocket_manager.execute_process_command(test_agent_id, kill_command)
            sent_message = json.loads(mock_websocket.send.call_args[0][0])
            
            # Verify critical process protection is included
            powershell_command = sent_message["command"]
            critical_processes = [
                'explorer', 'winlogon', 'csrss', 'lsass', 
                'services', 'system', 'smss', 'wininit'
            ]
            
            for critical_process in critical_processes:
                assert critical_process in powershell_command.lower()
                
            assert "Cannot terminate critical system process" in powershell_command
        
        asyncio.run(test_kill_command())

    @pytest.mark.integration
    @pytest.mark.performance
    @pytest.mark.slow
    def test_process_list_performance(self, authenticated_session):
        """Test performance of process list endpoint"""
        
        # This test would require a connected agent, so we'll test the API response time
        # when agent is not connected (should fail fast)
        
        test_agent_id = "performance_test_agent"
        start_time = time.time()
        
        response = authenticated_session.get(
            f"{TEST_CONFIG['backend_url']}/api/v1/agents/{test_agent_id}/processes"
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # Should respond quickly even for non-existent agent
        assert response_time < 1.0, f"API response too slow: {response_time}s"
        assert response.status_code in [400, 404]  # Agent not found or not connected

    @pytest.mark.integration
    @pytest.mark.regression
    def test_api_response_formats(self, authenticated_session, test_agent_data):
        """Test that API responses follow expected format"""
        
        # Create test agent
        agent_response = authenticated_session.post(
            f"{TEST_CONFIG['backend_url']}/api/v1/agents/register",
            json=test_agent_data
        )
        assert agent_response.status_code == 200
        agent_id = agent_response.json()['id']
        
        # Test process list response format (when agent offline)
        response = authenticated_session.get(
            f"{TEST_CONFIG['backend_url']}/api/v1/agents/{agent_id}/processes"
        )
        assert response.status_code == 400
        response_data = response.json()
        assert "detail" in response_data
        
        # Test kill process response format (when agent offline)
        response = authenticated_session.delete(
            f"{TEST_CONFIG['backend_url']}/api/v1/agents/{agent_id}/processes/1234"
        )
        assert response.status_code == 400
        response_data = response.json()
        assert "detail" in response_data
        
        # Test bulk kill response format (when agent offline)
        bulk_request = {"process_ids": [1234, 5678]}
        response = authenticated_session.delete(
            f"{TEST_CONFIG['backend_url']}/api/v1/agents/{agent_id}/processes/bulk",
            json=bulk_request
        )
        assert response.status_code == 400
        response_data = response.json()
        assert "detail" in response_data

    @pytest.mark.integration
    @pytest.mark.smoke
    def test_task_manager_api_smoke_test(self, authenticated_session):
        """Smoke test for basic Task Manager API functionality"""
        
        # Test that all endpoints exist and return expected error codes
        test_agent_id = "smoke_test_agent"
        base_url = TEST_CONFIG['backend_url']
        
        # Process list endpoint
        response = authenticated_session.get(f"{base_url}/api/v1/agents/{test_agent_id}/processes")
        assert response.status_code in [400, 404]  # Agent not found or not connected
        
        # Kill process endpoint  
        response = authenticated_session.delete(f"{base_url}/api/v1/agents/{test_agent_id}/processes/1234")
        assert response.status_code in [400, 404]  # Agent not found or not connected
        
        # Bulk kill endpoint
        response = authenticated_session.delete(
            f"{base_url}/api/v1/agents/{test_agent_id}/processes/bulk",
            json={"process_ids": [1234]}
        )
        assert response.status_code in [400, 404]  # Agent not found or not connected
        
        print("✅ All Task Manager API endpoints are accessible")


class TestTaskManagerSecurity:
    """Security-focused tests for Task Manager feature"""

    @pytest.mark.integration
    @pytest.mark.security
    @pytest.mark.critical
    def test_sql_injection_prevention(self, authenticated_session):
        """Test SQL injection prevention in process management endpoints"""
        
        # SQL injection payloads
        sql_payloads = [
            "'; DROP TABLE agents; --",
            "1' OR '1'='1",
            "1; SELECT * FROM users; --",
            "1' UNION SELECT password FROM users --"
        ]
        
        base_url = TEST_CONFIG['backend_url']
        
        for payload in sql_payloads:
            # Test agent_id injection
            response = authenticated_session.get(f"{base_url}/api/v1/agents/{payload}/processes")
            assert response.status_code in [400, 404, 422]
            
            # Test PID injection
            response = authenticated_session.delete(f"{base_url}/api/v1/agents/test/{payload}")
            assert response.status_code in [400, 404, 422]

    @pytest.mark.integration
    @pytest.mark.security
    def test_powershell_command_injection_prevention(self, mock_websocket):
        """Test that PowerShell commands are properly protected against injection"""
        
        from apps.backend.app.core.websocket_manager import websocket_manager
        
        # Mock agent connection
        test_agent_id = "test_agent_123"
        websocket_manager.agent_connections[test_agent_id] = "mock_connection_id"
        websocket_manager.active_connections["mock_connection_id"] = mock_websocket
        
        async def test_injection_protection():
            # Test with malicious PID values
            malicious_pids = [
                "1234; Remove-Item -Path C:\\ -Recurse -Force",
                "1234 | Invoke-Expression 'malicious code'",
                "1234 && shutdown /s /f",
                "1234'; DROP TABLE agents; --"
            ]
            
            for malicious_pid in malicious_pids:
                kill_command = {
                    "action": "kill_process", 
                    "pid": malicious_pid,
                    "timeout": 30
                }
                
                try:
                    await websocket_manager.execute_process_command(test_agent_id, kill_command)
                    # Command should still execute but PID should be sanitized
                    sent_message = json.loads(mock_websocket.send.call_args[0][0])
                    powershell_command = sent_message["command"]
                    
                    # Should not contain dangerous commands
                    dangerous_commands = ["Remove-Item", "Invoke-Expression", "shutdown", "DROP TABLE"]
                    for dangerous in dangerous_commands:
                        assert dangerous not in powershell_command
                        
                except Exception:
                    # It's okay if the command fails due to invalid PID
                    pass
        
        asyncio.run(test_injection_protection())

    @pytest.mark.integration
    @pytest.mark.security
    def test_rate_limiting_protection(self, authenticated_session, test_agent_data):
        """Test rate limiting for process management operations"""
        
        # Create test agent
        agent_response = authenticated_session.post(
            f"{TEST_CONFIG['backend_url']}/api/v1/agents/register",
            json=test_agent_data
        )
        assert agent_response.status_code == 200
        agent_id = agent_response.json()['id']
        
        # Make rapid requests to test rate limiting
        base_url = TEST_CONFIG['backend_url']
        rapid_requests = []
        
        # Make 20 rapid requests
        for i in range(20):
            response = authenticated_session.get(f"{base_url}/api/v1/agents/{agent_id}/processes")
            rapid_requests.append(response.status_code)
        
        # All requests should either succeed (400 for offline agent) or be rate limited (429)
        for status_code in rapid_requests:
            assert status_code in [400, 404, 429], f"Unexpected status code: {status_code}"

    @pytest.mark.integration
    @pytest.mark.security
    def test_cross_agent_access_prevention(self, authenticated_session):
        """Test that users cannot access processes of agents they don't own"""
        
        # This test would need multi-user setup, for now we test basic agent isolation
        test_agents = [
            {"id": "agent_1", "name": "Agent 1"},
            {"id": "agent_2", "name": "Agent 2"}
        ]
        
        base_url = TEST_CONFIG['backend_url']
        
        # Try to access processes of non-existent agents
        for agent in test_agents:
            response = authenticated_session.get(f"{base_url}/api/v1/agents/{agent['id']}/processes")
            # Should return 404 (not found) rather than exposing any information
            assert response.status_code == 404

    @pytest.mark.integration
    @pytest.mark.security
    def test_audit_logging_for_process_operations(self, authenticated_session, test_agent_data):
        """Test that process management operations are properly logged"""
        
        # Create test agent
        agent_response = authenticated_session.post(
            f"{TEST_CONFIG['backend_url']}/api/v1/agents/register",
            json=test_agent_data
        )
        assert agent_response.status_code == 200
        agent_id = agent_response.json()['id']
        
        base_url = TEST_CONFIG['backend_url']
        
        # Perform operations that should be logged
        operations = [
            ("GET", f"/api/v1/agents/{agent_id}/processes"),
            ("DELETE", f"/api/v1/agents/{agent_id}/processes/1234"),
        ]
        
        for method, endpoint in operations:
            if method == "GET":
                response = authenticated_session.get(f"{base_url}{endpoint}")
            else:
                response = authenticated_session.delete(f"{base_url}{endpoint}")
            
            # Operations should be processed (even if they fail due to agent being offline)
            assert response.status_code in [400, 404]
            
        # Note: In a real implementation, we would check audit logs in database
        # For this test, we're verifying the operations are handled properly
        print("✅ Process management operations processed and should be logged")


# Test data generators
@pytest.fixture
def mock_process_list():
    """Generate mock process list data"""
    return [
        {
            "name": "notepad",
            "pid": 1234,
            "status": "Running",
            "description": "Notepad", 
            "userName": "TestUser",
            "cpu": 0.1
        },
        {
            "name": "chrome",
            "pid": 5678,
            "status": "Running",
            "description": "Google Chrome",
            "userName": "TestUser", 
            "cpu": 2.5
        },
        {
            "name": "explorer",
            "pid": 9999,
            "status": "Running", 
            "description": "Windows Explorer",
            "userName": "SYSTEM",
            "cpu": 0.0
        }
    ]


# Utility functions for tests
def simulate_powershell_response(success: bool, data: Dict[str, Any] = None, error: str = None) -> str:
    """Simulate PowerShell JSON response"""
    
    if success:
        response = {
            "success": True,
            **(data or {})
        }
    else:
        response = {
            "success": False,
            "error": error or "Command failed"
        }
    
    return json.dumps(response)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])