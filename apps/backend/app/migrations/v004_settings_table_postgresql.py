"""
Migration v004: Create settings table (PostgreSQL)
"""

def upgrade_postgresql(cursor):
    """Upgrade PostgreSQL database"""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            id SERIAL PRIMARY KEY,
            key VARCHAR(255) UNIQUE NOT NULL,
            value TEXT,
            is_encrypted BOOLEAN DEFAULT FALSE,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_settings_key ON settings(key)")
    
    print("Settings table created successfully (PostgreSQL)")

def downgrade_postgresql(cursor):
    """Downgrade PostgreSQL database"""
    cursor.execute("DROP TABLE IF EXISTS settings")
    print("Settings table dropped (PostgreSQL)")