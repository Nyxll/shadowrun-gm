#!/usr/bin/env python3
"""
List all columns in characters table
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
    
    cur = conn.cursor()
    
    # Get all columns from characters table
    cur.execute("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_name = 'characters'
        ORDER BY ordinal_position
    """)
    
    columns = cur.fetchall()
    print(f"Characters table has {len(columns)} columns:\n")
    print(f"{'Column Name':<30} {'Type':<20} {'Nullable':<10} {'Default'}")
    print("=" * 100)
    
    for col_name, data_type, nullable, default in columns:
        default_str = str(default)[:30] if default else ""
        print(f"{col_name:<30} {data_type:<20} {nullable:<10} {default_str}")
    
    # Check if ui_state exists
    print("\n" + "=" * 100)
    ui_state_exists = any(col[0] == 'ui_state' for col in columns)
    if ui_state_exists:
        print("✓ ui_state column EXISTS")
    else:
        print("✗ ui_state column MISSING - THIS IS THE PROBLEM!")
    
    conn.close()

if __name__ == "__main__":
    main()
