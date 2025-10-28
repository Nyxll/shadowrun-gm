#!/usr/bin/env python3
"""
Apply schema v5 - Adds character_spirits table
"""
import os
from dotenv import load_dotenv
import psycopg

load_dotenv()

def apply_schema():
    """Apply schema-v5.sql to database"""
    conn = psycopg.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB')
    )
    
    cursor = conn.cursor()
    
    print("Reading schema-v5.sql...")
    with open('schema-v5.sql', 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    print("Applying schema...")
    try:
        cursor.execute(schema_sql)
        conn.commit()
        print("✓ Schema v5 applied successfully!")
        print("✓ character_spirits table created")
    except Exception as e:
        print(f"✗ Error applying schema: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    apply_schema()
