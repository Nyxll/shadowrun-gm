#!/usr/bin/env python3
"""
Check actual schema of specific tables
"""
import os
from dotenv import load_dotenv
import psycopg

load_dotenv()

def check_table_schema(table_name: str):
    """Check columns in a specific table"""
    conn = psycopg.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=int(os.getenv('POSTGRES_PORT')),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB')
    )
    
    cur = conn.cursor()
    
    # Get column information
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
    
    columns = cur.fetchall()
    
    print(f"\n{'='*80}")
    print(f"TABLE: {table_name}")
    print(f"{'='*80}")
    
    if not columns:
        print(f"⚠️  Table '{table_name}' not found!")
        return
    
    print(f"\nColumns ({len(columns)}):")
    print(f"{'Column Name':<30} {'Type':<20} {'Nullable':<10} {'Default'}")
    print("-" * 80)
    
    for col_name, data_type, nullable, default in columns:
        default_str = str(default)[:30] if default else ''
        print(f"{col_name:<30} {data_type:<20} {nullable:<10} {default_str}")
    
    cur.close()
    conn.close()

def main():
    tables = [
        'character_edges_flaws',
        'character_cyberdecks',
        'character_vehicles',
        'character_skills',
        'character_modifiers'
    ]
    
    for table in tables:
        check_table_schema(table)

if __name__ == "__main__":
    main()
