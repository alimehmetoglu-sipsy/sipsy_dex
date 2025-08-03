from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from ...core.database import db_manager
from ...core.auth import verify_token
import logging
import json
import base64
from cryptography.fernet import Fernet
import os

logger = logging.getLogger(__name__)

router = APIRouter()

# Simple encryption for sensitive settings
ENCRYPTION_KEY = os.getenv("SETTINGS_ENCRYPTION_KEY")
if ENCRYPTION_KEY is None:
    ENCRYPTION_KEY = Fernet.generate_key()
elif isinstance(ENCRYPTION_KEY, str):
    ENCRYPTION_KEY = ENCRYPTION_KEY.encode()
cipher_suite = Fernet(ENCRYPTION_KEY)

class SettingRequest(BaseModel):
    key: str = Field(..., description="Setting key")
    value: str = Field(..., description="Setting value")
    description: Optional[str] = Field(None, description="Setting description")
    is_encrypted: bool = Field(False, description="Whether to encrypt the value")

class SettingResponse(BaseModel):
    key: str
    value: str
    description: Optional[str]
    is_encrypted: bool
    created_at: str
    updated_at: str

class ChatGPTConfig(BaseModel):
    api_key: str = Field(..., description="OpenAI API Key")
    model: str = Field("gpt-3.5-turbo", description="ChatGPT model")
    max_tokens: int = Field(1000, description="Maximum tokens per response")
    temperature: float = Field(0.7, description="Temperature for responses")
    system_prompt: Optional[str] = Field(None, description="System prompt for ChatGPT")

def encrypt_value(value: str) -> str:
    """Encrypt a sensitive value"""
    try:
        encrypted = cipher_suite.encrypt(value.encode())
        return base64.b64encode(encrypted).decode()
    except Exception as e:
        logger.error(f"Error encrypting value: {e}")
        return value

def decrypt_value(encrypted_value: str) -> str:
    """Decrypt a sensitive value"""
    try:
        encrypted_bytes = base64.b64decode(encrypted_value.encode())
        decrypted = cipher_suite.decrypt(encrypted_bytes)
        return decrypted.decode()
    except Exception as e:
        logger.error(f"Error decrypting value: {e}")
        return encrypted_value

@router.get("/", response_model=List[SettingResponse])
async def get_all_settings(token: str = Depends(verify_token)):
    """Get all settings"""
    try:
        settings = db_manager.get_all_settings()
        result = []
        for setting in settings:
            setting_dict = dict(setting)
            # Decrypt sensitive values for display (mask API keys)
            if setting_dict.get('is_encrypted') and setting_dict.get('key', '').endswith('_api_key'):
                # Mask API key for security
                setting_dict['value'] = '*' * 20
            elif setting_dict.get('is_encrypted'):
                # Decrypt other encrypted values
                setting_dict['value'] = decrypt_value(setting_dict['value'])
                
            # Convert datetime objects to strings
            for field in ['created_at', 'updated_at']:
                if setting_dict.get(field):
                    setting_dict[field] = str(setting_dict[field])
            
            result.append(SettingResponse(**setting_dict))
        return result
    except Exception as e:
        logger.error(f"Error getting settings: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get settings")

@router.get("/{key}", response_model=SettingResponse)
async def get_setting(key: str, token: str = Depends(verify_token)):
    """Get a specific setting"""
    try:
        setting = db_manager.get_setting(key)
        if not setting:
            raise HTTPException(status_code=404, detail="Setting not found")
        
        setting_dict = dict(setting)
        
        # Decrypt if encrypted and not an API key
        if setting_dict.get('is_encrypted'):
            if key.endswith('_api_key'):
                # Mask API key for security
                setting_dict['value'] = '*' * 20
            else:
                setting_dict['value'] = decrypt_value(setting_dict['value'])
        
        # Convert datetime objects to strings
        for field in ['created_at', 'updated_at']:
            if setting_dict.get(field):
                setting_dict[field] = str(setting_dict[field])
        
        return SettingResponse(**setting_dict)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting setting {key}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get setting")

