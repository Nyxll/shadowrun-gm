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
    SELECT source, modifier_type, target_name, modifier_value, modifier_data 
    FROM character_modifiers 
    WHERE source = 'Math SPU 4' AND parent_modifier_id IS NOT NULL
""")

print("Math SPU 4 child modifiers:")
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]}/{row[2]} = {row[3]}")
    print(f"    modifier_data: {row[4]}")

conn.close()
