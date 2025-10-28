#!/usr/bin/env python3
"""
Fix campaign schema - drop existing table and recreate with correct types
"""
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=os.getenv('POSTGRES_PORT'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    dbname=os.getenv('POSTGRES_DB')
)

cursor = conn.cursor()

try:
    print("Dropping existing campaigns table (if exists)...")
    cursor.execute("DROP TABLE IF EXISTS campaign_npcs CASCADE")
    cursor.execute("DROP TABLE IF EXISTS campaign_characters CASCADE")
    cursor.execute("DROP TABLE IF EXISTS campaigns CASCADE")
    conn.commit()
    print("✓ Dropped existing tables")
    
    print("\nApplying migration 016 with correct UUID types...")
    
    # Read and execute migration
    with open('migrations/016_add_campaign_management.sql', 'r') as f:
        migration_sql = f.read()
    
    cursor.execute(migration_sql)
    conn.commit()
    
    print("✓ Migration applied successfully")
    
    # Verify tables
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
          AND table_name IN ('campaigns', 'campaign_npcs', 'campaign_characters')
        ORDER BY table_name
    """)
    
    tables = cursor.fetchall()
    print(f"\n✓ Created {len(tables)} tables:")
    for table in tables:
        print(f"  - {table[0]}")
    
    # Verify ID types
    cursor.execute("""
        SELECT table_name, column_name, data_type
        FROM information_schema.columns
        WHERE table_name IN ('campaigns', 'campaign_npcs', 'campaign_characters')
          AND column_name = 'id'
        ORDER BY table_name
    """)
    
    id_types = cursor.fetchall()
    print(f"\n✓ ID column types:")
    for row in id_types:
        print(f"  - {row[0]}.{row[1]}: {row[2]}")
    
    print("\n✓ Campaign management system ready!")
    
except Exception as e:
    conn.rollback()
    print(f"\n✗ Error: {e}")
    raise

finally:
    cursor.close()
    conn.close()
