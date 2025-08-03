import openai
import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import base64
from cryptography.fernet import Fernet
import os

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.client = None
        self._cipher_suite = None
        self._init_encryption()
        self._load_api_key()
    
    def _init_encryption(self):
        """Initialize encryption for decrypting settings"""
        try:
            encryption_key = os.getenv("SETTINGS_ENCRYPTION_KEY", Fernet.generate_key())
            if isinstance(encryption_key, str):
                encryption_key = encryption_key.encode()
            self._cipher_suite = Fernet(encryption_key)
        except Exception as e:
            logger.error(f"Failed to initialize encryption: {str(e)}")
    
    def _decrypt_value(self, encrypted_value: str) -> str:
        """Decrypt a sensitive value"""
        if not self._cipher_suite:
            return encrypted_value
        try:
            encrypted_bytes = base64.b64decode(encrypted_value.encode())
            decrypted = self._cipher_suite.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Error decrypting value: {e}")
            return encrypted_value
    
    def _load_api_key(self):
        """Load OpenAI API key from database settings or fallback to file"""
        try:
            # First try to load from database settings
            from ..core.database import db_manager
            
            try:
                api_key_setting = db_manager.get_setting("chatgpt_api_key")
                if api_key_setting and api_key_setting.get('value'):
                    encrypted_api_key = api_key_setting['value']
                    # Decrypt if encrypted
                    if api_key_setting.get('is_encrypted'):
                        api_key = self._decrypt_value(encrypted_api_key)
                    else:
                        api_key = encrypted_api_key
                    
                    if api_key and api_key.strip():
                        self.client = openai.OpenAI(api_key=api_key.strip())
                        logger.info("OpenAI API client initialized successfully from database settings")
                        return
                        
            except Exception as db_error:
                logger.warning(f"Failed to load API key from database: {str(db_error)}")
            
            # Fallback to file-based loading (for backward compatibility)
            key_paths = [
                Path("/app/chatgpt.key"),  # Container path (for Docker)
                Path("/home/ali/chatgpt.key")  # Host path (for local development)
            ]
            
            for key_file in key_paths:
                if key_file.exists():
                    api_key = key_file.read_text().strip()
                    if api_key:
                        self.client = openai.OpenAI(api_key=api_key)
                        logger.info(f"OpenAI API client initialized successfully from {key_file} (fallback)")
                        return
                    else:
                        logger.warning(f"API key file {key_file} is empty")
            
            logger.error("ChatGPT API key not found in database settings or file")
        except Exception as e:
            logger.error(f"Failed to load ChatGPT API key: {str(e)}")
    
    def reload_api_key(self):
        """Reload API key from database (useful when settings are updated)"""
        self._load_api_key()
    
    def is_available(self) -> bool:
        """Check if AI service is available"""
        return self.client is not None
    
    async def generate_powershell_command(
        self, 
        user_request: str, 
        conversation_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Generate PowerShell command based on user request"""
        if not self.is_available():
            raise Exception("AI service not available - API key not configured")
        
        system_prompt = """You are a PowerShell command generation expert for a Windows endpoint management system.

Generate PowerShell commands that are:
1. Windows-compatible and safe for remote execution
2. Use proper PowerShell syntax and cmdlets
3. Include error handling where appropriate
4. Return structured output (preferably JSON) when possible
5. Are suitable for system administration and monitoring

IMPORTANT: Always return a valid JSON response in this exact format:
{
  "command": "Your-PowerShell-Command-Here",
  "name": "Short Descriptive Name",
  "description": "What the command does",
  "category": "system|network|disk|security|monitoring|general",
  "parameters": [],
  "tags": ["relevant", "tags"],
  "explanation": "Brief explanation of what the command does"
}

Example response:
{
  "command": "Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion, CsName, CsProcessors, CsTotalPhysicalMemory | ConvertTo-Json",
  "name": "Get System Information",
  "description": "Retrieves basic system information including OS version, computer name, and hardware details",
  "category": "system",
  "parameters": [],
  "tags": ["system", "information", "hardware"],
  "explanation": "This command gathers essential system information and formats it as JSON for easy processing"
}

Do NOT include markdown code blocks, explanatory text, or anything other than the JSON response.
Always prioritize safety and avoid commands that could harm the system.
"""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history if provided
        if conversation_history:
            for msg in conversation_history[-10:]:  # Keep last 10 messages for context
                messages.append(msg)
        
        # Add current user request
        messages.append({"role": "user", "content": user_request})
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.3,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content
            
            # Try to parse JSON response
            try:
                result = json.loads(content)
                # Validate that we have the required fields
                if isinstance(result, dict) and "command" in result:
                    return {
                        "success": True,
                        "command_data": result,
                        "raw_response": content
                    }
                else:
                    raise json.JSONDecodeError("Invalid JSON structure", content, 0)
                    
            except json.JSONDecodeError:
                # If not JSON, try to extract PowerShell command from the text
                import re
                
                # Look for PowerShell commands in code blocks
                powershell_patterns = [
                    r'```powershell\s*\n(.*?)\n```',
                    r'```\s*\n(.*?)\n```',
                    r'`([^`]+)`',
                ]
                
                extracted_command = None
                for pattern in powershell_patterns:
                    matches = re.findall(pattern, content, re.DOTALL)
                    if matches:
                        # Take the first match and clean it
                        extracted_command = matches[0].strip()
                        # Skip if it's JSON or contains JSON-like content
                        if not (extracted_command.startswith('{') or '"command":' in extracted_command):
                            break
                        extracted_command = None
                
                # If no command found in code blocks, look for common PowerShell cmdlets
                if not extracted_command:
                    cmdlet_pattern = r'(Get-\w+|Set-\w+|New-\w+|Remove-\w+|Start-\w+|Stop-\w+|Test-\w+|Invoke-\w+)[^"]*'
                    cmdlet_matches = re.findall(cmdlet_pattern, content)
                    if cmdlet_matches:
                        # Try to extract the full command line
                        for match in cmdlet_matches:
                            # Find the line containing this cmdlet
                            lines = content.split('\n')
                            for line in lines:
                                if match in line and not line.strip().startswith('"'):
                                    extracted_command = line.strip()
                                    break
                            if extracted_command:
                                break
                
                # Final fallback - use the content as is if it looks like a PowerShell command
                if not extracted_command:
                    # Check if content looks like a PowerShell command
                    if any(cmd in content for cmd in ['Get-', 'Set-', 'New-', 'Remove-', 'Start-', 'Stop-', 'Test-', 'Invoke-']):
                        extracted_command = content.strip()
                    else:
                        extracted_command = "Get-ComputerInfo"  # Safe fallback
                
                return {
                    "success": True,
                    "command_data": {
                        "command": extracted_command,
                        "name": "Generated Command",
                        "description": "AI-generated PowerShell command",
                        "category": "general",
                        "parameters": [],
                        "tags": ["ai-generated"],
                        "explanation": "Command extracted from AI response"
                    },
                    "raw_response": content,
                    "note": "Response was not in JSON format, extracted PowerShell command from text"
                }
                
        except Exception as e:
            logger.error(f"Error generating PowerShell command: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def test_command_on_agent(
        self,
        command: str,
        agent_id: str,
        websocket_manager,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """Test generated command on specified agent"""
        try:
            # Check if agent is connected
            if not websocket_manager.is_agent_connected(agent_id):
                return {
                    "success": False,
                    "error": "Agent not connected"
                }
            
            # Create PowerShell command message
            from uuid import uuid4
            from datetime import datetime
            
            request_id = f"ai_test_{datetime.now().timestamp()}_{uuid4().hex[:8]}"
            
            powershell_message = {
                "type": "powershell_command",
                "request_id": request_id,
                "command": command,
                "timeout": timeout,
                "timestamp": datetime.now().isoformat()
            }
            
            # Send command to agent
            success = await websocket_manager.send_to_agent(agent_id, powershell_message)
            if not success:
                return {
                    "success": False,
                    "error": "Failed to send command to agent"
                }
            
            # Wait for response with polling
            import asyncio
            max_attempts = timeout // 2  # Poll every 2 seconds
            
            for attempt in range(max_attempts):
                await asyncio.sleep(2)
                response = websocket_manager.get_command_response(request_id)
                
                if response is not None:
                    return {
                        "success": True,
                        "command_id": request_id,
                        "result": response
                    }
            
            # Timeout
            return {
                "success": False,
                "error": f"Command test timed out after {timeout} seconds"
            }
            
        except Exception as e:
            logger.error(f"Error testing command on agent: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

# Global AI service instance
ai_service = AIService()