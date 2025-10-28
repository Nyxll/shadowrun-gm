#!/usr/bin/env python3
"""
Check which character-related tables exist in the database
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

cur = conn.cursor()
cur.execute("""
    SELECT tablename 
    FROM pg_tables 
    WHERE schemaname='public' 
      AND tablename LIKE 'character_%' 
    ORDER BY tablename
""")

print("Character-related tables in database:")
print("=" * 60)
for row in cur.fetchall():
    print(f"  - {row[0]}")

cur.close()
conn.close()
