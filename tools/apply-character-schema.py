#!/usr/bin/env python3
"""
Apply character system schema to database
"""
import psycopg2
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# Database configuration
db_config = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', 5432)),
    'database': os.getenv('POSTGRES_DB', 'postgres'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', '')
}

# Read schema file
schema_file = Path(__file__).parent.parent / 'schema' / 'character_system.sql'
with open(schema_file, 'r', encoding='utf-8') as f:
    schema_sql = f.read()

# Connect and apply schema
print("Connecting to database...")
conn = psycopg2.connect(**db_config)
conn.autocommit = True

try:
    print("Applying character system schema...")
    cur = conn.cursor()
    cur.execute(schema_sql)
    print("✓ Schema applied successfully!")
    
    # Check what was created
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name IN (
            'metatypes', 'qualities', 'skills', 'powers', 'spells', 'totems',
            'creatures', 'characters', 'contacts', 
            'reference_load_history', 'character_history'
        )
        ORDER BY table_name
    """)
    
    tables = cur.fetchall()
    print(f"\n✓ Created {len(tables)} tables:")
    for table in tables:
        print(f"  - {table[0]}")
    
    # Check views
    cur.execute("""
        SELECT table_name 
        FROM information_schema.views 
        WHERE table_schema = 'public' 
        AND table_name IN ('character_summary', 'reference_data_stats')
        ORDER BY table_name
    """)
    
    views = cur.fetchall()
    if views:
        print(f"\n✓ Created {len(views)} views:")
        for view in views:
            print(f"  - {view[0]}")
    
    # Show reference data stats
    cur.execute("SELECT * FROM reference_data_stats ORDER BY table_name")
    stats = cur.fetchall()
    print("\n📊 Current data counts:")
    for stat in stats:
        print(f"  {stat[0]:20} {stat[1]:4} items")
    
finally:
    conn.close()
    print("\n✓ Done!")
