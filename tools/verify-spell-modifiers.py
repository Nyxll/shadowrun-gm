#!/usr/bin/env python3
"""
Verify spell modifiers for Block and Oak
"""
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

# Check Block
print("\n" + "=" * 80)
print("BLOCK (Mok' TuBing) - Spell Lock Modifiers")
print("=" * 80)
cursor.execute("""
    SELECT cm.modifier_type, cm.target_name, cm.modifier_value, cm.source, cm.source_type
    FROM character_modifiers cm
    JOIN characters c ON cm.character_id = c.id
    WHERE c.street_name = 'Block'
    ORDER BY cm.source
""")
for mod in cursor.fetchall():
    print(f"{mod['source']:40s} | {mod['source_type']:10s} | {mod['modifier_type']:15s} | {mod['target_name']:20s} | {mod['modifier_value']:+3d}")

# Check Oak
print("\n" + "=" * 80)
print("OAK (Simon Stalman) - Quickened Spell Modifiers")
print("=" * 80)
cursor.execute("""
    SELECT cm.modifier_type, cm.target_name, cm.modifier_value, cm.source, cm.source_type
    FROM character_modifiers cm
    JOIN characters c ON cm.character_id = c.id
    WHERE c.street_name = 'Oak'
    ORDER BY cm.source
""")
for mod in cursor.fetchall():
    print(f"{mod['source']:40s} | {mod['source_type']:10s} | {mod['modifier_type']:15s} | {mod['target_name']:20s} | {mod['modifier_value']:+3d}")

print("\n" + "=" * 80)

conn.close()
