#!/usr/bin/env python3
"""Check for combat pool modifiers in the database"""
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=os.getenv('POSTGRES_PORT'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    dbname=os.getenv('POSTGRES_DB')
)

cur = conn.cursor()

# Check for combat pool modifiers
cur.execute("""
    SELECT 
        cm.source,
        cm.modifier_type,
        cm.modifier_value,
        cm.target_name,
        cm.notes
    FROM character_modifiers cm
    JOIN characters c ON cm.character_id = c.id
    WHERE c.name = 'Platinum'
    AND (
        cm.target_name ILIKE '%combat%pool%'
        OR cm.source ILIKE '%combat%pool%'
        OR cm.notes ILIKE '%combat%pool%'
    )
    ORDER BY cm.source
""")

print("Combat Pool Modifiers for Platinum:")
print("="*70)
rows = cur.fetchall()
if rows:
    for row in rows:
        print(f"\n{row[0]}:")
        print(f"  Type: {row[1]}")
        print(f"  Value: {row[2]}")
        print(f"  Target: {row[3]}")
        print(f"  Notes: {row[4]}")
else:
    print("No combat pool modifiers found!")

# Check base combat pool in characters table
cur.execute("""
    SELECT combat_pool, quickness
    FROM characters
    WHERE name = 'Platinum'
""")
row = cur.fetchone()
print(f"\n{'='*70}")
print(f"Base Combat Pool in DB: {row[0]}")
print(f"Quickness: {row[1]}")
print(f"Quickness/2: {row[1] // 2}")

conn.close()
