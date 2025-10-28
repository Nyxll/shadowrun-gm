#!/usr/bin/env python3
"""
Verify character modifiers have been loaded
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

# Get Platinum's modifiers
cursor.execute("SELECT id, name FROM characters WHERE street_name = 'Platinum'")
char = cursor.fetchone()

if char:
    cursor.execute("""
        SELECT modifier_type, target_name, modifier_value, source, source_type 
        FROM character_modifiers 
        WHERE character_id = %s 
        ORDER BY source
    """, (char['id'],))
    mods = cursor.fetchall()
    
    print(f"\nModifiers for {char['name']}:")
    print("=" * 80)
    for m in mods:
        print(f"{m['source']:40s} | {m['modifier_type']:15s} | {m['target_name']:20s} | {m['modifier_value']:+3d}")
    print(f"\nTotal: {len(mods)} modifiers")
else:
    print("Platinum not found")

conn.close()
