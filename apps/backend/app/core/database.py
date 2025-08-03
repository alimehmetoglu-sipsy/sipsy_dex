import sqlite3
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from contextlib import contextmanager
import logging
from .config import settings

logger = logging.getLogger(__name__)

# Import PostgreSQL manager
try:
    from .database_postgresql import PostgreSQLDatabaseManager
    POSTGRESQL_AVAILABLE = True
except ImportError:
    POSTGRESQL_AVAILABLE = False
    logger.warning("PostgreSQL dependencies not available, using SQLite only")

class DatabaseManager:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or settings.DATABASE_URL
        # Ensure database directory exists
        import os
        db_dir = os.path.dirname(os.path.abspath(self.db_path))
        os.makedirs(db_dir, exist_ok=True)
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign keys
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
                    tags TEXT,  -- JSON array as string
                    system_info TEXT,  -- JSON object as string
                    connection_id TEXT,
                    is_connected BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create command_history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS command_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action TEXT NOT NULL,
                    resource_type TEXT,
                    resource_id TEXT,
                    details TEXT,  -- JSON object as string
                    ip_address TEXT,
                    user_agent TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
                )
            ''')
            
            # Create agent_metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agent_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT,
                    alert_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    details TEXT,  -- JSON object as string
                    is_resolved BOOLEAN DEFAULT FALSE,
                    resolved_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (agent_id) REFERENCES agents (id) ON DELETE CASCADE
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
            
            conn.commit()
            logger.info("Database initialized successfully")
            
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
            
            # Convert tags to JSON string
            tags_json = json.dumps(agent_data.get('tags', []))
            
            # Convert system_info to JSON string
            system_info_json = json.dumps(agent_data.get('system_info', {}))
            
            cursor.execute('''
                INSERT OR REPLACE INTO agents 
                (id, hostname, ip, os, version, status, last_seen, tags, system_info, connection_id, is_connected, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                agent_data['id'],
                agent_data['hostname'],
                agent_data.get('ip'),
                agent_data.get('os'),
                agent_data.get('version'),
                agent_data.get('status', 'offline'),
                agent_data.get('last_seen', datetime.now().isoformat()),
                tags_json,
                system_info_json,
                agent_data.get('connection_id'),
                agent_data.get('is_connected', False),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            logger.info(f"Agent {agent_data['id']} added/updated successfully")
            return agent_data['id']
    
    def get_agents(self) -> List[Dict[str, Any]]:
        """Get all agents from database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM agents ORDER BY updated_at DESC')
            rows = cursor.fetchall()
            
            agents = []
            for row in rows:
                agent = dict(row)
                # Parse JSON fields
                agent['tags'] = json.loads(agent['tags']) if agent['tags'] else []
                agent['system_info'] = json.loads(agent['system_info']) if agent['system_info'] else {}
                agents.append(agent)
            
            return agents
    
    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific agent by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM agents WHERE id = ?', (agent_id,))
            row = cursor.fetchone()
            
            if row:
                agent = dict(row)
                # Parse JSON fields
                agent['tags'] = json.loads(agent['tags']) if agent['tags'] else []
                agent['system_info'] = json.loads(agent['system_info']) if agent['system_info'] else {}
                return agent
            
            return None
    
    def get_agent_by_hostname(self, hostname: str) -> Optional[Dict[str, Any]]:
        """Get agent by hostname"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM agents WHERE hostname = ?', (hostname,))
            row = cursor.fetchone()
            
            if row:
                agent = dict(row)
                # Parse JSON fields
                agent['tags'] = json.loads(agent['tags']) if agent['tags'] else []
                agent['system_info'] = json.loads(agent['system_info']) if agent['system_info'] else {}
                return agent
            
            return None
    
    def update_agent(self, agent_id: str, update_data: Dict[str, Any]) -> bool:
        """Update an existing agent"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if agent exists
            cursor.execute('SELECT id FROM agents WHERE id = ?', (agent_id,))
            if not cursor.fetchone():
                return False
            
            # Build update query dynamically
            update_fields = []
            values = []
            
            for field, value in update_data.items():
                if field in ['hostname', 'ip', 'os', 'version', 'status', 'last_seen', 'connection_id', 'is_connected']:
                    update_fields.append(f"{field} = ?")
                    values.append(value)
                elif field == 'tags':
                    update_fields.append("tags = ?")
                    values.append(json.dumps(value))
                elif field == 'system_info':
                    update_fields.append("system_info = ?")
                    values.append(json.dumps(value))
            
            if update_fields:
                update_fields.append("updated_at = ?")
                values.append(datetime.now().isoformat())
                values.append(agent_id)
                
                query = f"UPDATE agents SET {', '.join(update_fields)} WHERE id = ?"
                cursor.execute(query, values)
                conn.commit()
                
                logger.info(f"Agent {agent_id} updated successfully")
                return True
            
            return False
    
    def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent from database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM agents WHERE id = ?', (agent_id,))
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
    
    # Command history methods
    def add_command_history(self, agent_id: str, command_data: Dict[str, Any]) -> int:
        """Add command execution history"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO command_history 
                (agent_id, command, success, output, error, execution_time, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                agent_id,
                command_data['command'],
                command_data['success'],
                command_data.get('output', ''),
                command_data.get('error', ''),
                command_data.get('execution_time', 0.0),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            command_id = cursor.lastrowid
            logger.info(f"Command history added for agent {agent_id}")
            return command_id
    
    def get_command_history(self, agent_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get command history for an agent"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM command_history 
                WHERE agent_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (agent_id, limit))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    # User methods
    def create_user(self, username: str, email: str, password_hash: str, full_name: str = None, is_admin: bool = False) -> Optional[int]:
        """Create a new user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    INSERT INTO users (username, email, password_hash, full_name, is_admin)
                    VALUES (?, ?, ?, ?, ?)
                ''', (username, email, password_hash, full_name, is_admin))
                
                conn.commit()
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                logger.error(f"User with username '{username}' or email '{email}' already exists")
                return None
    
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
    
    def update_user_last_login(self, user_id: int):
        """Update user's last login timestamp"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users 
                SET last_login = ?, updated_at = ?
                WHERE id = ?
            ''', (datetime.now().isoformat(), datetime.now().isoformat(), user_id))
            conn.commit()
    
    def ensure_default_user(self):
        """Ensure default admin user exists"""
        from .jwt_utils import get_password_hash
        
        # Check if admin user exists
        admin_user = self.get_user_by_username("admin")
        if not admin_user:
            # Create default admin user
            password_hash = get_password_hash("admin123")
            user_id = self.create_user(
                username="admin",
                email="admin@dexagents.local",
                password_hash=password_hash,
                full_name="System Administrator",
                is_admin=True
            )
            if user_id:
                logger.info("Default admin user created successfully")
            else:
                logger.error("Failed to create default admin user")
    
    # Group methods
    def create_agent_group(self, name: str, description: str = None) -> Optional[int]:
        """Create a new agent group"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    INSERT INTO agent_groups (name, description)
                    VALUES (?, ?)
                ''', (name, description))
                
                conn.commit()
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                logger.error(f"Group with name '{name}' already exists")
                return None
    
    def add_agent_to_group(self, group_id: int, agent_id: str) -> bool:
        """Add an agent to a group"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    INSERT INTO agent_group_members (group_id, agent_id)
                    VALUES (?, ?)
                ''', (group_id, agent_id))
                
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                logger.error(f"Agent {agent_id} is already in group {group_id}")
                return False
    
    def get_group_agents(self, group_id: int) -> List[Dict[str, Any]]:
        """Get all agents in a group"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT a.* FROM agents a
                JOIN agent_group_members agm ON a.id = agm.agent_id
                WHERE agm.group_id = ?
                ORDER BY a.hostname
            ''', (group_id,))
            
            rows = cursor.fetchall()
            agents = []
            for row in rows:
                agent = dict(row)
                agent['tags'] = json.loads(agent['tags']) if agent['tags'] else []
                agent['system_info'] = json.loads(agent['system_info']) if agent['system_info'] else {}
                agents.append(agent)
            
            return agents
    
    # Metrics methods
    def add_agent_metrics(self, agent_id: str, metrics: Dict[str, Any]) -> int:
        """Add agent performance metrics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO agent_metrics 
                (agent_id, cpu_usage, memory_usage, disk_usage, network_in, network_out, process_count)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                agent_id,
                metrics.get('cpu_usage'),
                metrics.get('memory_usage'),
                metrics.get('disk_usage'),
                metrics.get('network_in'),
                metrics.get('network_out'),
                metrics.get('process_count')
            ))
            
            conn.commit()
            return cursor.lastrowid
    
    def get_agent_metrics(self, agent_id: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get agent metrics for the last N hours"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM agent_metrics 
                WHERE agent_id = ? 
                AND timestamp > datetime('now', '-{} hours')
                ORDER BY timestamp DESC
            '''.format(hours), (agent_id,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    # Alert methods
    def create_alert(self, agent_id: str, alert_type: str, severity: str, message: str, details: Dict = None) -> int:
        """Create a new alert"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            details_json = json.dumps(details) if details else None
            
            cursor.execute('''
                INSERT INTO alerts (agent_id, alert_type, severity, message, details)
                VALUES (?, ?, ?, ?, ?)
            ''', (agent_id, alert_type, severity, message, details_json))
            
            conn.commit()
            return cursor.lastrowid
    
    def get_active_alerts(self, agent_id: str = None) -> List[Dict[str, Any]]:
        """Get active alerts, optionally filtered by agent"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if agent_id:
                cursor.execute('''
                    SELECT * FROM alerts 
                    WHERE agent_id = ? AND is_resolved = FALSE
                    ORDER BY created_at DESC
                ''', (agent_id,))
            else:
                cursor.execute('''
                    SELECT * FROM alerts 
                    WHERE is_resolved = FALSE
                    ORDER BY created_at DESC
                ''')
            
            rows = cursor.fetchall()
            alerts = []
            for row in rows:
                alert = dict(row)
                alert['details'] = json.loads(alert['details']) if alert['details'] else {}
                alerts.append(alert)
            
            return alerts
    
    def resolve_alert(self, alert_id: int) -> bool:
        """Mark an alert as resolved"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE alerts 
                SET is_resolved = TRUE, resolved_at = ?
                WHERE id = ?
            ''', (datetime.now().isoformat(), alert_id))
            
            conn.commit()
            return cursor.rowcount > 0
    
    # Audit log methods
    def add_audit_log(self, user_id: int, action: str, resource_type: str = None, 
                      resource_id: str = None, details: Dict = None, ip_address: str = None, 
                      user_agent: str = None) -> int:
        """Add an audit log entry"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            details_json = json.dumps(details) if details else None
            
            cursor.execute('''
                INSERT INTO audit_logs 
                (user_id, action, resource_type, resource_id, details, ip_address, user_agent)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, action, resource_type, resource_id, details_json, ip_address, user_agent))
            
            conn.commit()
            return cursor.lastrowid
    
    def get_audit_logs(self, user_id: int = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit logs, optionally filtered by user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if user_id:
                cursor.execute('''
                    SELECT * FROM audit_logs 
                    WHERE user_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (user_id, limit))
            else:
                cursor.execute('''
                    SELECT * FROM audit_logs 
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (limit,))
            
            rows = cursor.fetchall()
            logs = []
            for row in rows:
                log = dict(row)
                log['details'] = json.loads(log['details']) if log['details'] else {}
                logs.append(log)
            
            return logs
    
    # PowerShell Command methods  
    def save_powershell_command(self, command_data: Dict[str, Any]) -> bool:
        """Save a PowerShell command"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    INSERT INTO powershell_commands 
                    (id, name, description, category, command, parameters, tags, version, author, is_system, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            except sqlite3.Error as e:
                logger.error(f"Error saving PowerShell command: {str(e)}")
                return False
    
    def get_all_saved_commands(self) -> List[Dict[str, Any]]:
        """Get all saved PowerShell commands"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM powershell_commands 
                ORDER BY created_at DESC
            ''')
            
            rows = cursor.fetchall()
            commands = []
            for row in rows:
                command = dict(row)
                command['parameters'] = json.loads(command['parameters']) if command['parameters'] else []
                command['tags'] = json.loads(command['tags']) if command['tags'] else []
                commands.append(command)
            
            return commands
    
    def get_saved_command(self, command_id: str) -> Optional[Dict[str, Any]]:
        """Get a saved PowerShell command by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM powershell_commands WHERE id = ?', (command_id,))
            row = cursor.fetchone()
            
            if row:
                command = dict(row)
                command['parameters'] = json.loads(command['parameters']) if command['parameters'] else []
                command['tags'] = json.loads(command['tags']) if command['tags'] else []
                return command
            return None
    
    def update_saved_command(self, command_id: str, command_data: Dict[str, Any]) -> bool:
        """Update a saved PowerShell command"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    UPDATE powershell_commands 
                    SET name = ?, description = ?, category = ?, command = ?, 
                        parameters = ?, tags = ?, version = ?, author = ?, 
                        updated_at = ?
                    WHERE id = ?
                ''', (
                    command_data['name'],
                    command_data.get('description'),
                    command_data.get('category', 'general'),
                    command_data['command'],
                    json.dumps(command_data.get('parameters', [])),
                    json.dumps(command_data.get('tags', [])),
                    command_data.get('version', '1.0'),
                    command_data.get('author', 'Unknown'),
                    command_data.get('updated_at'),
                    command_id
                ))
                
                conn.commit()
                return cursor.rowcount > 0
            except sqlite3.Error as e:
                logger.error(f"Error updating PowerShell command: {str(e)}")
                return False
    
    def delete_saved_command(self, command_id: str) -> bool:
        """Delete a saved PowerShell command"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute('DELETE FROM powershell_commands WHERE id = ?', (command_id,))
                conn.commit()
                return cursor.rowcount > 0
            except sqlite3.Error as e:
                logger.error(f"Error deleting PowerShell command: {str(e)}")
                return False

# Lazy loading wrapper for database manager
class LazyDatabaseManager:
    def __init__(self):
        self._instance = None
    
    def __getattr__(self, name):
        if self._instance is None:
            # Choose database manager based on configuration
            if settings.is_postgresql and POSTGRESQL_AVAILABLE:
                logger.info("Using PostgreSQL database manager")
                self._instance = PostgreSQLDatabaseManager()
            else:
                if settings.is_postgresql and not POSTGRESQL_AVAILABLE:
                    logger.warning("PostgreSQL requested but dependencies not available, falling back to SQLite")
                logger.info("Using SQLite database manager")
                self._instance = DatabaseManager()
        return getattr(self._instance, name)

# Global database manager instance
db_manager = LazyDatabaseManager()