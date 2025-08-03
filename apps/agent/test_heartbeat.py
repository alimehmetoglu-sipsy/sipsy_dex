#!/usr/bin/env python3
"""
Test script for DexAgents heartbeat functionality
"""

import requests
import time
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_heartbeat():
    """Test heartbeat functionality"""
    server_url = "http://localhost:8000"
    api_token = "your-secret-key-here"
    agent_id = "test-agent-001"
    
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    logger.info("Testing heartbeat functionality...")
    
    # Test 1: Register agent
    logger.info("Test 1: Registering agent...")
    agent_data = {
        "hostname": "test-host",
        "ip": "192.168.1.100",
        "os": "Windows 10",
        "version": "10.0.19045",
        "status": "online",
        "tags": ["test", "heartbeat"]
    }
    
    try:
        response = requests.post(
            f"{server_url}/api/v1/agents/register",
            headers=headers,
            json=agent_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Agent registered successfully: {result}")
        else:
            logger.error(f"Registration failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return False
    
    # Test 2: Send heartbeat
    logger.info("Test 2: Sending heartbeat...")
    try:
        response = requests.post(
            f"{server_url}/api/v1/agents/{agent_id}/heartbeat",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Heartbeat sent successfully: {result}")
        else:
            logger.error(f"Heartbeat failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"Heartbeat error: {str(e)}")
        return False
    
    # Test 3: Check agent status
    logger.info("Test 3: Checking agent status...")
    try:
        response = requests.get(
            f"{server_url}/api/v1/agents/status/{agent_id}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Agent status: {result}")
        else:
            logger.error(f"Status check failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        return False
    
    # Test 4: Get all agents
    logger.info("Test 4: Getting all agents...")
    try:
        response = requests.get(
            f"{server_url}/api/v1/agents/",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            agents = response.json()
            logger.info(f"Found {len(agents)} agents")
            for agent in agents:
                logger.info(f"Agent: {agent.get('id')} - Status: {agent.get('status')}")
        else:
            logger.error(f"Get agents failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"Get agents error: {str(e)}")
        return False
    
    logger.info("All tests completed successfully!")
    return True

def test_offline_agents():
    """Test offline agents functionality"""
    server_url = "http://localhost:8000"
    api_token = "your-secret-key-here"
    
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    logger.info("Testing offline agents functionality...")
    
    try:
        response = requests.get(
            f"{server_url}/api/v1/agents/offline",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            offline_agents = response.json()
            logger.info(f"Found {len(offline_agents)} offline agents")
            for agent in offline_agents:
                logger.info(f"Offline agent: {agent.get('id')} - Last seen: {agent.get('last_seen')}")
        else:
            logger.error(f"Get offline agents failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"Get offline agents error: {str(e)}")
        return False
    
    return True

def main():
    """Main test function"""
    logger.info("Starting DexAgents heartbeat tests...")
    
    # Test basic heartbeat functionality
    if test_heartbeat():
        logger.info("✅ Basic heartbeat tests passed")
    else:
        logger.error("❌ Basic heartbeat tests failed")
        return
    
    # Test offline agents functionality
    if test_offline_agents():
        logger.info("✅ Offline agents tests passed")
    else:
        logger.error("❌ Offline agents tests failed")
        return
    
    logger.info("🎉 All tests passed successfully!")

if __name__ == "__main__":
    main() 