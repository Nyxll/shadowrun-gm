#!/usr/bin/env python3
"""
Diagnose test failures by checking actual schema requirements
"""
import os
import sys
from dotenv import load_dotenv
import psycopg

load_dotenv()

def check_table_schema(table_name):
    """Check schema for a table"""
    conn = psycopg.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=int(os.getenv('POSTGRES_PORT')),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB')
    )
    
    cur = conn.cursor()
    
    # Get column info
    cur.execute("""
        SELECT 
            column_name,
            data_type,
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_name = %s
        ORDER BY ordinal_position
    """, (table_name,))
    
    print(f"\n{'='*70}")
    print(f"Schema for {table_name}")
    print(f"{'='*70}")
    print(f"{'Column':<30} {'Type':<20} {'Nullable':<10} {'Default'}")
    print(f"{'-'*70}")
    
    for row in cur.fetchall():
        col_name, data_type, nullable, default = row
        nullable_str = 'YES' if nullable == 'YES' else 'NO'
        default_str = str(default)[:20] if default else ''
        print(f"{col_name:<30} {data_type:<20} {nullable_str:<10} {default_str}")
    
    cur.close()
    conn.close()

def main():
    """Check schemas for tables mentioned in test failures"""
    tables = [
        'character_spells',
        'character_active_effects',
        'character_modifiers',
        'character_skills'
    ]
    
    for table in tables:
        try:
            check_table_schema(table)
        except Exception as e:
            print(f"\nError checking {table}: {e}")

if __name__ == "__main__":
    main()
