"""
Add PowerShell commands table for PostgreSQL
"""
from datetime import datetime

UP_SQL = """
-- Create powershell_commands table
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
);

-- Create indexes for powershell_commands
CREATE INDEX IF NOT EXISTS idx_powershell_commands_category ON powershell_commands(category);
CREATE INDEX IF NOT EXISTS idx_powershell_commands_name ON powershell_commands(name);
CREATE INDEX IF NOT EXISTS idx_powershell_commands_tags ON powershell_commands USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_powershell_commands_is_system ON powershell_commands(is_system);
"""

DOWN_SQL = """
DROP INDEX IF EXISTS idx_powershell_commands_is_system;
DROP INDEX IF EXISTS idx_powershell_commands_tags;
DROP INDEX IF EXISTS idx_powershell_commands_name;
DROP INDEX IF EXISTS idx_powershell_commands_category;
DROP TABLE IF EXISTS powershell_commands CASCADE;
"""

MIGRATION = {
    'version': 'v003_postgresql',
    'description': 'Add PowerShell commands table for PostgreSQL',
    'up': UP_SQL,
    'down': DOWN_SQL,
    'created_at': datetime.now().isoformat(),
    'updated_at': datetime.now().isoformat()
}