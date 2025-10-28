#!/usr/bin/env python3
import os
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row

load_dotenv()

conn = psycopg.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=os.getenv('POSTGRES_PORT'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    dbname=os.getenv('POSTGRES_DB'),
    row_factory=dict_row
)

cur = conn.cursor()
cur.execute("""
    SELECT gear_type, COUNT(*) as count
    FROM character_gear 
    WHERE character_id = (SELECT id FROM characters WHERE name = 'Kent Jefferies')
    GROUP BY gear_type
""")

rows = cur.fetchall()
print('Gear by type:')
for r in rows:
    print(f'  {r["gear_type"]}: {r["count"]}')

# Show some examples
cur.execute("""
    SELECT gear_name, gear_type
    FROM character_gear 
    WHERE character_id = (SELECT id FROM characters WHERE name = 'Kent Jefferies')
    LIMIT 15
""")
print('\nFirst 15 items:')
for r in cur.fetchall():
    print(f'  {r["gear_type"]}: {r["gear_name"]}')

conn.close()
