#!/usr/bin/env python3
import os
import psycopg
from dotenv import load_dotenv

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
    SELECT modifier_data 
    FROM character_modifiers 
    WHERE source = 'Math SPU 4' 
      AND parent_modifier_id IS NOT NULL 
      AND modifier_data IS NOT NULL
    LIMIT 1
""")

row = cur.fetchone()
if row:
    print(f"Type: {type(row[0])}")
    print(f"Value: {row[0]}")
    if isinstance(row[0], dict):
        print(f"Description: {row[0].get('description')}")
else:
    print("No rows found")

conn.close()
