-- Initialize test database
-- This script sets up the test database with required extensions and initial data

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create test schemas if needed
CREATE SCHEMA IF NOT EXISTS test_data;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE dexagent_test TO postgres;
GRANT ALL PRIVILEGES ON SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON SCHEMA test_data TO postgres;

-- Insert test user data
INSERT INTO users (id, username, email, password_hash, is_active, created_at, updated_at)
VALUES 
    ('550e8400-e29b-41d4-a716-446655440000', 'admin', 'admin@dexagent.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewAmKoNbOa9LRlWa', true, NOW(), NOW()),
    ('550e8400-e29b-41d4-a716-446655440001', 'testuser', 'test@dexagent.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewAmKoNbOa9LRlWa', true, NOW(), NOW())
ON CONFLICT (username) DO NOTHING;

-- Insert test agent data
INSERT INTO agents (id, name, hostname, ip_address, os, version, status, capabilities, created_at, updated_at, last_seen)
VALUES 
    ('test-agent-001', 'Test Agent 1', 'test-host-1', '192.168.1.101', 'Windows 10', '1.0.0', 'offline', '["powershell", "cmd"]', NOW(), NOW(), NOW() - INTERVAL '5 minutes'),
    ('test-agent-002', 'Test Agent 2', 'test-host-2', '192.168.1.102', 'Windows 11', '1.0.0', 'offline', '["powershell", "cmd", "python"]', NOW(), NOW(), NOW() - INTERVAL '10 minutes'),
    ('test-agent-003', 'Test Agent 3', 'test-host-3', '192.168.1.103', 'Windows Server 2019', '1.0.0', 'offline', '["powershell", "cmd"]', NOW(), NOW(), NOW() - INTERVAL '1 hour')
ON CONFLICT (id) DO NOTHING;

-- Insert test command data
INSERT INTO saved_commands (id, name, command, description, category, timeout, created_by, created_at, updated_at)
VALUES 
    (gen_random_uuid(), 'Test Get Date', 'Get-Date', 'Test command to get current date', 'system', 30, 'admin', NOW(), NOW()),
    (gen_random_uuid(), 'Test Get Process', 'Get-Process | Select-Object -First 5 Name, Id', 'Test command to get process list', 'system', 30, 'admin', NOW(), NOW()),
    (gen_random_uuid(), 'Test System Info', 'Get-ComputerInfo | Select-Object WindowsProductName, TotalPhysicalMemory', 'Test command to get system information', 'system', 60, 'admin', NOW(), NOW())
ON CONFLICT (name) DO NOTHING;

-- Insert test settings
INSERT INTO settings (key, value, description, created_at, updated_at)
VALUES 
    ('default_command_timeout', '30', 'Default command execution timeout in seconds', NOW(), NOW()),
    ('max_concurrent_commands', '10', 'Maximum number of concurrent commands per agent', NOW(), NOW()),
    ('agent_heartbeat_interval', '30', 'Agent heartbeat interval in seconds', NOW(), NOW()),
    ('openai_api_key', NULL, 'OpenAI API key for AI features', NOW(), NOW()),
    ('test_mode', 'true', 'Test mode flag', NOW(), NOW())
ON CONFLICT (key) DO NOTHING;

-- Create test data in separate schema for cleanup
CREATE TABLE IF NOT EXISTS test_data.test_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    cleaned_up BOOLEAN DEFAULT FALSE
);

-- Insert current test session
INSERT INTO test_data.test_sessions (session_name)
VALUES ('integration_test_' || EXTRACT(EPOCH FROM NOW()));

-- Create indexes for better test performance
CREATE INDEX IF NOT EXISTS idx_agents_test_status ON agents(status) WHERE id LIKE 'test_%';
CREATE INDEX IF NOT EXISTS idx_command_executions_test_agent ON command_executions(agent_id) WHERE agent_id LIKE 'test_%';
CREATE INDEX IF NOT EXISTS idx_agent_metrics_test_agent ON agent_metrics(agent_id, timestamp) WHERE agent_id LIKE 'test_%';

