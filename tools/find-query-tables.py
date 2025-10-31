#!/usr/bin/env python3
"""
Find all query/log/conversation tables
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
    
    # Find all tables with query, log, or conversation in name
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema='public' 
        AND (table_name LIKE '%query%' 
             OR table_name LIKE '%log%' 
             OR table_name LIKE '%conversation%'
             OR table_name LIKE '%chat%'
             OR table_name LIKE '%message%')
        ORDER BY table_name
    """)
    
    tables = cur.fetchall()
    print("=== Tables found ===")
    for table in tables:
        print(f"\n{table[0]}:")
        
        # Get structure
        cur.execute(f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = '{table[0]}'
            ORDER BY ordinal_position
        """)
        
        columns = cur.fetchall()
        for col in columns:
            print(f"  - {col[0]}: {col[1]}")
        
        # Get count
        cur.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cur.fetchone()[0]
        print(f"  Total rows: {count}")
    
    conn.close()

if __name__ == "__main__":
    main()
