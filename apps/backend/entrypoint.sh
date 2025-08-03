#!/bin/bash
set -e

echo "Starting DexAgents Backend..."

# Create necessary directories
mkdir -p /app/data /app/logs /app/temp /app/agent_installers

# Wait for database to be ready (if PostgreSQL)
if [[ "${DATABASE_URL}" == postgresql* ]]; then
    echo "Waiting for PostgreSQL to be ready..."
    until python -c "
import psycopg2
import os
import sys
try:
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    conn.close()
    print('PostgreSQL is ready!')
except Exception as e:
    print(f'PostgreSQL not ready: {e}')
    sys.exit(1)
"; do
        echo "PostgreSQL is unavailable - sleeping..."
        sleep 2
    done
fi

# Run database migrations
echo "Running database migrations..."
python -c "
from app.migrations.migration_manager import MigrationManager
from app.core.config import settings
import os

if settings.is_postgresql:
    db_path = settings.DATABASE_URL
else:
    db_path = os.path.join('/app', settings.DATABASE_URL)
    
mm = MigrationManager(db_path)
mm.run_migrations()
print('Migrations completed successfully')
"

# Insert default PowerShell commands
echo "Inserting default PowerShell commands..."
python /app/app/scripts/insert_default_commands.py

# Start the application
echo "Starting the application..."
exec python run.py