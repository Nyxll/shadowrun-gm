#!/usr/bin/env python3
"""Check database schema for characters table"""
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
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'characters' 
    ORDER BY ordinal_position
""")

print("Characters table schema:")
print("-" * 50)
for row in cur.fetchall():
    print(f"{row[0]}: {row[1]}")

conn.close()
