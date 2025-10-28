#!/usr/bin/env python3
"""
Check bioware body index costs in database
"""
import os
import json
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

print("="*70)
print("PLATINUM'S BIOWARE BODY INDEX COSTS")
print("="*70)

cur.execute("""
    SELECT source, body_index_cost, modifier_data
    FROM character_modifiers
    WHERE character_id = (SELECT id FROM characters WHERE street_name = 'Platinum')
    AND source_type = 'bioware'
    ORDER BY source
""")

for row in cur.fetchall():
    print(f"\n{row['source']}:")
    print(f"  body_index_cost column: {row['body_index_cost']}")
    print(f"  modifier_data: {json.dumps(row['modifier_data'], indent=4)}")

conn.close()
