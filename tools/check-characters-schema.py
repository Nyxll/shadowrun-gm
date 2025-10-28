#!/usr/bin/env python3
"""Check characters table schema"""
import os
from dotenv import load_dotenv
import psycopg

load_dotenv()

conn = psycopg.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=int(os.getenv('POSTGRES_PORT')),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    dbname=os.getenv('POSTGRES_DB')
)

cur = conn.cursor()
cur.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'characters' 
    ORDER BY ordinal_position
""")

print("characters table columns:")
print("=" * 60)
for row in cur.fetchall():
    print(f"  {row[0]:30} {row[1]}")

cur.close()
conn.close()
