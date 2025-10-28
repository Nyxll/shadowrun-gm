#!/usr/bin/env python3
"""
Apply the new characters v2 schema to the database
"""
import os
from dotenv import load_dotenv
import psycopg

load_dotenv()

def apply_schema():
    """Apply the characters v2 schema"""
    
    # Read schema file
    with open('schema/characters_v2.sql', 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    # Connect to database
    conn = psycopg.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB')
    )
    
    cursor = conn.cursor()
    
    try:
        print("Applying characters v2 schema...")
        print("=" * 70)
        
        # Execute schema
        cursor.execute(schema_sql)
        conn.commit()
        
        print("✓ Schema applied successfully!")
        print()
        
        # Verify tables were created
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE 'character%'
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        print("Created tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        print()
        print("=" * 70)
        print("Schema migration complete!")
        
    except Exception as e:
        conn.rollback()
        print(f"Error applying schema: {e}")
        raise
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    apply_schema()
