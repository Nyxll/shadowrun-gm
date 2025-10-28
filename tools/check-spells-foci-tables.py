#!/usr/bin/env python3
"""
Check if spells and foci tables exist and their structure
"""
import os
from dotenv import load_dotenv
import psycopg

load_dotenv()

def main():
    """Check spells and foci tables"""
    try:
        conn = psycopg.connect(
            host=os.getenv('POSTGRES_HOST'),
            port=os.getenv('POSTGRES_PORT'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            dbname=os.getenv('POSTGRES_DB')
        )
        
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
              AND table_name IN ('character_spells', 'character_foci')
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        print("Existing tables:")
        for table in tables:
            print(f"  - {table[0]}")
            
            # Get columns for this table
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                  AND table_name = %s
                ORDER BY ordinal_position
            """, (table[0],))
            
            columns = cursor.fetchall()
            print(f"    Columns:")
            for col in columns:
                print(f"      - {col[0]} ({col[1]})")
            print()
        
        if not tables:
            print("  No spells/foci tables found - migration needed")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")
        raise

if __name__ == "__main__":
    main()
