#!/usr/bin/env python3
"""
Test database connection
"""
import os
from dotenv import load_dotenv
import psycopg

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', '127.0.0.1'),
    'port': int(os.getenv('POSTGRES_PORT', '5434')),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'dbname': os.getenv('POSTGRES_DB', 'postgres')
}

print("Testing database connection...")
print(f"Host: {DB_CONFIG['host']}")
print(f"Port: {DB_CONFIG['port']}")
print(f"User: {DB_CONFIG['user']}")
print(f"Database: {DB_CONFIG['dbname']}")
print()

try:
    # Try to connect with a short timeout
    conn = psycopg.connect(**DB_CONFIG, connect_timeout=5)
    print("✓ Connection successful!")
    
    # Try a simple query
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM characters")
    count = cursor.fetchone()[0]
    print(f"✓ Query successful! Found {count} characters")
    
    cursor.close()
    conn.close()
    print("✓ Connection closed cleanly")
    
except Exception as e:
    print(f"✗ Connection failed: {e}")
    import traceback
    traceback.print_exc()
