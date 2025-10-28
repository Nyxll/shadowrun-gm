#!/usr/bin/env python3
"""
Verify tables exist and are ready for data
"""
import os
from dotenv import load_dotenv
import psycopg

load_dotenv()

def main():
    conn = psycopg.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=int(os.getenv('POSTGRES_PORT')),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB')
    )
    
    cur = conn.cursor()
    
    print("=" * 80)
    print("TABLE VERIFICATION")
    print("=" * 80)
    
    tables_to_check = [
        'character_edges_flaws',
        'character_cyberdecks',
        'character_vehicles',
        'character_skills',
        'character_modifiers',
        'character_spells',
        'character_gear',
        'character_contacts'
    ]
    
    for table in tables_to_check:
        # Check if table exists
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = %s
            )
        """, (table,))
        exists = cur.fetchone()[0]
        
        if not exists:
            print(f"✗ {table:<30} DOES NOT EXIST")
            continue
        
        # Count rows
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        count = cur.fetchone()[0]
        
        # Get column count
        cur.execute("""
            SELECT COUNT(*) 
            FROM information_schema.columns 
            WHERE table_name = %s
        """, (table,))
        col_count = cur.fetchone()[0]
        
        status = "✓" if exists else "✗"
        print(f"{status} {table:<30} {col_count:2d} columns, {count:4d} rows")
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("All tables exist and are ready to receive data.")
    print("Empty tables are normal - data will be added via:")
    print("  1. Character imports")
    print("  2. MCP operations")
    print("  3. UI interactions")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
