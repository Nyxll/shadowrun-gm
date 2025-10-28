#!/usr/bin/env python3
"""
Apply the character modifier fixes migration
"""
import os
from dotenv import load_dotenv
import psycopg

load_dotenv()

def apply_migration():
    """Apply the SQL migration"""
    conn = psycopg.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB')
    )
    
    # Read the migration file
    with open('migrations/006_fix_character_modifiers.sql', 'r') as f:
        sql = f.read()
    
    print("Applying character modifier fixes...")
    print("=" * 80)
    
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        print("✓ Migration applied successfully!")
        cursor.close()
    except Exception as e:
        print(f"✗ Error applying migration: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    apply_migration()