@router.post("/", response_model=SettingResponse)
async def create_or_update_setting(setting: SettingRequest, token: str = Depends(verify_token)):
    """Create or update a setting"""
    try:
        value = setting.value
        
        # Encrypt sensitive values
        if setting.is_encrypted:
            value = encrypt_value(value)
        
        success = db_manager.save_setting(
            setting.key, 
            value, 
            setting.description, 
            setting.is_encrypted
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save setting")
        
        # Return the saved setting
        return await get_setting(setting.key, token)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving setting {setting.key}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to save setting")

@router.delete("/{key}")
async def delete_setting(key: str, token: str = Depends(verify_token)):
    """Delete a setting"""
    try:
        success = db_manager.delete_setting(key)
        if not success:
            raise HTTPException(status_code=404, detail="Setting not found")
        return {"message": "Setting deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting setting {key}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete setting")

@router.post("/chatgpt/config")
async def save_chatgpt_config(config: ChatGPTConfig, token: str = Depends(verify_token)):
    """Save ChatGPT configuration"""
    try:
        # Save each config value as a separate setting
        settings_to_save = [
            ("chatgpt_api_key", config.api_key, "OpenAI API Key for ChatGPT", True),
            ("chatgpt_model", config.model, "ChatGPT model to use", False),
            ("chatgpt_max_tokens", str(config.max_tokens), "Maximum tokens per response", False),
            ("chatgpt_temperature", str(config.temperature), "Temperature for responses", False),
        ]
        
        # Always save system_prompt, even if empty
        system_prompt_value = config.system_prompt or ""
        settings_to_save.append(("chatgpt_system_prompt", system_prompt_value, "System prompt for ChatGPT", False))
        
        for key, value, desc, encrypted in settings_to_save:
            encrypted_value = encrypt_value(value) if encrypted else value
            success = db_manager.save_setting(key, encrypted_value, desc, encrypted)
            if not success:
                raise HTTPException(status_code=500, detail=f"Failed to save {key}")
        
        # Reload AI service to use new API key
        try:
            from ...services.ai_service import ai_service
            ai_service.reload_api_key()
        except Exception as reload_error:
            logger.warning(f"Failed to reload AI service: {str(reload_error)}")
        
        return {"message": "ChatGPT configuration saved successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving ChatGPT config: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to save ChatGPT configuration")

@router.get("/chatgpt/config")
async def get_chatgpt_config(token: str = Depends(verify_token)):
    """Get ChatGPT configuration"""
    try:
        config = {}
        config_keys = {
            "chatgpt_api_key": "api_key",
            "chatgpt_model": "model", 
            "chatgpt_max_tokens": "max_tokens",
            "chatgpt_temperature": "temperature",
            "chatgpt_system_prompt": "system_prompt"
        }
        
        for db_key, config_key in config_keys.items():
            setting = db_manager.get_setting(db_key)
            if setting:
                value = setting['value']
                if setting.get('is_encrypted'):
                    if db_key == "chatgpt_api_key":
                        # Mask API key
                        value = '*' * 20 if value else ''
                    else:
                        value = decrypt_value(value)
                
                # Convert string values to appropriate types
                if config_key in ['max_tokens']:
                    try:
                        config[config_key] = int(value)
                    except (ValueError, TypeError):
                        config[config_key] = 1000  # default
                elif config_key in ['temperature']:
                    try:
                        config[config_key] = float(value)
                    except (ValueError, TypeError):
                        config[config_key] = 0.7  # default
                else:
                    config[config_key] = value
        
        # Set defaults if not found
        config.setdefault("model", "gpt-3.5-turbo")
        config.setdefault("max_tokens", 1000)
        config.setdefault("temperature", 0.7)
        config.setdefault("api_key", "")
        
        return config
    except Exception as e:
        logger.error(f"Error getting ChatGPT config: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get ChatGPT configuration")

@router.post("/chatgpt/test")
async def test_chatgpt_api(token: str = Depends(verify_token)):
    """Test ChatGPT API connection"""
    try:
        # Get API key
        api_key_setting = db_manager.get_setting("chatgpt_api_key")
        if not api_key_setting:
            raise HTTPException(status_code=400, detail="ChatGPT API key not configured")
        
        api_key = decrypt_value(api_key_setting['value'])
        
        # Simple test - just validate API key format
        if not api_key.startswith('sk-'):
            raise HTTPException(status_code=400, detail="Invalid API key format")
        
        # Get model setting
        model_setting = db_manager.get_setting("chatgpt_model")
        model = model_setting['value'] if model_setting else "gpt-3.5-turbo"
        
        # Make a real API test call to OpenAI using official client
        from openai import AsyncOpenAI
        
        client = AsyncOpenAI(api_key=api_key)
        
        try:
            # Test with a simple completion request
            response = await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=10
            )
            
            return {
                "success": True,
                "message": f"ChatGPT API connection successful! Model: {model}, Response: {response.choices[0].message.content.strip()}"
            }
            
        except Exception as openai_error:
            error_msg = str(openai_error)
            if "incorrect api key" in error_msg.lower() or "invalid api key" in error_msg.lower():
                raise HTTPException(status_code=400, detail="Invalid API key - authentication failed")
            elif "rate limit" in error_msg.lower():
                raise HTTPException(status_code=400, detail="API rate limit exceeded")
            elif "insufficient_quota" in error_msg.lower():
                raise HTTPException(status_code=400, detail="API quota exceeded - check your billing")
            elif "model" in error_msg.lower() and "does not exist" in error_msg.lower():
                raise HTTPException(status_code=400, detail=f"Model '{model}' is not available with your API key")
            else:
                raise HTTPException(status_code=400, detail=f"OpenAI API error: {error_msg}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing ChatGPT API: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to test ChatGPT API: {str(e)}")

@router.post("/reload-ai-service")
async def reload_ai_service(token: str = Depends(verify_token)):
    """Reload AI service configuration from database"""
    try:
        from ...services.ai_service import ai_service
        ai_service.reload_api_key()
        
        is_available = ai_service.is_available()
        return {
            "success": True,
            "available": is_available,
            "message": "AI service reloaded successfully" if is_available else "AI service reloaded but API key not configured"
        }
    except Exception as e:
        logger.error(f"Error reloading AI service: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to reload AI service: {str(e)}")