#!/usr/bin/env python3
"""
DexAgents WebSocket Client - Enhanced with auto-reconnection and reliability
"""

import asyncio
import websockets
import json
import logging
import platform
import socket
import time
from datetime import datetime
from typing import Dict, Any, Optional, Callable
import ssl
import certifi
from websockets.exceptions import ConnectionClosed, InvalidURI, InvalidHandshake

class WebSocketClient:
    def __init__(self, agent_id: str, server_url: str, api_token: str, gui_callback: Optional[Callable] = None):
        self.agent_id = agent_id
        self.server_url = server_url
        self.api_token = api_token
        self.gui_callback = gui_callback
        
        # Connection state
        self.websocket = None
        self.is_running = False
        self.is_connected = False
        self.reconnection_attempts = 0
        self.max_reconnection_attempts = 10
        self.reconnection_delay = 5  # seconds
        self.max_reconnection_delay = 300  # 5 minutes
        
        # Message queuing for offline mode
        self.message_queue = []
        self.max_queue_size = 1000
        
        # Heartbeat configuration
        self.heartbeat_interval = 30  # seconds
        self.heartbeat_timeout = 10   # seconds
        self.last_heartbeat = None
        self.heartbeat_task = None
        
        # Import components
        from system_monitor import SystemMonitor
        from powershell_executor import PowerShellExecutor
        from logger import Logger
        
        self.system_monitor = SystemMonitor()
        self.powershell_executor = PowerShellExecutor()
        self.logger = Logger()
        
        self.logger.info(f"WebSocket client initialized for agent: {agent_id}")
    
    def _notify_gui(self, event_type: str, data: Dict[str, Any] = None):
        """Notify GUI of events"""
        if self.gui_callback:
            try:
                self.gui_callback(event_type, data or {})
            except Exception as e:
                self.logger.error(f"Error notifying GUI: {e}")
    
    def _calculate_reconnection_delay(self) -> float:
        """Calculate exponential backoff delay"""
        if self.reconnection_attempts == 0:
            return self.reconnection_delay
        
        delay = min(
            self.reconnection_delay * (2 ** (self.reconnection_attempts - 1)),
            self.max_reconnection_delay
        )
        
        # Add jitter to prevent thundering herd
        import random
        jitter = random.uniform(0.1, 0.3) * delay
        return delay + jitter
    
    def _get_ws_url(self) -> str:
        """Get WebSocket URL with proper formatting"""
        base_url = self.server_url.rstrip('/')
        if not base_url.startswith(('ws://', 'wss://')):
            # Convert HTTP(S) to WebSocket URL
            if base_url.startswith('https://'):
                base_url = base_url.replace('https://', 'wss://', 1)
            elif base_url.startswith('http://'):
                base_url = base_url.replace('http://', 'ws://', 1)
            else:
                # Default to ws://
                base_url = f"ws://{base_url}"
        
        return f"{base_url}/api/v1/ws/{self.agent_id}"
    
    def _get_ssl_context(self) -> Optional[ssl.SSLContext]:
        """Create SSL context for secure connections"""
        if self.server_url.startswith('wss://'):
            try:
                ssl_context = ssl.create_default_context(cafile=certifi.where())
                ssl_context.check_hostname = True
                ssl_context.verify_mode = ssl.CERT_REQUIRED
                return ssl_context
            except Exception as e:
                self.logger.warning(f"Failed to create SSL context: {e}")
                return None
        return None
    
    async def _send_message(self, message_type: str, data: Dict[str, Any]):
        """Send message with queuing support"""
        message = {
            "type": message_type,
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "agent_id": self.agent_id
        }
        
        if self.websocket and self.is_connected:
            try:
                await self.websocket.send(json.dumps(message))
                self.logger.debug(f"Sent message: {message_type}")
                return True
            except Exception as e:
                self.logger.error(f"Error sending message: {e}")
                self._queue_message(message)
                return False
        else:
            # Queue message for later
            self._queue_message(message)
            return False
    
    def _queue_message(self, message: Dict[str, Any]):
        """Queue message for offline sending"""
        if len(self.message_queue) >= self.max_queue_size:
            # Remove oldest message
            self.message_queue.pop(0)
            self.logger.warning("Message queue full, dropped oldest message")
        
        self.message_queue.append(message)
        self.logger.debug(f"Queued message, queue size: {len(self.message_queue)}")
    
    async def _flush_message_queue(self):
        """Send queued messages"""
        if not self.message_queue or not (self.websocket and self.is_connected):
            return
        
        messages_to_send = self.message_queue.copy()
        self.message_queue.clear()
        
        self.logger.info(f"Flushing {len(messages_to_send)} queued messages")
        
        for message in messages_to_send:
            try:
                await self.websocket.send(json.dumps(message))
                await asyncio.sleep(0.1)  # Small delay to prevent flooding
            except Exception as e:
                self.logger.error(f"Error sending queued message: {e}")
                # Re-queue failed message
                self._queue_message(message)
                break  # Stop sending if connection fails
    
    async def _register_agent(self):
        """Register agent with server"""
        try:
            system_info = self.system_monitor.get_current_stats()
            
            registration_data = {
                "agent_id": self.agent_id,
                "hostname": system_info.get("hostname", socket.gethostname()),
                "ip": self._get_local_ip(),
                "os": platform.system(),
                "version": "2.0.0",
                "status": "online",
                "tags": ["windows", "powershell", "modern"],
                "system_info": system_info,
                "capabilities": [
                    "powershell_execution",
                    "system_monitoring",
                    "file_operations",
                    "process_management"
                ]
            }
            
            await self._send_message("register", registration_data)
            self.logger.info("Agent registration sent")
            
        except Exception as e:
            self.logger.error(f"Error registering agent: {e}")
    
    def _get_local_ip(self) -> str:
        """Get local IP address"""
        try:
            # Connect to a remote address to determine local IP
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.connect(("8.8.8.8", 80))
            local_ip = sock.getsockname()[0]
            sock.close()
            return local_ip
        except Exception:
            try:
                return socket.gethostbyname(socket.gethostname())
            except Exception:
                return "127.0.0.1"
    
    async def _handle_message(self, message: str):
        """Handle incoming WebSocket message"""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            message_data = data.get("data", {})
            
            self.logger.info(f"Received message: {message_type}")
            
            if message_type == "command":
                await self._handle_command(message_data)
            elif message_type == "ping":
                await self._handle_ping(message_data)
            elif message_type == "welcome":
                await self._handle_welcome(message_data)
            elif message_type == "system_info_request":
                await self._handle_system_info_request(message_data)
            else:
                self.logger.warning(f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON message: {e}")
        except Exception as e:
            self.logger.error(f"Error handling message: {e}")
    
    async def _handle_command(self, data: Dict[str, Any]):
        """Handle command execution request"""
        try:
            command = data.get("command")
            command_id = data.get("command_id")
            timeout = data.get("timeout", 30)
            working_directory = data.get("working_directory")
            
            if not command or not command_id:
                self.logger.error("Invalid command message format")
                return
            
            # Notify GUI
            self._notify_gui("command_received", {"command": command, "command_id": command_id})
            
            # Execute command
            self.logger.info(f"Executing command [{command_id}]: {command}")
            result = self.powershell_executor.execute_command(
                command, timeout=timeout, working_directory=working_directory
            )
            
            # Send result back
            await self._send_message("command_result", {
                "command_id": command_id,
                "result": result
            })
            
            # Notify GUI
            self._notify_gui("command_completed", {"command_id": command_id, "result": result})
            
            self.logger.info(f"Command [{command_id}] completed: success={result.get('success')}")
            
        except Exception as e:
            self.logger.error(f"Error handling command: {e}")
            # Send error result
            if 'command_id' in locals():
                await self._send_message("command_result", {
                    "command_id": command_id,
                    "result": {
                        "command": data.get("command", ""),
                        "success": False,
                        "output": "",
                        "error": str(e),
                        "exit_code": -1,
                        "execution_time": 0
                    }
                })
    
    async def _handle_ping(self, data: Dict[str, Any]):
        """Handle ping message"""
        await self._send_message("pong", {
            "timestamp": datetime.now().isoformat(),
            "agent_id": self.agent_id
        })
    
    async def _handle_welcome(self, data: Dict[str, Any]):
        """Handle welcome message from server"""
        self.logger.info("Received welcome message from server")
        server_info = data.get("server_info", {})
        self.logger.info(f"Connected to server: {server_info.get('name', 'Unknown')} v{server_info.get('version', 'Unknown')}")
    
    async def _handle_system_info_request(self, data: Dict[str, Any]):
        """Handle system information request"""
        try:
            request_id = data.get("request_id")
            detail_level = data.get("detail_level", "basic")
            
            if detail_level == "detailed":
                system_info = self.system_monitor.get_detailed_info()
            else:
                system_info = self.system_monitor.get_current_stats()
            
            await self._send_message("system_info_response", {
                "request_id": request_id,
                "system_info": system_info
            })
            
        except Exception as e:
            self.logger.error(f"Error handling system info request: {e}")
    
    async def _heartbeat_loop(self):
        """Periodic heartbeat loop"""
        while self.is_running and self.is_connected:
            try:
                # Send heartbeat with system info
                system_info = self.system_monitor.get_current_stats()
                await self._send_message("heartbeat", {
                    "agent_id": self.agent_id,
                    "system_info": system_info,
                    "status": "online",
                    "timestamp": datetime.now().isoformat()
                })
                
                self.last_heartbeat = time.time()
                await asyncio.sleep(self.heartbeat_interval)
                
            except Exception as e:
                self.logger.error(f"Error in heartbeat loop: {e}")
                break
    
    async def _connect_websocket(self):
        """Establish WebSocket connection"""
        ws_url = self._get_ws_url()
        ssl_context = self._get_ssl_context()
        
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "User-Agent": f"DexAgents-Windows-Agent/2.0.0 ({platform.system()} {platform.release()})"
        }
        
        self.logger.info(f"Connecting to WebSocket: {ws_url}")
        
        # Connection parameters
        connect_kwargs = {
            "additional_headers": headers,
            "ping_interval": 20,
            "ping_timeout": 10,
            "close_timeout": 10
        }
        
        if ssl_context:
            connect_kwargs["ssl"] = ssl_context
        
        try:
            self.websocket = await websockets.connect(ws_url, **connect_kwargs)
            self.is_connected = True
            self.reconnection_attempts = 0
            
            self.logger.info("WebSocket connected successfully")
            self._notify_gui("connected")
            
            return True
            
        except (ConnectionClosed, InvalidURI, InvalidHandshake, OSError) as e:
            self.logger.error(f"WebSocket connection failed: {e}")
            self.is_connected = False
            return False
        except Exception as e:
            self.logger.error(f"Unexpected connection error: {e}")
            self.is_connected = False
            return False
    
    async def _disconnect_websocket(self):
        """Disconnect WebSocket"""
        self.is_connected = False
        
        if self.websocket:
            try:
                await self.websocket.close()
            except Exception as e:
                self.logger.error(f"Error closing WebSocket: {e}")
            finally:
                self.websocket = None
        
        self._notify_gui("disconnected")
    
    async def _connection_loop(self):
        """Main connection loop with reconnection logic"""
        while self.is_running:
            try:
                # Attempt connection
                if await self._connect_websocket():
                    # Register agent
                    await self._register_agent()
                    
                    # Flush queued messages
                    await self._flush_message_queue()
                    
                    # Start heartbeat
                    self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
                    
                    try:
                        # Listen for messages
                        async for message in self.websocket:
                            if not self.is_running:
                                break
                            await self._handle_message(message)
                            
                    except ConnectionClosed as e:
                        self.logger.warning(f"WebSocket connection closed: {e}")
                    except Exception as e:
                        self.logger.error(f"Error in message loop: {e}")
                    
                    finally:
                        # Clean up
                        if self.heartbeat_task:
                            self.heartbeat_task.cancel()
                            try:
                                await self.heartbeat_task
                            except asyncio.CancelledError:
                                pass
                        
                        await self._disconnect_websocket()
                
                # Connection failed or closed
                if self.is_running:
                    self.reconnection_attempts += 1
                    
                    if self.reconnection_attempts <= self.max_reconnection_attempts:
                        delay = self._calculate_reconnection_delay()
                        self.logger.info(f"Reconnection attempt {self.reconnection_attempts}/{self.max_reconnection_attempts} in {delay:.1f} seconds")
                        await asyncio.sleep(delay)
                    else:
                        self.logger.error("Max reconnection attempts reached, stopping")
                        self.is_running = False
                        break
                        
            except Exception as e:
                self.logger.error(f"Unexpected error in connection loop: {e}")
                if self.is_running:
                    await asyncio.sleep(self.reconnection_delay)
    
    async def run(self):
        """Run the WebSocket client"""
        self.is_running = True
        self.reconnection_attempts = 0
        
        self.logger.info("Starting WebSocket client")
        
        try:
            await self._connection_loop()
        except Exception as e:
            self.logger.error(f"Fatal error in WebSocket client: {e}")
        finally:
            await self.stop()
    
    async def stop(self):
        """Stop the WebSocket client"""
        self.logger.info("Stopping WebSocket client")
        self.is_running = False
        
        # Cancel heartbeat task
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
            try:
                await self.heartbeat_task
            except asyncio.CancelledError:
                pass
        
        # Disconnect WebSocket
        await self._disconnect_websocket()
        
        self.logger.info("WebSocket client stopped")
    
    def stop_sync(self):
        """Synchronous stop method for use from GUI"""
        self.is_running = False

def main():
    """Test function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="DexAgents WebSocket Client")
    parser.add_argument("--agent-id", required=True, help="Agent ID")
    parser.add_argument("--server-url", default="ws://localhost:8080", help="WebSocket server URL")
    parser.add_argument("--api-token", default="test-token", help="API Token")
    
    args = parser.parse_args()
    
    client = WebSocketClient(
        agent_id=args.agent_id,
        server_url=args.server_url,
        api_token=args.api_token
    )
    
    try:
        asyncio.run(client.run())
    except KeyboardInterrupt:
        print("Client stopped by user")

if __name__ == "__main__":
    main()