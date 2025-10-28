#!/usr/bin/env python3
import os
from dotenv import load_dotenv
import psycopg

load_dotenv()

conn = psycopg.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=os.getenv('POSTGRES_PORT'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    dbname=os.getenv('POSTGRES_DB')
)

cursor = conn.cursor()

tables = ['qualities', 'gear', 'gear_items', 'spells', 'powers', 'rules_content']

for table in tables:
    print(f"\n{'='*70}")
    print(f"{table.upper()} TABLE")
    print('='*70)
    
    cursor.execute(f"""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = '{table}'
        ORDER BY ordinal_position
    """)
    
    cols = cursor.fetchall()
    if cols:
        print("Columns:")
        for col in cols:
            print(f"  {col[0]}: {col[1]}")
        
        # Get sample row
        cursor.execute(f"SELECT * FROM {table} LIMIT 1")
        sample = cursor.fetchone()
        if sample:
            print("\nSample data available: Yes")
    else:
        print(f"Table '{table}' not found or has no columns")

conn.close()
