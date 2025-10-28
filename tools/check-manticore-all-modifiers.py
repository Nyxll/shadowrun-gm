#!/usr/bin/env python3
"""Check ALL modifiers for Manticore including orphans"""
import os
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

cursor = conn.cursor(cursor_factory=RealDictCursor)

# Get character ID
cursor.execute("SELECT id FROM characters WHERE name = 'Edom Pentathor'")
char = cursor.fetchone()
char_id = char['id']

print(f"Character ID: {char_id}")
print("\n" + "="*80)
print("ALL MODIFIERS (including orphans):")
print("="*80)

cursor.execute("""
    SELECT 
        id,
        source,
        source_type,
        modifier_type,
        target_name,
        modifier_value,
        essence_cost,
        parent_modifier_id,
        is_permanent
    FROM character_modifiers
    WHERE character_id = %s
    ORDER BY source_type, source, parent_modifier_id NULLS FIRST
""", (char_id,))

modifiers = cursor.fetchall()

print(f"\nTotal modifiers: {len(modifiers)}\n")

for mod in modifiers:
    parent_status = "PARENT" if mod['parent_modifier_id'] is None else f"child of {mod['parent_modifier_id']}"
    print(f"ID: {mod['id']} | {parent_status}")
    print(f"  Source: {mod['source']} ({mod['source_type']})")
    print(f"  Type: {mod['modifier_type']} -> {mod['target_name']}")
    print(f"  Value: {mod['modifier_value']}, Essence: {mod['essence_cost']}")
    print(f"  Permanent: {mod['is_permanent']}")
    print()

cursor.close()
conn.close()
