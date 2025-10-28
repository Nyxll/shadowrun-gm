#!/usr/bin/env python3
"""Debug the parent-child structure of modifiers"""
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
char_id = char['id']

# Get ALL cyberware modifiers to see the structure
cur.execute("""
    SELECT 
        id,
        source,
        source_type,
        modifier_type,
        target_name,
        modifier_value,
        parent_modifier_id,
        essence_cost
    FROM character_modifiers
    WHERE character_id = %s 
    AND source_type = 'cyberware'
    ORDER BY source, parent_modifier_id NULLS FIRST, id
""", (char_id,))

mods = cur.fetchall()

print("ALL CYBERWARE MODIFIERS (showing parent-child structure):")
print("=" * 80)
for mod in mods:
    parent_marker = "PARENT" if mod['parent_modifier_id'] is None else f"  CHILD (parent_id={mod['parent_modifier_id']})"
    print(f"{parent_marker} | ID={mod['id']} | {mod['source']}")
    print(f"  modifier_type={mod['modifier_type']}, target={mod['target_name']}, value={mod['modifier_value']}")
    print(f"  essence_cost={mod['essence_cost']}")
    print()

conn.close()
