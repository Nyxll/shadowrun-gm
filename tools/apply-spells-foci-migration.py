#!/usr/bin/env python3
"""
Apply migration 014: Add spells and foci tables
"""
import os
from dotenv import load_dotenv
import psycopg

load_dotenv()

def main():
    """Apply the spells and foci migration"""
    try:
        conn = psycopg.connect(
            host=os.getenv('POSTGRES_HOST'),
            port=os.getenv('POSTGRES_PORT'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            dbname=os.getenv('POSTGRES_DB')
        )
        
        cursor = conn.cursor()
        
        # Read migration file
        with open('migrations/014_add_spells_and_foci.sql', 'r') as f:
            migration_sql = f.read()
        
        print("Applying migration 014: Add spells and foci tables...")
        cursor.execute(migration_sql)
        conn.commit()
        
        print("✓ Migration applied successfully")
        
        # Verify tables were created
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
              AND table_name IN ('character_spells', 'character_foci')
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        print(f"\nCreated tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error applying migration: {e}")
        raise

if __name__ == "__main__":
    main()
