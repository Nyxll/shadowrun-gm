#!/usr/bin/env python3
"""Check Platinum's cyberware in database"""
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
    SELECT gear_name, notes 
    FROM character_gear 
    WHERE character_id = (SELECT id FROM characters WHERE name = 'Kent Jefferies')
    AND (gear_name ILIKE '%cyber%' OR gear_name ILIKE '%smart%')
    ORDER BY gear_name
""")

print("Platinum's Cyberware/Smartlink:")
print("=" * 70)
for row in cursor.fetchall():
    print(f"\nGear: {row['gear_name']}")
    print(f"Notes: {row['notes']}")

cursor.close()
conn.close()
