#!/usr/bin/env python3
"""Check Manticore's cyberware names in database"""
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

# Get Manticore's cyberware
cur.execute("""
    SELECT source, essence_cost 
    FROM character_modifiers 
    WHERE character_id = (SELECT id FROM characters WHERE name = 'Edom Pentathor' LIMIT 1)
      AND source_type = 'cyberware'
      AND parent_modifier_id IS NULL
    ORDER BY source
""")

print("Manticore's cyberware in database:")
for row in cur.fetchall():
    print(f"  - {row[0]} ({row[1]} Essence)")

conn.close()
