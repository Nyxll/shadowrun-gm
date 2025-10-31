#!/usr/bin/env python3
"""
Apply migration 024 to add pool columns to characters table
"""
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

def main():
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB')
    )
    
    try:
        cur = conn.cursor()
        
        print("Applying migration 024: Add pool columns...")
        
        # Read and execute migration
        with open('migrations/024_add_pool_columns.sql', 'r') as f:
            migration_sql = f.read()
        
        cur.execute(migration_sql)
        conn.commit()
        
        print("✓ Migration applied successfully")
        
        # Verify columns were added
        cur.execute("""
            SELECT column_name, data_type, column_default
            FROM information_schema.columns
            WHERE table_name = 'characters'
            AND column_name IN ('combat_pool', 'task_pool', 'hacking_pool')
            ORDER BY column_name
        """)
        
        columns = cur.fetchall()
        print("\nAdded columns:")
        for col in columns:
            print(f"  - {col[0]}: {col[1]} (default: {col[2]})")
        
        cur.close()
    finally:
        conn.close()

if __name__ == "__main__":
    main()
