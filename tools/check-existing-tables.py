#!/usr/bin/env python3
"""
Check what character-related tables already exist
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

db_config = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', 5432)),
    'database': os.getenv('POSTGRES_DB', 'postgres'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', '')
}

conn = psycopg2.connect(**db_config)
cur = conn.cursor()

# Check for character system tables
tables_to_check = [
    'metatypes', 'qualities', 'skills', 'powers', 'spells', 'totems',
    'creatures', 'characters', 'contacts', 
    'reference_load_history', 'character_history'
]

print("Checking for existing tables...")
print("-" * 60)

for table in tables_to_check:
    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = %s
        )
    """, (table,))
    
    exists = cur.fetchone()[0]
    
    if exists:
        # Get row count
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        count = cur.fetchone()[0]
        
        # Get owner
        cur.execute("""
            SELECT tableowner 
            FROM pg_tables 
            WHERE schemaname = 'public' 
            AND tablename = %s
        """, (table,))
        owner = cur.fetchone()[0]
        
        print(f"✓ {table:25} EXISTS  ({count:4} rows, owner: {owner})")
    else:
        print(f"✗ {table:25} MISSING")

conn.close()
