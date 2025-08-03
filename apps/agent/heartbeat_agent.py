#!/usr/bin/env python3
"""
Simple standalone heartbeat agent for DexAgents
This script sends heartbeat signals to the backend every 30 seconds
"""

import requests
import time
import json
import socket
import platform
import psutil
import logging
import os
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/heartbeat.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class HeartbeatAgent:
    def __init__(self, agent_id, server_url="http://localhost:8000", api_token="your-secret-key-here"):
        self.agent_id = agent_id
        self.server_url = server_url
        self.api_token = api_token
        self.running = False
        
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
    def get_system_info(self):
        """Get current system information"""
        try:
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk_usage = {}
            
            # Get disk usage for all mounted drives
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_usage[partition.mountpoint] = round((usage.used / usage.total) * 100, 1)
                except PermissionError:
                    continue
            
            return {
                "hostname": platform.node(),
                "os_version": platform.platform(),
                "cpu_usage": cpu_usage,
                "memory_usage": memory.percent,
                "disk_usage": disk_usage
            }
        except Exception as e:
            logger.error(f"Error getting system info: {str(e)}")
            return {}
    
    def send_heartbeat(self):
        """Send heartbeat to server"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{self.server_url}/api/v1/agents/{self.agent_id}/heartbeat",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("Heartbeat sent successfully")
                return True
            else:
                logger.error(f"Heartbeat failed: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error sending heartbeat: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error sending heartbeat: {str(e)}")
            return False
    
    def register_agent(self):
        """Register agent with server"""
        try:
            system_info = self.get_system_info()
            
            agent_data = {
                "hostname": system_info.get("hostname", socket.gethostname()),
                "ip": socket.gethostbyname(socket.gethostname()),
                "os": platform.system(),
                "version": platform.version(),
                "status": "online",
                "tags": ["heartbeat-agent", "standalone"],
                "system_info": system_info
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{self.server_url}/api/v1/agents/register",
                headers=headers,
                json=agent_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Agent registered successfully: {result.get('id', 'unknown')}")
                return result.get('id')
            else:
                logger.error(f"Registration failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error registering agent: {str(e)}")
            return None
    
    def run(self):
        """Main heartbeat loop"""
        logger.info(f"Starting heartbeat agent for ID: {self.agent_id}")
        logger.info(f"Server URL: {self.server_url}")
        
        self.running = True
        heartbeat_count = 0
        
        while self.running:
            try:
                # Send heartbeat
                success = self.send_heartbeat()
                heartbeat_count += 1
                
                if success:
                    logger.info(f"Heartbeat #{heartbeat_count} sent successfully")
                else:
                    logger.warning(f"Heartbeat #{heartbeat_count} failed")
                
                # Wait 30 seconds before next heartbeat
                time.sleep(30)
                
            except KeyboardInterrupt:
                logger.info("Heartbeat agent stopped by user")
                self.running = False
                break
            except Exception as e:
                logger.error(f"Unexpected error in heartbeat loop: {str(e)}")
                time.sleep(30)
    
    def stop(self):
        """Stop the heartbeat agent"""
        self.running = False
        logger.info("Heartbeat agent stopped")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="DexAgents Heartbeat Agent")
    parser.add_argument("--agent-id", required=True, help="Agent ID")
    parser.add_argument("--server-url", default="http://localhost:8000", help="Server URL")
    parser.add_argument("--api-token", default="your-secret-key-here", help="API Token")
    parser.add_argument("--register", action="store_true", help="Register agent first")
    
    args = parser.parse_args()
    
    # Create heartbeat agent
    agent = HeartbeatAgent(
        agent_id=args.agent_id,
        server_url=args.server_url,
        api_token=args.api_token
    )
    
    # Register agent if requested
    if args.register:
        logger.info("Registering agent...")
        registered_id = agent.register_agent()
        if registered_id:
            logger.info(f"Agent registered with ID: {registered_id}")
        else:
            logger.error("Failed to register agent")
            sys.exit(1)
    
    try:
        # Start heartbeat loop
        agent.run()
    except KeyboardInterrupt:
        logger.info("Shutting down heartbeat agent...")
        agent.stop()

if __name__ == "__main__":
    main() 