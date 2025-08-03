#!/usr/bin/env python3
"""
Pytest configuration and fixtures for integration tests
"""

import asyncio
import pytest
import psycopg2
import requests
import subprocess
import time
import os
from typing import Generator, Dict, Any

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

@pytest.fixture(scope='session')
def setup_test_environment():
    """Setup test environment before running tests"""
    
    # Check if services are running
    try:
        response = requests.get(f"{TEST_CONFIG['backend_url']}/api/v1/system/health", timeout=5)
        if response.status_code != 200:
            raise Exception("Backend not ready")
    except Exception:
        # Try to start services
        print("Starting test services...")
        subprocess.run(['docker-compose', 'up', '-d'], check=True)
        
        # Wait for services to be ready
        for i in range(30):  # 30 second timeout
            try:
                response = requests.get(f"{TEST_CONFIG['backend_url']}/api/v1/system/health", timeout=2)
                if response.status_code == 200:
                    break
            except:
                pass
            time.sleep(1)
        else:
            raise Exception("Services failed to start")
    
    yield
    
    # Cleanup after all tests
    cleanup_test_database()

@pytest.fixture(scope='session')
def test_database():
    """Setup test database"""
    
    # Create test database if it doesn't exist
    try:
        # Connect to default database to create test database
        conn = psycopg2.connect(
            host=TEST_CONFIG['database']['host'],
            port=TEST_CONFIG['database']['port'],
            database='postgres',
            user=TEST_CONFIG['database']['user'],
            password=TEST_CONFIG['database']['password']
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Create test database
        cursor.execute(f"DROP DATABASE IF EXISTS {TEST_CONFIG['database']['database']}")
        cursor.execute(f"CREATE DATABASE {TEST_CONFIG['database']['database']}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Database setup error: {e}")
    
    yield TEST_CONFIG['database']
    
    # Database cleanup handled in setup_test_environment

@pytest.fixture
def authenticated_session():
    """Create an authenticated HTTP session"""
    
    session = requests.Session()
    
    # Authenticate
    response = session.post(
        f"{TEST_CONFIG['backend_url']}/api/v1/auth/login",
        json=TEST_CONFIG['test_user']
    )
    
    if response.status_code == 200:
        data = response.json()
        session.headers.update({
            'Authorization': f'Bearer {data["access_token"]}'
        })
    
    yield session
    
    # Session cleanup is automatic

@pytest.fixture
def clean_database():
    """Clean database before and after each test"""
    
    cleanup_test_database()
    yield
    cleanup_test_database()

@pytest.fixture
def test_agent_data():
    """Provide test agent data"""
    
    import uuid
    
    return {
        'id': f'test_agent_{uuid.uuid4().hex[:8]}',
        'name': 'Test Integration Agent',
        'hostname': 'test-machine',
        'ip_address': '192.168.1.100',
        'os': 'Windows 10',
        'version': '1.0.0',
        'capabilities': ['powershell', 'cmd']
    }

@pytest.fixture
def test_command_data():
    """Provide test command data"""
    
    return {
        'name': 'Test_Integration_Command',
        'command': 'Get-Process | Select-Object -First 3 Name, Id',
        'description': 'Test command for integration testing',
        'category': 'system',
        'timeout': 30
    }

def cleanup_test_database():
    """Clean up test data from database"""
    
    try:
        conn = psycopg2.connect(**TEST_CONFIG['database'])
        cursor = conn.cursor()
        
        # Clean up in correct order due to foreign key constraints
        cleanup_queries = [
            "DELETE FROM command_executions WHERE agent_id LIKE 'test_%'",
            "DELETE FROM agent_metrics WHERE agent_id LIKE 'test_%'",
            "DELETE FROM agents WHERE id LIKE 'test_%'",
            "DELETE FROM saved_commands WHERE name LIKE 'Test_%'",
            "DELETE FROM audit_logs WHERE details LIKE '%test_%'",
        ]
        
        for query in cleanup_queries:
            try:
                cursor.execute(query)
            except Exception as e:
                print(f"Cleanup query failed: {query}, Error: {e}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Database cleanup error: {e}")

@pytest.fixture
def mock_websocket():
    """Mock WebSocket for testing"""
    
    from unittest.mock import Mock, AsyncMock
    
    mock_ws = Mock()
    mock_ws.send = AsyncMock()
    mock_ws.recv = AsyncMock()
    mock_ws.close = AsyncMock()
    
    return mock_ws

@pytest.fixture(scope='session')
def event_loop():
    """Create event loop for async tests"""
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()

# Pytest configuration
def pytest_configure(config):
    """Configure pytest"""
    
    # Add custom markers
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "websocket: mark test as WebSocket related"
    )

def pytest_collection_modifyitems(config, items):
    """Modify test collection"""
    
    # Mark all tests in this file as integration tests
    for item in items:
        if "integration" in item.fspath.basename:
            item.add_marker(pytest.mark.integration)
            
# Test helpers
class TestHelpers:
    """Helper functions for integration tests"""
    
    @staticmethod
    def wait_for_condition(condition_func, timeout=10, interval=0.5):
        """Wait for a condition to be true"""
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            if condition_func():
                return True
            time.sleep(interval)
        return False
    
    @staticmethod
    def create_test_agent(session, agent_data):
        """Helper to create test agent via API"""
        
        response = session.post(
            f"{TEST_CONFIG['backend_url']}/api/v1/agents",
            json=agent_data
        )
        return response
    
    @staticmethod
    def execute_command_on_agent(session, agent_id, command_data):
        """Helper to execute command on agent"""
        
        response = session.post(
            f"{TEST_CONFIG['backend_url']}/api/v1/commands/agent/{agent_id}/execute",
            json=command_data
        )
        return response
    
    @staticmethod
    async def simulate_websocket_message(websocket, message_type, payload):
        """Helper to simulate WebSocket message"""
        
        import json
        import uuid
        
        message = {
            'type': message_type,
            'id': str(uuid.uuid4()),
            'timestamp': time.time(),
            'payload': payload
        }
        
        await websocket.send(json.dumps(message))
        return message

# Export helpers for use in tests
helpers = TestHelpers()