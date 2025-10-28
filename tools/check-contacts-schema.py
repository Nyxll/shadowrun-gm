#!/usr/bin/env python3
"""Check character_contacts table schema"""
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
    WHERE table_name = 'character_contacts' 
    ORDER BY ordinal_position
""")

print("Columns in character_contacts table:")
for row in cur.fetchall():
    print(f"  - {row[0]}: {row[1]}")

conn.close()
