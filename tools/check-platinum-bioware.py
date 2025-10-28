#!/usr/bin/env python3
"""Check Platinum's bioware modifiers for duplicates"""
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

# Get Platinum's bioware modifiers
cur.execute("""
    SELECT source, modifier_type, target_name, modifier_value, parent_modifier_id
    FROM character_modifiers 
    WHERE character_id = (SELECT id FROM characters WHERE name = 'Kent Jefferies')
    AND source_type = 'bioware'
    ORDER BY source, parent_modifier_id NULLS FIRST, modifier_type, target_name
""")

rows = cur.fetchall()

print(f"Platinum's Bioware Modifiers ({len(rows)} total):")
print()

current_source = None
for r in rows:
    if r['source'] != current_source:
        current_source = r['source']
        print(f"\n{current_source}:")
    
    indent = "  " if r['parent_modifier_id'] else ""
    parent_marker = "(parent)" if not r['parent_modifier_id'] else "(child)"
    print(f"  {indent}{parent_marker} {r['modifier_type']} -> {r['target_name']} = {r['modifier_value']}")

# Check for duplicates
print("\n" + "="*70)
print("Checking for duplicates...")

cur.execute("""
    SELECT source, modifier_type, target_name, COUNT(*) as count
    FROM character_modifiers 
    WHERE character_id = (SELECT id FROM characters WHERE name = 'Kent Jefferies')
    AND source_type = 'bioware'
    AND parent_modifier_id IS NOT NULL  -- Only check child modifiers
    GROUP BY source, modifier_type, target_name
    HAVING COUNT(*) > 1
""")

duplicates = cur.fetchall()

if duplicates:
    print(f"Found {len(duplicates)} duplicate modifier combinations:")
    for d in duplicates:
        print(f"  {d['source']}: {d['modifier_type']} -> {d['target_name']} ({d['count']} times)")
else:
    print("✓ No duplicates found!")

conn.close()
