#!/usr/bin/env python3
"""
Check all UUID columns across all tables to understand the UUID architecture
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
    
    # Find all UUID columns
    cur.execute("""
        SELECT 
            table_name,
            column_name,
            is_nullable
        FROM information_schema.columns 
        WHERE data_type = 'uuid'
        ORDER BY table_name, column_name
    """)
    
    print("=" * 80)
    print("ALL UUID COLUMNS IN DATABASE")
    print("=" * 80)
    
    current_table = None
    for row in cur.fetchall():
        table_name, column_name, is_nullable = row
        nullable = "NULL" if is_nullable == 'YES' else "NOT NULL"
        
        if table_name != current_table:
            print(f"\n{table_name}:")
            current_table = table_name
        
        print(f"  {column_name:<30} {nullable}")
    
    # Check for tables with INTEGER ids that should be UUID
    print("\n" + "=" * 80)
    print("TABLES WITH INTEGER IDs (Potential UUID Migration Candidates)")
    print("=" * 80)
    
    cur.execute("""
        SELECT 
            table_name,
            column_name,
            data_type
        FROM information_schema.columns 
        WHERE column_name IN ('id', 'character_id') 
        AND data_type IN ('integer', 'bigint')
        ORDER BY table_name
    """)
    
    for row in cur.fetchall():
        print(f"  {row[0]:<40} {row[1]:<20} {row[2]}")
    
    # Check users table structure
    print("\n" + "=" * 80)
    print("USERS TABLE (for player/user UUIDs)")
    print("=" * 80)
    
    cur.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns 
        WHERE table_name = 'users'
        ORDER BY ordinal_position
    """)
    
    result = cur.fetchall()
    if result:
        for row in result:
            nullable = "NULL" if row[2] == 'YES' else "NOT NULL"
            print(f"  {row[0]:<30} {row[1]:<20} {nullable}")
    else:
        print("  [users table does not exist]")
    
    # Check campaigns table
    print("\n" + "=" * 80)
    print("CAMPAIGNS TABLE")
    print("=" * 80)
    
    cur.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns 
        WHERE table_name = 'campaigns'
        ORDER BY ordinal_position
    """)
    
    result = cur.fetchall()
    if result:
        for row in result:
            nullable = "NULL" if row[2] == 'YES' else "NOT NULL"
            print(f"  {row[0]:<30} {row[1]:<20} {nullable}")
    else:
        print("  [campaigns table does not exist]")
    
    # Check character_campaign_links
    print("\n" + "=" * 80)
    print("CHARACTER_CAMPAIGN_LINKS TABLE")
    print("=" * 80)
    
    cur.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns 
        WHERE table_name = 'character_campaign_links'
        ORDER BY ordinal_position
    """)
    
    result = cur.fetchall()
    if result:
        for row in result:
            nullable = "NULL" if row[2] == 'YES' else "NOT NULL"
            print(f"  {row[0]:<30} {row[1]:<20} {nullable}")
    else:
        print("  [character_campaign_links table does not exist]")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