-- Create functions for test cleanup
CREATE OR REPLACE FUNCTION cleanup_test_data()
RETURNS VOID AS $$
BEGIN
    -- Delete test command executions
    DELETE FROM command_executions WHERE agent_id LIKE 'test_%';
    
    -- Delete test agent metrics
    DELETE FROM agent_metrics WHERE agent_id LIKE 'test_%';
    
    -- Delete test agents
    DELETE FROM agents WHERE id LIKE 'test_%';
    
    -- Delete test commands
    DELETE FROM saved_commands WHERE name LIKE 'Test_%';
    
    -- Delete test audit logs
    DELETE FROM audit_logs WHERE details LIKE '%test_%';
    
    -- Mark test session as cleaned up
    UPDATE test_data.test_sessions 
    SET cleaned_up = TRUE 
    WHERE session_name LIKE 'integration_test_%' 
    AND cleaned_up = FALSE;
    
    RAISE NOTICE 'Test data cleanup completed';
END;
$$ LANGUAGE plpgsql;

-- Create function to generate test agents
CREATE OR REPLACE FUNCTION generate_test_agents(agent_count INTEGER DEFAULT 5)
RETURNS VOID AS $$
DECLARE
    i INTEGER;
    agent_id TEXT;
    agent_name TEXT;
    hostname TEXT;
    ip_address TEXT;
BEGIN
    FOR i IN 1..agent_count LOOP
        agent_id := 'test_perf_agent_' || i;
        agent_name := 'Performance Test Agent ' || i;
        hostname := 'perf-test-host-' || i;
        ip_address := '192.168.10.' || (100 + i);
        
        INSERT INTO agents (id, name, hostname, ip_address, os, version, status, capabilities, created_at, updated_at, last_seen)
        VALUES (
            agent_id,
            agent_name,
            hostname,
            ip_address,
            'Windows 10',
            '1.0.0',
            'online',
            '["powershell", "cmd"]',
            NOW(),
            NOW(),
            NOW()
        )
        ON CONFLICT (id) DO UPDATE SET
            status = 'online',
            last_seen = NOW(),
            updated_at = NOW();
    END LOOP;
    
    RAISE NOTICE 'Generated % test agents', agent_count;
END;
$$ LANGUAGE plpgsql;

-- Create function to simulate agent metrics
CREATE OR REPLACE FUNCTION simulate_agent_metrics(agent_id_param TEXT, metric_count INTEGER DEFAULT 10)
RETURNS VOID AS $$
DECLARE
    i INTEGER;
    timestamp_val TIMESTAMP;
    cpu_usage NUMERIC;
    memory_usage NUMERIC;
    disk_usage NUMERIC;
BEGIN
    FOR i IN 1..metric_count LOOP
        timestamp_val := NOW() - (i || ' minutes')::INTERVAL;
        cpu_usage := RANDOM() * 100;
        memory_usage := 40 + (RANDOM() * 40); -- 40-80% memory usage
        disk_usage := 30 + (RANDOM() * 30);   -- 30-60% disk usage
        
        INSERT INTO agent_metrics (agent_id, timestamp, cpu_usage, memory_usage, disk_usage, network_in, network_out)
        VALUES (
            agent_id_param,
            timestamp_val,
            cpu_usage,
            memory_usage,
            disk_usage,
            FLOOR(RANDOM() * 1000000)::BIGINT, -- Random network in bytes
            FLOOR(RANDOM() * 1000000)::BIGINT  -- Random network out bytes
        )
        ON CONFLICT (agent_id, timestamp) DO NOTHING;
    END LOOP;
    
    RAISE NOTICE 'Generated % metrics for agent %', metric_count, agent_id_param;
END;
$$ LANGUAGE plpgsql;

-- Create test roles and permissions if needed
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'test_user') THEN
        CREATE ROLE test_user WITH LOGIN PASSWORD 'test_password';
        GRANT CONNECT ON DATABASE dexagent_test TO test_user;
        GRANT USAGE ON SCHEMA public TO test_user;
        GRANT SELECT ON ALL TABLES IN SCHEMA public TO test_user;
    END IF;
END
$$;

-- Final verification
SELECT 'Test database initialization completed successfully' AS status;