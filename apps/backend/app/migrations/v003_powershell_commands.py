"""
Migration v003: Add PowerShell Commands table
"""

MIGRATION = {
    'version': 'v003',
    'description': 'Add PowerShell Commands table for saved command templates',
    'up': '''
        -- Create powershell_commands table
        CREATE TABLE IF NOT EXISTS powershell_commands (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            category TEXT NOT NULL DEFAULT 'general',
            command TEXT NOT NULL,
            parameters TEXT, -- JSON array of parameters
            tags TEXT, -- JSON array of tags
            version TEXT DEFAULT '1.0',
            author TEXT DEFAULT 'Unknown',
            is_system INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Create index for faster queries
        CREATE INDEX IF NOT EXISTS idx_powershell_commands_category ON powershell_commands(category);
        CREATE INDEX IF NOT EXISTS idx_powershell_commands_author ON powershell_commands(author);
        CREATE INDEX IF NOT EXISTS idx_powershell_commands_created_at ON powershell_commands(created_at);
    ''',
    'down': '''
        DROP TABLE IF EXISTS powershell_commands;
    '''
}