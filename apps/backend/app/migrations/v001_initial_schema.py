"""
Initial database schema migration
"""

migration = {
    'version': 'v001',
    'description': 'Initial database schema',
    'up': '''
        -- Create agents table
        CREATE TABLE IF NOT EXISTS agents (
            id TEXT PRIMARY KEY,
            hostname TEXT NOT NULL,
            ip TEXT,
            os TEXT,
            version TEXT,
            status TEXT DEFAULT 'offline',
            last_seen TIMESTAMP,
            tags TEXT,
            system_info TEXT,
            connection_id TEXT,
            is_connected BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Create command_history table
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
        );
        
        -- Create users table
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            full_name TEXT,
            password_hash TEXT NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            is_admin BOOLEAN DEFAULT FALSE,
            last_login TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Create sessions table
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );
        
        -- Create agent_groups table
        CREATE TABLE IF NOT EXISTS agent_groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Create agent_group_members table
        CREATE TABLE IF NOT EXISTS agent_group_members (
            group_id INTEGER NOT NULL,
            agent_id TEXT NOT NULL,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (group_id, agent_id),
            FOREIGN KEY (group_id) REFERENCES agent_groups (id) ON DELETE CASCADE,
            FOREIGN KEY (agent_id) REFERENCES agents (id) ON DELETE CASCADE
        );
        
        -- Create scheduled_tasks table
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
        );
        
        -- Create audit_logs table
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            resource_type TEXT,
            resource_id TEXT,
            details TEXT,
            ip_address TEXT,
            user_agent TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
        );
        
        -- Create agent_metrics table
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
        );
        
        -- Create alerts table
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id TEXT,
            alert_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            message TEXT NOT NULL,
            details TEXT,
            is_resolved BOOLEAN DEFAULT FALSE,
            resolved_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (agent_id) REFERENCES agents (id) ON DELETE CASCADE
        );
    ''',
    'down': '''
        DROP TABLE IF EXISTS alerts;
        DROP TABLE IF EXISTS agent_metrics;
        DROP TABLE IF EXISTS audit_logs;
        DROP TABLE IF EXISTS scheduled_tasks;
        DROP TABLE IF EXISTS agent_group_members;
        DROP TABLE IF EXISTS agent_groups;
        DROP TABLE IF EXISTS sessions;
        DROP TABLE IF EXISTS users;
        DROP TABLE IF EXISTS command_history;
        DROP TABLE IF EXISTS agents;
    '''
}