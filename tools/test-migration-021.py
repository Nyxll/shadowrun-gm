#!/usr/bin/env python3
"""
Quick test to apply migration 021
"""
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

try:
    print("Connecting to database...")
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB'),
        connect_timeout=5
    )
    
    print("Connected. Checking if master_spells table exists...")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'master_spells'
        );
    """)
    exists = cursor.fetchone()[0]
    
    if exists:
        print("✓ master_spells table already exists!")
        cursor.execute("SELECT COUNT(*) FROM master_spells")
        count = cursor.fetchone()[0]
        print(f"  Contains {count} spells")
    else:
        print("✗ master_spells table does not exist")
        print("Applying migration...")
        
        with open('migrations/021_add_master_spells_table.sql', 'r') as f:
            sql = f.read()
        
        cursor.execute(sql)
        conn.commit()
        print("✓ Migration applied successfully!")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
