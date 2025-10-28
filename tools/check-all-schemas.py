#!/usr/bin/env python3
"""
Check all table schemas to identify mismatches with CRUD operations
"""
import os
from dotenv import load_dotenv
import psycopg

load_dotenv()

def check_table_schema(conn, table_name):
    """Get column info for a table"""
    cur = conn.cursor()
    cur.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns 
        WHERE table_name = %s 
        ORDER BY ordinal_position
    """, (table_name,))
    
    print(f"\n{table_name}:")
    print("-" * 60)
    for row in cur.fetchall():
        nullable = "NULL" if row[2] == 'YES' else "NOT NULL"
        print(f"  {row[0]:<30} {row[1]:<20} {nullable}")
    cur.close()

def main():
    conn = psycopg.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=int(os.getenv('POSTGRES_PORT')),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB')
    )
    
    tables = [
        'characters',
        'character_skills',
        'character_spells',
        'character_spirits',
        'character_foci',
        'character_gear',
        'character_contacts',
        'character_vehicles',
        'character_cyberdecks',
        'character_edges_flaws',
        'character_powers',
        'character_relationships',
        'character_active_effects',
        'character_modifiers'
    ]
    
    print("=" * 60)
    print("TABLE SCHEMAS")
    print("=" * 60)
    
    for table in tables:
        try:
            check_table_schema(conn, table)
        except Exception as e:
            print(f"\n{table}: ERROR - {e}")
    
    conn.close()

if __name__ == "__main__":
    main()
