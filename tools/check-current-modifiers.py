#!/usr/bin/env python3
"""Check current modifiers for Platinum and Oak"""
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
cursor = conn.cursor()

cursor.execute("""
    SELECT c.street_name, cm.source, cm.modifier_type, cm.target_name, cm.modifier_value, cm.source_type
    FROM character_modifiers cm
    JOIN characters c ON cm.character_id = c.id
    WHERE c.street_name IN ('Platinum', 'Oak')
    ORDER BY c.street_name, cm.source
""")

print('\nCurrent Modifiers:')
print('='*100)
for r in cursor.fetchall():
    print(f"{r['street_name']:12s} | {r['source']:45s} | {r['source_type']:10s} | {r['modifier_type']:15s} | {r['target_name']:15s} | {r['modifier_value']:+3d}")

conn.close()
