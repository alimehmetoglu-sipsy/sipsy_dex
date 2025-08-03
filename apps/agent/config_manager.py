#!/usr/bin/env python3
"""
DexAgents Configuration Manager
Secure configuration handling with encryption and validation
"""

import json
import os
import platform
import socket
from datetime import datetime
from typing import Dict, Any, Optional
import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class ConfigManager:
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config_dir = os.path.dirname(os.path.abspath(config_file))
        self.backup_dir = os.path.join(self.config_dir, "config_backups")
        
        # Encryption settings
        self.use_encryption = True
        self.key_file = os.path.join(self.config_dir, ".config_key")
        self._encryption_key = None
        
        # Configuration schema for validation
        self.config_schema = {
            'server_url': {'type': str, 'required': True},
            'api_token': {'type': str, 'required': True, 'encrypted': True},
            'agent_name': {'type': str, 'required': True},
            'tags': {'type': list, 'required': False, 'default': []},
            'auto_start': {'type': bool, 'required': False, 'default': False},
            'minimize_to_tray': {'type': bool, 'required': False, 'default': True},
            'run_as_service': {'type': bool, 'required': False, 'default': False},
            'log_level': {'type': str, 'required': False, 'default': 'INFO'},
            'connection_timeout': {'type': int, 'required': False, 'default': 10},
            'reconnection_attempts': {'type': int, 'required': False, 'default': 10},
            'heartbeat_interval': {'type': int, 'required': False, 'default': 30},
            'command_timeout': {'type': int, 'required': False, 'default': 30},
            'max_log_size_mb': {'type': int, 'required': False, 'default': 10},
            'max_log_files': {'type': int, 'required': False, 'default': 5},
            'enable_system_monitoring': {'type': bool, 'required': False, 'default': True},
            'monitoring_interval': {'type': int, 'required': False, 'default': 5},
            'proxy_settings': {'type': dict, 'required': False, 'default': {}},
            'ssl_verify': {'type': bool, 'required': False, 'default': True},
            'custom_ca_bundle': {'type': str, 'required': False, 'default': ''},
            'debug_mode': {'type': bool, 'required': False, 'default': False}
        }
        
        # Import logger
        from logger import Logger
        self.logger = Logger()
        
        # Ensure directories exist
        os.makedirs(self.config_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
        
        self.logger.info(f"Configuration manager initialized: {self.config_file}")
    
    def _get_encryption_key(self) -> bytes:
        """Get or create encryption key"""
        if self._encryption_key:
            return self._encryption_key
        
        if os.path.exists(self.key_file):
            # Load existing key
            try:
                with open(self.key_file, 'rb') as f:
                    self._encryption_key = f.read()
                return self._encryption_key
            except Exception as e:
                self.logger.warning(f"Failed to load encryption key: {e}")
        
        # Generate new key
        try:
            # Use machine-specific data for key derivation
            machine_data = f"{platform.node()}-{platform.machine()}-{platform.processor()}".encode()
            
            # Add current user info if available
            try:
                import getpass
                machine_data += getpass.getuser().encode()
            except Exception:
                pass
            
            # Derive key from machine data
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'dexagents_salt_2024',  # Fixed salt for reproducibility
                iterations=100000,
            )
            
            key = base64.urlsafe_b64encode(kdf.derive(machine_data))
            
            # Save key to file with restricted permissions
            with open(self.key_file, 'wb') as f:
                f.write(key)
            
            # Set restrictive permissions (owner only)
            if os.name != 'nt':  # Unix-like systems
                os.chmod(self.key_file, 0o600)
            
            self._encryption_key = key
            self.logger.info("Generated new encryption key")
            
            return self._encryption_key
            
        except Exception as e:
            self.logger.error(f"Failed to generate encryption key: {e}")
            self.use_encryption = False
            return b''
    
    def _encrypt_value(self, value: str) -> str:
        """Encrypt a configuration value"""
        if not self.use_encryption or not value:
            return value
        
        try:
            key = self._get_encryption_key()
            if not key:
                return value
            
            f = Fernet(key)
            encrypted = f.encrypt(value.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
            
        except Exception as e:
            self.logger.error(f"Encryption failed: {e}")
            return value
    
    def _decrypt_value(self, encrypted_value: str) -> str:
        """Decrypt a configuration value"""
        if not self.use_encryption or not encrypted_value:
            return encrypted_value
        
        try:
            key = self._get_encryption_key()
            if not key:
                return encrypted_value
            
            f = Fernet(key)
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_value.encode())
            decrypted = f.decrypt(encrypted_bytes)
            return decrypted.decode()
            
        except Exception as e:
            self.logger.debug(f"Decryption failed, value may not be encrypted: {e}")
            return encrypted_value
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        hostname = socket.gethostname()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        default_config = {
            'server_url': 'ws://localhost:8080',
            'api_token': 'your-api-token-here',
            'agent_name': f'WindowsAgent_{hostname}_{timestamp}',
            'tags': ['windows', 'powershell', 'agent'],
            'auto_start': False,
            'minimize_to_tray': True,
            'run_as_service': False,
            'log_level': 'INFO',
            'connection_timeout': 10,
            'reconnection_attempts': 10,
            'heartbeat_interval': 30,
            'command_timeout': 30,
            'max_log_size_mb': 10,
            'max_log_files': 5,
            'enable_system_monitoring': True,
            'monitoring_interval': 5,
            'proxy_settings': {},
            'ssl_verify': True,
            'custom_ca_bundle': '',
            'debug_mode': False
        }
        
        return default_config
    
    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize configuration"""
        validated_config = {}
        errors = []
        
        for key, schema in self.config_schema.items():
            value = config.get(key)
            
            # Check required fields
            if schema.get('required', False) and value is None:
                if 'default' in schema:
                    value = schema['default']
                else:
                    errors.append(f"Required field '{key}' is missing")
                    continue
            
            # Use default if not provided
            if value is None and 'default' in schema:
                value = schema['default']
            
            # Type validation
            if value is not None:
                expected_type = schema['type']
                if not isinstance(value, expected_type):
                    try:
                        # Try to convert
                        if expected_type == bool and isinstance(value, str):
                            value = value.lower() in ('true', '1', 'yes', 'on')
                        elif expected_type == int and isinstance(value, str):
                            value = int(value)
                        elif expected_type == str and not isinstance(value, str):
                            value = str(value)
                        else:
                            raise ValueError(f"Cannot convert {type(value)} to {expected_type}")
                    except (ValueError, TypeError):
                        errors.append(f"Field '{key}' must be of type {expected_type.__name__}")
                        continue
            
            validated_config[key] = value
        
        # Additional validation
        self._validate_special_fields(validated_config, errors)
        
        if errors:
            raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
        
        return validated_config
    
    def _validate_special_fields(self, config: Dict[str, Any], errors: list):
        """Validate special configuration fields"""
        # Validate server URL
        server_url = config.get('server_url', '')
        if server_url and not (server_url.startswith('ws://') or server_url.startswith('wss://') or 
                              server_url.startswith('http://') or server_url.startswith('https://')):
            errors.append("server_url must start with ws://, wss://, http://, or https://")
        
        # Validate agent name
        agent_name = config.get('agent_name', '')
        if agent_name and (len(agent_name) < 3 or len(agent_name) > 64):
            errors.append("agent_name must be between 3 and 64 characters")
        
        # Validate timeouts
        for field in ['connection_timeout', 'command_timeout', 'heartbeat_interval']:
            value = config.get(field, 0)
            if value and (value < 1 or value > 3600):
                errors.append(f"{field} must be between 1 and 3600 seconds")
        
        # Validate log settings
        max_log_size = config.get('max_log_size_mb', 0)
        if max_log_size and (max_log_size < 1 or max_log_size > 100):
            errors.append("max_log_size_mb must be between 1 and 100")
        
        max_log_files = config.get('max_log_files', 0)
        if max_log_files and (max_log_files < 1 or max_log_files > 20):
            errors.append("max_log_files must be between 1 and 20")
        
        # Validate log level
        log_level = config.get('log_level', '')
        if log_level and log_level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            errors.append("log_level must be DEBUG, INFO, WARNING, ERROR, or CRITICAL")
    
    def load_config(self, config_file: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from file"""
        if config_file:
            config_path = config_file
        else:
            config_path = self.config_file
        
        # Start with default configuration
        config = self.get_default_config()
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                
                # Decrypt encrypted fields
                for key, value in loaded_config.items():
                    if (key in self.config_schema and 
                        self.config_schema[key].get('encrypted', False) and 
                        isinstance(value, str)):
                        loaded_config[key] = self._decrypt_value(value)
                
                # Merge with defaults
                config.update(loaded_config)
                
                self.logger.info(f"Configuration loaded from {config_path}")
                
            except json.JSONDecodeError as e:
                self.logger.error(f"Invalid JSON in config file: {e}")
                raise ValueError(f"Configuration file contains invalid JSON: {e}")
            except Exception as e:
                self.logger.error(f"Error loading config file: {e}")
                raise RuntimeError(f"Failed to load configuration: {e}")
        else:
            self.logger.info("No config file found, using defaults")
        
        # Validate configuration
        validated_config = self.validate_config(config)
        
        return validated_config
    
    def save_config(self, config: Dict[str, Any], config_file: Optional[str] = None) -> bool:
        """Save configuration to file"""
        if config_file:
            config_path = config_file
        else:
            config_path = self.config_file
        
        try:
            # Validate configuration before saving
            validated_config = self.validate_config(config)
            
            # Create backup if file exists
            if os.path.exists(config_path):
                self._create_backup(config_path)
            
            # Encrypt sensitive fields
            config_to_save = validated_config.copy()
            for key, value in config_to_save.items():
                if (key in self.config_schema and 
                    self.config_schema[key].get('encrypted', False) and 
                    isinstance(value, str)):
                    config_to_save[key] = self._encrypt_value(value)
            
            # Add metadata
            config_to_save['_metadata'] = {
                'created_at': datetime.now().isoformat(),
                'version': '2.0.0',
                'hostname': socket.gethostname(),
                'platform': platform.system()
            }
            
            # Write configuration
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_to_save, f, indent=2, ensure_ascii=False)
            
            # Set restrictive permissions
            if os.name != 'nt':  # Unix-like systems
                os.chmod(config_path, 0o600)
            
            self.logger.info(f"Configuration saved to {config_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")
            return False
    
    def _create_backup(self, config_path: str):
        """Create backup of existing configuration"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"config_backup_{timestamp}.json"
            backup_path = os.path.join(self.backup_dir, backup_name)
            
            # Copy current config to backup
            with open(config_path, 'r', encoding='utf-8') as src:
                config_data = src.read()
            
            with open(backup_path, 'w', encoding='utf-8') as dst:
                dst.write(config_data)
            
            self.logger.info(f"Configuration backup created: {backup_path}")
            
            # Clean old backups (keep only last 10)
            self._cleanup_old_backups()
            
        except Exception as e:
            self.logger.warning(f"Failed to create config backup: {e}")
    
    def _cleanup_old_backups(self):
        """Clean up old backup files"""
        try:
            backup_files = []
            for filename in os.listdir(self.backup_dir):
                if filename.startswith('config_backup_') and filename.endswith('.json'):
                    backup_path = os.path.join(self.backup_dir, filename)
                    backup_files.append((backup_path, os.path.getmtime(backup_path)))
            
            # Sort by modification time (newest first)
            backup_files.sort(key=lambda x: x[1], reverse=True)
            
            # Remove old backups (keep only 10 most recent)
            for backup_path, _ in backup_files[10:]:
                try:
                    os.remove(backup_path)
                    self.logger.debug(f"Removed old backup: {backup_path}")
                except Exception as e:
                    self.logger.warning(f"Failed to remove old backup {backup_path}: {e}")
                    
        except Exception as e:
            self.logger.warning(f"Failed to cleanup old backups: {e}")
    
    def get_config_info(self) -> Dict[str, Any]:
        """Get information about configuration"""
        info = {
            'config_file': self.config_file,
            'config_exists': os.path.exists(self.config_file),
            'backup_dir': self.backup_dir,
            'encryption_enabled': self.use_encryption,
            'key_file_exists': os.path.exists(self.key_file)
        }
        
        if info['config_exists']:
            try:
                stat = os.stat(self.config_file)
                info['file_size'] = stat.st_size
                info['modified_time'] = datetime.fromtimestamp(stat.st_mtime).isoformat()
            except Exception as e:
                info['stat_error'] = str(e)
        
        # Count backup files
        try:
            backup_files = [f for f in os.listdir(self.backup_dir) 
                          if f.startswith('config_backup_') and f.endswith('.json')]
            info['backup_count'] = len(backup_files)
        except Exception:
            info['backup_count'] = 0
        
        return info
    
    def restore_backup(self, backup_filename: str) -> bool:
        """Restore configuration from backup"""
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        if not os.path.exists(backup_path):
            self.logger.error(f"Backup file not found: {backup_path}")
            return False
        
        try:
            # Create backup of current config
            if os.path.exists(self.config_file):
                self._create_backup(self.config_file)
            
            # Copy backup to main config
            with open(backup_path, 'r', encoding='utf-8') as src:
                config_data = src.read()
            
            with open(self.config_file, 'w', encoding='utf-8') as dst:
                dst.write(config_data)
            
            self.logger.info(f"Configuration restored from {backup_filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to restore backup: {e}")
            return False
    
    def list_backups(self) -> list:
        """List available backup files"""
        backups = []
        
        try:
            for filename in os.listdir(self.backup_dir):
                if filename.startswith('config_backup_') and filename.endswith('.json'):
                    backup_path = os.path.join(self.backup_dir, filename)
                    stat = os.stat(backup_path)
                    
                    backups.append({
                        'filename': filename,
                        'size': stat.st_size,
                        'created': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        'path': backup_path
                    })
            
            # Sort by creation time (newest first)
            backups.sort(key=lambda x: x['created'], reverse=True)
            
        except Exception as e:
            self.logger.error(f"Failed to list backups: {e}")
        
        return backups

def main():
    """Test configuration manager"""
    config_manager = ConfigManager("test_config.json")
    
    print("=== Default Configuration ===")
    default_config = config_manager.get_default_config()
    print(json.dumps(default_config, indent=2))
    
    print("\n=== Saving Configuration ===")
    test_config = default_config.copy()
    test_config['server_url'] = 'ws://example.com:8080'
    test_config['api_token'] = 'secret-token-123'
    
    success = config_manager.save_config(test_config)
    print(f"Save successful: {success}")
    
    print("\n=== Loading Configuration ===")
    loaded_config = config_manager.load_config()
    print(f"API Token (decrypted): {loaded_config['api_token']}")
    
    print("\n=== Configuration Info ===")
    info = config_manager.get_config_info()
    print(json.dumps(info, indent=2))
    
    # Clean up test file
    try:
        os.remove("test_config.json")
    except Exception:
        pass

if __name__ == "__main__":
    main()