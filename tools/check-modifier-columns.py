#!/usr/bin/env python3
"""Check character_modifiers table columns"""
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=os.getenv('POSTGRES_PORT'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    dbname=os.getenv('POSTGRES_DB')
)

cur = conn.cursor()
cur.execute("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name = 'character_modifiers' 
    ORDER BY ordinal_position
""")

print("character_modifiers columns:")
for row in cur.fetchall():
    print(f"  - {row[0]}")

conn.close()
