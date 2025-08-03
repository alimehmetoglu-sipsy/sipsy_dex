"""
Add indexes for PostgreSQL performance optimization
"""
from datetime import datetime

UP_SQL = """
-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_agents_hostname ON agents(hostname);
CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status);
CREATE INDEX IF NOT EXISTS idx_command_history_agent_id ON command_history(agent_id);
CREATE INDEX IF NOT EXISTS idx_command_history_timestamp ON command_history(timestamp);
CREATE INDEX IF NOT EXISTS idx_agent_metrics_agent_id ON agent_metrics(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_metrics_timestamp ON agent_metrics(timestamp);
CREATE INDEX IF NOT EXISTS idx_alerts_agent_id ON alerts(agent_id);
CREATE INDEX IF NOT EXISTS idx_alerts_is_resolved ON alerts(is_resolved);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp);

-- JSONB indexes for better performance
CREATE INDEX IF NOT EXISTS idx_agents_tags ON agents USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_agents_system_info ON agents USING GIN(system_info);
"""

DOWN_SQL = """
DROP INDEX IF EXISTS idx_agents_tags;
DROP INDEX IF EXISTS idx_agents_system_info;
DROP INDEX IF EXISTS idx_audit_logs_timestamp;
DROP INDEX IF EXISTS idx_audit_logs_user_id;
DROP INDEX IF EXISTS idx_alerts_is_resolved;
DROP INDEX IF EXISTS idx_alerts_agent_id;
DROP INDEX IF EXISTS idx_agent_metrics_timestamp;
DROP INDEX IF EXISTS idx_agent_metrics_agent_id;
DROP INDEX IF EXISTS idx_command_history_timestamp;
DROP INDEX IF EXISTS idx_command_history_agent_id;
DROP INDEX IF EXISTS idx_agents_status;
DROP INDEX IF EXISTS idx_agents_hostname;
"""

migration = {
    'version': 'v002_postgresql',
    'description': 'Add PostgreSQL indexes',
    'up': UP_SQL,
    'down': DOWN_SQL,
    'created_at': datetime.now().isoformat(),
    'updated_at': datetime.now().isoformat()
}