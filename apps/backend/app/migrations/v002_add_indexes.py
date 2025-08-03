"""
Add performance indexes to database tables
"""

migration = {
    'version': 'v002',
    'description': 'Add performance indexes',
    'up': '''
        -- Indexes for agents table
        CREATE INDEX IF NOT EXISTS idx_agents_hostname ON agents(hostname);
        CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status);
        CREATE INDEX IF NOT EXISTS idx_agents_last_seen ON agents(last_seen);
        
        -- Indexes for command_history table
        CREATE INDEX IF NOT EXISTS idx_command_history_agent_id ON command_history(agent_id);
        CREATE INDEX IF NOT EXISTS idx_command_history_timestamp ON command_history(timestamp);
        
        -- Indexes for sessions table
        CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(token);
        CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
        CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at);
        
        -- Indexes for agent_metrics table
        CREATE INDEX IF NOT EXISTS idx_agent_metrics_agent_id ON agent_metrics(agent_id);
        CREATE INDEX IF NOT EXISTS idx_agent_metrics_timestamp ON agent_metrics(timestamp);
        
        -- Indexes for alerts table
        CREATE INDEX IF NOT EXISTS idx_alerts_agent_id ON alerts(agent_id);
        CREATE INDEX IF NOT EXISTS idx_alerts_is_resolved ON alerts(is_resolved);
        CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity);
        CREATE INDEX IF NOT EXISTS idx_alerts_created_at ON alerts(created_at);
        
        -- Indexes for audit_logs table
        CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
        CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp);
        CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);
        CREATE INDEX IF NOT EXISTS idx_audit_logs_resource_type ON audit_logs(resource_type);
        
        -- Indexes for scheduled_tasks table
        CREATE INDEX IF NOT EXISTS idx_scheduled_tasks_agent_id ON scheduled_tasks(agent_id);
        CREATE INDEX IF NOT EXISTS idx_scheduled_tasks_group_id ON scheduled_tasks(group_id);
        CREATE INDEX IF NOT EXISTS idx_scheduled_tasks_is_active ON scheduled_tasks(is_active);
        CREATE INDEX IF NOT EXISTS idx_scheduled_tasks_next_run ON scheduled_tasks(next_run);
    ''',
    'down': '''
        -- Drop all indexes
        DROP INDEX IF EXISTS idx_agents_hostname;
        DROP INDEX IF EXISTS idx_agents_status;
        DROP INDEX IF EXISTS idx_agents_last_seen;
        DROP INDEX IF EXISTS idx_command_history_agent_id;
        DROP INDEX IF EXISTS idx_command_history_timestamp;
        DROP INDEX IF EXISTS idx_sessions_token;
        DROP INDEX IF EXISTS idx_sessions_user_id;
        DROP INDEX IF EXISTS idx_sessions_expires_at;
        DROP INDEX IF EXISTS idx_agent_metrics_agent_id;
        DROP INDEX IF EXISTS idx_agent_metrics_timestamp;
        DROP INDEX IF EXISTS idx_alerts_agent_id;
        DROP INDEX IF EXISTS idx_alerts_is_resolved;
        DROP INDEX IF EXISTS idx_alerts_severity;
        DROP INDEX IF EXISTS idx_alerts_created_at;
        DROP INDEX IF EXISTS idx_audit_logs_user_id;
        DROP INDEX IF EXISTS idx_audit_logs_timestamp;
        DROP INDEX IF EXISTS idx_audit_logs_action;
        DROP INDEX IF EXISTS idx_audit_logs_resource_type;
        DROP INDEX IF EXISTS idx_scheduled_tasks_agent_id;
        DROP INDEX IF EXISTS idx_scheduled_tasks_group_id;
        DROP INDEX IF EXISTS idx_scheduled_tasks_is_active;
        DROP INDEX IF EXISTS idx_scheduled_tasks_next_run;
    '''
}