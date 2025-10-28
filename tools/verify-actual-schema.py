#!/usr/bin/env python3
"""
Verify actual schema for tables we modified
"""
import os
from dotenv import load_dotenv
import psycopg

load_dotenv()

def check_table_columns(table_name):
    """Check actual columns in a table"""
    conn = psycopg.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=int(os.getenv('POSTGRES_PORT')),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB')
    )
    
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
        print(f"  {row[0]:<30} {row[1]:<20} {'NULL' if row[2] == 'YES' else 'NOT NULL'}")
    
    cur.close()
    conn.close()

def list_character_tables():
    """List all character-related tables"""
    conn = psycopg.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=int(os.getenv('POSTGRES_PORT')),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB')
    )
    
    cur = conn.cursor()
    cur.execute("""
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public' AND tablename LIKE 'character_%'
        ORDER BY tablename
    """)
    
    tables = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return tables

def main():
    print("="*80)
    print("ACTUAL DATABASE SCHEMA VERIFICATION")
    print("="*80)
    
    # Get all character tables
    tables = list_character_tables()
    print(f"\nFound {len(tables)} character tables:")
    for t in tables:
        print(f"  - {t}")
    
    # Check specific tables we care about
    important_tables = [
        'character_edges_flaws',
        'character_vehicles',
        'character_skills',
        'character_modifiers',
        'character_spells',
        'character_spirits',
        'character_foci',
        'character_contacts',
        'character_cyberdecks'
    ]
    
    for table in important_tables:
        if table in tables:
            check_table_columns(table)
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()
