import psycopg2
import psycopg2.extras
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from contextlib import contextmanager
import logging
from .config import settings

logger = logging.getLogger(__name__)

class PostgreSQLDatabaseManager:
    def __init__(self, database_url: str = None):
        self.database_url = database_url or settings.DATABASE_URL
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = psycopg2.connect(self.database_url)
        conn.autocommit = False
        try:
            yield conn
        finally:
            conn.close()
    
    def init_database(self):
        """Initialize database tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create agents table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agents (
                    id TEXT PRIMARY KEY,
                    hostname TEXT NOT NULL,
                    ip TEXT,
                    os TEXT,
                    version TEXT,
                    status TEXT DEFAULT 'offline',
                    last_seen TIMESTAMP,
                    tags JSONB DEFAULT '[]',
                    system_info JSONB DEFAULT '{}',
                    connection_id TEXT,
                    is_connected BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create command_history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS command_history (
                    id SERIAL PRIMARY KEY,
                    agent_id TEXT,
                    command TEXT NOT NULL,
                    success BOOLEAN,
                    output TEXT,
                    error TEXT,
                    execution_time REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (agent_id) REFERENCES agents (id) ON DELETE CASCADE
                )
            ''')
            
            # Create users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    full_name TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    is_admin BOOLEAN DEFAULT FALSE,
                    last_login TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    token TEXT UNIQUE NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            ''')
            
            # Create agent_groups table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agent_groups (
                    id SERIAL PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create agent_group_members table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agent_group_members (
                    group_id INTEGER NOT NULL,
                    agent_id TEXT NOT NULL,
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (group_id, agent_id),
                    FOREIGN KEY (group_id) REFERENCES agent_groups (id) ON DELETE CASCADE,
                    FOREIGN KEY (agent_id) REFERENCES agents (id) ON DELETE CASCADE
                )
            ''')
            
            # Create scheduled_tasks table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scheduled_tasks (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    command TEXT NOT NULL,
                    cron_expression TEXT,
                    agent_id TEXT,
                    group_id INTEGER,
                    is_active BOOLEAN DEFAULT TRUE,
                    last_run TIMESTAMP,
                    next_run TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (agent_id) REFERENCES agents (id) ON DELETE SET NULL,
                    FOREIGN KEY (group_id) REFERENCES agent_groups (id) ON DELETE SET NULL
                )
            ''')
            
            # Create audit_logs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER,
                    action TEXT NOT NULL,
                    resource_type TEXT,
                    resource_id TEXT,
                    details JSONB DEFAULT '{}',
                    ip_address TEXT,
                    user_agent TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
                )
            ''')
            
            # Create agent_metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agent_metrics (
                    id SERIAL PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    cpu_usage REAL,
                    memory_usage REAL,
                    disk_usage REAL,
                    network_in REAL,
                    network_out REAL,
                    process_count INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (agent_id) REFERENCES agents (id) ON DELETE CASCADE
                )
            ''')
            
            # Create alerts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id SERIAL PRIMARY KEY,
                    agent_id TEXT,
                    alert_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    details JSONB DEFAULT '{}',
                    is_resolved BOOLEAN DEFAULT FALSE,
                    resolved_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (agent_id) REFERENCES agents (id) ON DELETE CASCADE
                )
            ''')
            
            # Create powershell_commands table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS powershell_commands (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    category TEXT DEFAULT 'general',
                    command TEXT NOT NULL,
                    parameters JSONB DEFAULT '[]',
                    tags JSONB DEFAULT '[]',
                    version TEXT DEFAULT '1.0',
                    author TEXT DEFAULT 'Unknown',
                    is_system BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_agents_hostname ON agents(hostname)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_command_history_agent_id ON command_history(agent_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_command_history_timestamp ON command_history(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_agent_metrics_agent_id ON agent_metrics(agent_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_agent_metrics_timestamp ON agent_metrics(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_agent_id ON alerts(agent_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_is_resolved ON alerts(is_resolved)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp)')
            
            # JSONB indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_agents_tags ON agents USING GIN(tags)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_agents_system_info ON agents USING GIN(system_info)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_powershell_commands_tags ON powershell_commands USING GIN(tags)')
            
            conn.commit()
            logger.info("PostgreSQL database initialized successfully")
            
            # Ensure default user exists
            self.ensure_default_user()
    
    # Agent methods
    def add_agent(self, agent_data: Dict[str, Any]) -> str:
        """Add a new agent to the database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Generate ID if not provided
            if 'id' not in agent_data:
                import time
                agent_data['id'] = f"agent_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{int(time.time() * 1000) % 1000}"
            
            cursor.execute('''
                INSERT INTO agents 
                (id, hostname, ip, os, version, status, last_seen, tags, system_info, connection_id, is_connected, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    hostname = EXCLUDED.hostname,
                    ip = EXCLUDED.ip,
                    os = EXCLUDED.os,
                    version = EXCLUDED.version,
                    status = EXCLUDED.status,
                    last_seen = EXCLUDED.last_seen,
                    tags = EXCLUDED.tags,
                    system_info = EXCLUDED.system_info,
                    connection_id = EXCLUDED.connection_id,
                    is_connected = EXCLUDED.is_connected,
                    updated_at = EXCLUDED.updated_at
            ''', (
                agent_data['id'],
                agent_data['hostname'],
                agent_data.get('ip'),
                agent_data.get('os'),
                agent_data.get('version'),
                agent_data.get('status', 'offline'),
                agent_data.get('last_seen', datetime.now()),
                json.dumps(agent_data.get('tags', [])),
                json.dumps(agent_data.get('system_info', {})),
                agent_data.get('connection_id'),
                agent_data.get('is_connected', False),
                datetime.now()
            ))
            
            conn.commit()
            logger.info(f"Agent {agent_data['id']} added/updated successfully")
            return agent_data['id']
    
    def get_agents(self) -> List[Dict[str, Any]]:
        """Get all agents from database"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute('SELECT * FROM agents ORDER BY updated_at DESC')
            rows = cursor.fetchall()
            
            agents = []
            for row in rows:
                agent = dict(row)
                # Convert datetime to ISO string
                if agent.get('last_seen'):
                    agent['last_seen'] = agent['last_seen'].isoformat() if agent['last_seen'] else None
                if agent.get('created_at'):
                    agent['created_at'] = agent['created_at'].isoformat() if agent['created_at'] else None
                if agent.get('updated_at'):
                    agent['updated_at'] = agent['updated_at'].isoformat() if agent['updated_at'] else None
                agents.append(agent)
            
            return agents
    
    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific agent by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute('SELECT * FROM agents WHERE id = %s', (agent_id,))
            row = cursor.fetchone()
            
            if row:
                agent = dict(row)
                # Convert datetime to ISO string
                if agent.get('last_seen'):
                    agent['last_seen'] = agent['last_seen'].isoformat() if agent['last_seen'] else None
                if agent.get('created_at'):
                    agent['created_at'] = agent['created_at'].isoformat() if agent['created_at'] else None
                if agent.get('updated_at'):
                    agent['updated_at'] = agent['updated_at'].isoformat() if agent['updated_at'] else None
                return agent
            
            return None
    
    def update_agent(self, agent_id: str, update_data: Dict[str, Any]) -> bool:
        """Update an existing agent"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if agent exists
            cursor.execute('SELECT id FROM agents WHERE id = %s', (agent_id,))
            if not cursor.fetchone():
                return False
            
            # Build update query dynamically
            update_fields = []
            values = []
            
            for field, value in update_data.items():
                if field in ['hostname', 'ip', 'os', 'version', 'status', 'last_seen', 'connection_id', 'is_connected']:
                    update_fields.append(f"{field} = %s")
                    values.append(value)
                elif field == 'tags':
                    update_fields.append("tags = %s")
                    values.append(json.dumps(value))
                elif field == 'system_info':
                    update_fields.append("system_info = %s")
                    values.append(json.dumps(value))
            
            if update_fields:
                update_fields.append("updated_at = %s")
                values.append(datetime.now())
                values.append(agent_id)
                
                query = f"UPDATE agents SET {', '.join(update_fields)} WHERE id = %s"
                cursor.execute(query, values)
                conn.commit()
                
                logger.info(f"Agent {agent_id} updated successfully")
                return True
            
            return False
    
    def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent from database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM agents WHERE id = %s', (agent_id,))
            conn.commit()
            
            if cursor.rowcount > 0:
                logger.info(f"Agent {agent_id} deleted successfully")
                return True
            
            return False
    
    def update_agent_status(self, agent_id: str, status: str, system_info: Optional[Dict] = None) -> bool:
        """Update agent status and optionally system info"""
        update_data = {
            'status': status,
            'last_seen': datetime.now().isoformat()
        }
        
        if system_info:
            update_data['system_info'] = system_info
        
        return self.update_agent(agent_id, update_data)
    
    def update_agent_connection(self, agent_id: str, connection_id: Optional[str], is_connected: bool) -> bool:
        """Update agent connection status"""
        update_data = {
            'connection_id': connection_id,
            'is_connected': is_connected,
            'status': 'online' if is_connected else 'offline',
            'last_seen': datetime.now().isoformat()
        }
        
        return self.update_agent(agent_id, update_data)
    
    def get_agent_by_hostname(self, hostname: str) -> Optional[Dict[str, Any]]:
        """Get agent by hostname"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute('SELECT * FROM agents WHERE hostname = %s', (hostname,))
            row = cursor.fetchone()
            
            if row:
                agent = dict(row)
                # Convert datetime to ISO string
                if agent.get('last_seen'):
                    agent['last_seen'] = agent['last_seen'].isoformat() if agent['last_seen'] else None
                if agent.get('created_at'):
                    agent['created_at'] = agent['created_at'].isoformat() if agent['created_at'] else None
                if agent.get('updated_at'):
                    agent['updated_at'] = agent['updated_at'].isoformat() if agent['updated_at'] else None
                return agent
            
            return None
    
    def add_command_history(self, agent_id: str, command_data: Dict[str, Any]) -> int:
        """Add command execution history"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO command_history 
                (agent_id, command, success, output, error, execution_time, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            ''', (
                agent_id,
                command_data['command'],
                command_data['success'],
                command_data.get('output', ''),
                command_data.get('error', ''),
                command_data.get('execution_time', 0.0),
                datetime.now()
            ))
            
            command_id = cursor.fetchone()[0]
            conn.commit()
            logger.info(f"Command history added for agent {agent_id}")
            return command_id
    
    def get_command_history(self, agent_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get command history for an agent"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute('''
                SELECT * FROM command_history 
                WHERE agent_id = %s 
                ORDER BY timestamp DESC 
                LIMIT %s
            ''', (agent_id, limit))
            
            rows = cursor.fetchall()
            commands = []
            for row in rows:
                command = dict(row)
                # Convert datetime to ISO string
                if command.get('timestamp'):
                    command['timestamp'] = command['timestamp'].isoformat()
                commands.append(command)
            return commands
    
    def ensure_default_user(self):
        """Ensure default admin user exists"""
        from .jwt_utils import get_password_hash
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Check if admin user exists
            cursor.execute("SELECT id FROM users WHERE username = %s", ("admin",))
            admin_user = cursor.fetchone()
            
            if not admin_user:
                # Create default admin user
                password_hash = get_password_hash("admin123")
                cursor.execute('''
                    INSERT INTO users (username, email, password_hash, full_name, is_admin)
                    VALUES (%s, %s, %s, %s, %s)
                ''', ("admin", "admin@dexagents.local", password_hash, "System Administrator", True))
                
                conn.commit()
                logger.info("Default admin user created successfully")
    
    # User methods
    def create_user(self, username: str, email: str, password_hash: str, full_name: str = None, is_admin: bool = False) -> Optional[int]:
        """Create a new user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    INSERT INTO users (username, email, password_hash, full_name, is_admin)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                ''', (username, email, password_hash, full_name, is_admin))
                
                user_id = cursor.fetchone()[0]
                conn.commit()
                return user_id
            except Exception as e:
                logger.error(f"User with username '{username}' or email '{email}' already exists: {e}")
                conn.rollback()
                return None
    
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
            row = cursor.fetchone()
            
            if row:
                user = dict(row)
                # Convert datetime to ISO string
                if user.get('last_login'):
                    user['last_login'] = user['last_login'].isoformat() if user['last_login'] else None
                if user.get('created_at'):
                    user['created_at'] = user['created_at'].isoformat() if user['created_at'] else None
                if user.get('updated_at'):
                    user['updated_at'] = user['updated_at'].isoformat() if user['updated_at'] else None
                return user
            return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
            row = cursor.fetchone()
            
            if row:
                user = dict(row)
                # Convert datetime to ISO string
                if user.get('last_login'):
                    user['last_login'] = user['last_login'].isoformat() if user['last_login'] else None
                if user.get('created_at'):
                    user['created_at'] = user['created_at'].isoformat() if user['created_at'] else None
                if user.get('updated_at'):
                    user['updated_at'] = user['updated_at'].isoformat() if user['updated_at'] else None
                return user
            return None
    
    def update_user_last_login(self, user_id: int):
        """Update user's last login timestamp"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users 
                SET last_login = %s, updated_at = %s
                WHERE id = %s
            ''', (datetime.now(), datetime.now(), user_id))
            conn.commit()
    
    # Add other methods following similar pattern...
    # (For brevity, I'll add the essential ones. The rest follow the same pattern)
    
    def get_all_saved_commands(self) -> List[Dict[str, Any]]:
        """Get all saved PowerShell commands"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute('''
                SELECT * FROM powershell_commands 
                ORDER BY created_at DESC
            ''')
            
            rows = cursor.fetchall()
            commands = []
            for row in rows:
                command = dict(row)
                # Convert datetime to ISO string
                if command.get('created_at'):
                    command['created_at'] = command['created_at'].isoformat()
                if command.get('updated_at'):
                    command['updated_at'] = command['updated_at'].isoformat()
                commands.append(command)
            
            return commands
    
    def save_powershell_command(self, command_data: Dict[str, Any]) -> bool:
        """Save a PowerShell command"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    INSERT INTO powershell_commands 
                    (id, name, description, category, command, parameters, tags, version, author, is_system, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (
                    command_data['id'],
                    command_data['name'],
                    command_data.get('description'),
                    command_data.get('category', 'general'),
                    command_data['command'],
                    json.dumps(command_data.get('parameters', [])),
                    json.dumps(command_data.get('tags', [])),
                    command_data.get('version', '1.0'),
                    command_data.get('author', 'Unknown'),
                    command_data.get('is_system', False),
                    command_data.get('created_at'),
                    command_data.get('updated_at')
                ))
                
                conn.commit()
                return True
            except Exception as e:
                logger.error(f"Error saving PowerShell command: {str(e)}")
                conn.rollback()
                return False
    
    def get_saved_command(self, command_id: str) -> Optional[Dict[str, Any]]:
        """Get a saved PowerShell command by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute('SELECT * FROM powershell_commands WHERE id = %s', (command_id,))
            row = cursor.fetchone()
            
            if row:
                command = dict(row)
                # Convert datetime to ISO string
                if command.get('created_at'):
                    command['created_at'] = command['created_at'].isoformat()
                if command.get('updated_at'):
                    command['updated_at'] = command['updated_at'].isoformat()
                return command
            return None
    
    def update_saved_command(self, command_id: str, command_data: Dict[str, Any]) -> bool:
        """Update a saved PowerShell command"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    UPDATE powershell_commands 
                    SET name = %s, description = %s, category = %s, command = %s, 
                        parameters = %s, tags = %s, version = %s, author = %s, 
                        updated_at = %s
                    WHERE id = %s
                ''', (
                    command_data['name'],
                    command_data.get('description'),
                    command_data.get('category', 'general'),
                    command_data['command'],
                    json.dumps(command_data.get('parameters', [])),
                    json.dumps(command_data.get('tags', [])),
                    command_data.get('version', '1.0'),
                    command_data.get('author', 'Unknown'),
                    datetime.now().isoformat(),
                    command_id
                ))
                
                conn.commit()
                return cursor.rowcount > 0
            except Exception as e:
                logger.error(f"Error updating PowerShell command: {str(e)}")
                conn.rollback()
                return False
    
    def delete_saved_command(self, command_id: str) -> bool:
        """Delete a saved PowerShell command"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute('DELETE FROM powershell_commands WHERE id = %s', (command_id,))
                conn.commit()
                return cursor.rowcount > 0
            except Exception as e:
                logger.error(f"Error deleting PowerShell command: {str(e)}")
                conn.rollback()
                return False

    # Settings Management
    def get_setting(self, key: str) -> Optional[Dict[str, Any]]:
        """Get a setting by key"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute('SELECT * FROM settings WHERE key = %s', (key,))
            result = cursor.fetchone()
            if result:
                return dict(result)
            return None
    
    def get_all_settings(self) -> List[Dict[str, Any]]:
        """Get all settings"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute('SELECT * FROM settings ORDER BY key')
            return [dict(row) for row in cursor.fetchall()]
    
    def save_setting(self, key: str, value: str, description: str = None, is_encrypted: bool = False) -> bool:
        """Save or update a setting"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    INSERT INTO settings (key, value, description, is_encrypted)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (key) 
                    DO UPDATE SET 
                        value = EXCLUDED.value,
                        description = EXCLUDED.description,
                        is_encrypted = EXCLUDED.is_encrypted,
                        updated_at = CURRENT_TIMESTAMP
                ''', (key, value, description, is_encrypted))
                
                conn.commit()
                logger.info(f"Setting '{key}' saved successfully")
                return True
            except Exception as e:
                logger.error(f"Error saving setting '{key}': {str(e)}")
                conn.rollback()
                return False
    
    def delete_setting(self, key: str) -> bool:
        """Delete a setting"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute('DELETE FROM settings WHERE key = %s', (key,))
                conn.commit()
                return cursor.rowcount > 0
            except Exception as e:
                logger.error(f"Error deleting setting '{key}': {str(e)}")
                conn.rollback()
                return False