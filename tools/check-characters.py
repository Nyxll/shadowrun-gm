#!/usr/bin/env python3
"""Check what characters exist in the database"""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', '127.0.0.1'),
    'port': os.getenv('POSTGRES_PORT', '5434'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'database': os.getenv('POSTGRES_DB', 'postgres')
}

try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Check both possible character tables
    print("Checking 'characters' table:")
    cursor.execute("SELECT COUNT(*) FROM characters")
    count = cursor.fetchone()[0]
    print(f"  Total: {count}")
    
    if count > 0:
        cursor.execute("SELECT id, name, street_name FROM characters LIMIT 10")
        for row in cursor.fetchall():
            print(f"  - ID {row[0]}: {row[1]} ({row[2]})")
    
    print("\nChecking 'sr_characters' table:")
    try:
        cursor.execute("SELECT COUNT(*) FROM sr_characters")
        count = cursor.fetchone()[0]
        print(f"  Total: {count}")
        
        if count > 0:
            cursor.execute("SELECT id, name, player_name FROM sr_characters LIMIT 10")
            for row in cursor.fetchall():
                print(f"  - ID {row[0]}: {row[1]} (Player: {row[2]})")
    except Exception as e:
        print(f"  Table doesn't exist or error: {e}")
    
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
