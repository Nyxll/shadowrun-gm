#!/usr/bin/env python3
"""Check what modifiers were parsed for Manticore"""
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

# Get Manticore's ID
cur.execute("SELECT id FROM characters WHERE street_name = 'Manticore'")
char = cur.fetchone()

if not char:
    print("Manticore not found")
    exit(1)

char_id = char['id']

# Get all modifiers
cur.execute("""
    SELECT 
        source,
        source_type,
        modifier_type,
        target_name,
        modifier_value,
        parent_modifier_id
    FROM character_modifiers
    WHERE character_id = %s
    ORDER BY source, parent_modifier_id NULLS FIRST
""", (char_id,))

mods = cur.fetchall()

print("MANTICORE'S MODIFIERS:")
print("=" * 70)

current_parent = None
for mod in mods:
    if mod['parent_modifier_id'] is None and mod['modifier_type'] == 'augmentation':
        # Parent entry
        current_parent = mod['source']
        print(f"\n{mod['source']} ({mod['source_type']}):")
    elif mod['parent_modifier_id'] is not None:
        # Child entry
        print(f"  • {mod['modifier_type']}: {mod['target_name']} = {mod['modifier_value']}")
    else:
        # Standalone modifier
        print(f"\n{mod['source']} ({mod['source_type']}):")
        print(f"  • {mod['modifier_type']}: {mod['target_name']} = {mod['modifier_value']}")

print("\n" + "=" * 70)

conn.close()
