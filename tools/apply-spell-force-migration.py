#!/usr/bin/env python3
"""
Apply migration 018: Add spell force column
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

def main():
    print("Applying migration 018: Add spell force column...")
    
    conn = psycopg.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Read migration file
        with open('migrations/018_add_spell_force.sql', 'r') as f:
            migration_sql = f.read()
        
        # Execute migration
        cursor.execute(migration_sql)
        conn.commit()
        
        print("✓ Migration applied successfully!")
        
        # Check if column was added
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'character_spells' 
            AND column_name = 'learned_force'
        """)
        
        result = cursor.fetchone()
        if result:
            print(f"✓ Column 'learned_force' added: {result[1]}")
        else:
            print("✗ Column not found after migration")
        
    except Exception as e:
        conn.rollback()
        print(f"✗ Migration failed: {e}")
        raise
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
