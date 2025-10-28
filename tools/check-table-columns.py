#!/usr/bin/env python3
"""
Check actual column names in tables
"""
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

tables = ['character_skills', 'character_modifiers', 'character_active_effects']

for table in tables:
    print(f"\n{table} columns:")
    print("=" * 60)
    cur = conn.cursor()
    cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = %s 
        ORDER BY ordinal_position
    """, (table,))
    for row in cur.fetchall():
        print(f"  {row[0]:30} {row[1]}")
    cur.close()

conn.close()
