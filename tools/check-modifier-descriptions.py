#!/usr/bin/env python3
"""Check if modifier descriptions are stored in modifier_data"""
import os
import json
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=os.getenv('POSTGRES_PORT'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    dbname=os.getenv('POSTGRES_DB')
)

cur = conn.cursor(cursor_factory=RealDictCursor)

# Get Manticore's child modifiers
cur.execute("""
    SELECT 
        source,
        modifier_type,
        target_name,
        modifier_value,
        modifier_data
    FROM character_modifiers
    WHERE character_id = (SELECT id FROM characters WHERE name='Edom Pentathor' LIMIT 1)
      AND source_type='cyberware'
      AND parent_modifier_id IS NOT NULL
    ORDER BY source
""")

rows = cur.fetchall()

print("MANTICORE CHILD MODIFIERS:")
print("="*80)
for row in rows:
    print(f"\n{row['source']}:")
    print(f"  Type: {row['modifier_type']}")
    print(f"  Target: {row['target_name']}")
    print(f"  Value: {row['modifier_value']}")
    print(f"  Data: {json.dumps(row['modifier_data'], indent=4) if row['modifier_data'] else 'None'}")

cur.close()
conn.close()
