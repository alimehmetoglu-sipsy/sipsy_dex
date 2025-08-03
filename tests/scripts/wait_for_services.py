#!/usr/bin/env python3
"""
Wait for services to be ready before running tests
"""

import os
import time
import requests
import psycopg2
import redis
from typing import Dict, Callable, Any

# Service configuration
SERVICES = {
    'backend': {
        'url': os.getenv('BACKEND_URL', 'http://localhost:8081'),
        'health_endpoint': '/api/v1/system/health',
        'timeout': 120,  # 2 minutes
    },
    'frontend': {
        'url': os.getenv('FRONTEND_URL', 'http://localhost:3001'),
        'health_endpoint': '/api/health',
        'timeout': 120,
    },
    'database': {
        'host': os.getenv('DB_HOST', 'postgres-test'),
        'port': int(os.getenv('DB_PORT', '5432')),
        'database': os.getenv('DB_NAME', 'dexagent_test'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'postgres123'),
        'timeout': 60,
    },
    'redis': {
        'host': os.getenv('REDIS_HOST', 'redis-test'),
        'port': int(os.getenv('REDIS_PORT', '6379')),
        'timeout': 60,
    }
}

def check_http_service(service_name: str, config: Dict[str, Any]) -> bool:
    """Check if HTTP service is ready"""
    try:
        url = f"{config['url']}{config['health_endpoint']}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            print(f"✓ {service_name} is ready")
            return True
        else:
            print(f"✗ {service_name} returned status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ {service_name} connection failed: {e}")
        return False

def check_database(config: Dict[str, Any]) -> bool:
    """Check if database is ready"""
    try:
        conn = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            database=config['database'],
            user=config['user'],
            password=config['password'],
            connect_timeout=5
        )
        
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        cursor.fetchone()
        cursor.close()
        conn.close()
        
        print("✓ Database is ready")
        return True
        
    except psycopg2.Error as e:
        print(f"✗ Database connection failed: {e}")
        return False

def check_redis(config: Dict[str, Any]) -> bool:
    """Check if Redis is ready"""
    try:
        r = redis.Redis(
            host=config['host'],
            port=config['port'],
            socket_connect_timeout=5,
            socket_timeout=5
        )
        
        r.ping()
        print("✓ Redis is ready")
        return True
        
    except redis.RedisError as e:
        print(f"✗ Redis connection failed: {e}")
        return False

def wait_for_service(service_name: str, check_func: Callable, config: Dict[str, Any]) -> bool:
    """Wait for a service to be ready"""
    print(f"Waiting for {service_name}...")
    
    timeout = config.get('timeout', 60)
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if check_func(config):
            return True
            
        time.sleep(2)
        
    print(f"✗ {service_name} failed to become ready within {timeout} seconds")
    return False

def main():
    """Main function to wait for all services"""
    print("DexAgent Test Environment - Waiting for Services")
    print("=" * 50)
    
    all_ready = True
    
    # Check Backend
    if not wait_for_service('backend', check_http_service, SERVICES['backend']):
        all_ready = False
        
    # Check Frontend
    if not wait_for_service('frontend', check_http_service, SERVICES['frontend']):
        all_ready = False
        
    # Check Database
    if not wait_for_service('database', check_database, SERVICES['database']):
        all_ready = False
        
    # Check Redis
    if not wait_for_service('redis', check_redis, SERVICES['redis']):
        all_ready = False
        
    print("=" * 50)
    
    if all_ready:
        print("✓ All services are ready! Starting tests...")
        return 0
    else:
        print("✗ Some services failed to start. Aborting tests.")
        return 1

if __name__ == '__main__':
    import sys
    sys.exit(main())