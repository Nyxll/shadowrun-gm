#!/usr/bin/env python3
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv
import os

load_dotenv()

conn = psycopg.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=int(os.getenv('POSTGRES_PORT')),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    dbname=os.getenv('POSTGRES_DB'),
    row_factory=dict_row
)

cur = conn.cursor()
cur.execute("""
    SELECT gear_name, gear_type
    FROM character_gear 
    WHERE character_id IN (
        SELECT id FROM characters 
        WHERE LOWER(COALESCE(street_name, '')) = 'manticore'
    )
    ORDER BY gear_type, gear_name
""")

results = cur.fetchall()
print(f"Manticore's gear ({len(results)} items):")
for r in results:
    print(f"  [{r['gear_type']}] {r['gear_name']}")

conn.close()
