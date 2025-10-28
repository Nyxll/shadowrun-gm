#!/usr/bin/env python3
"""Check all character modifiers"""
import os
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row
import json

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

# Get all characters with their modifiers
cursor.execute("""
    SELECT 
        c.street_name,
        c.name as real_name,
        cm.source,
        cm.source_type,
        cm.modifier_type,
        cm.target_name,
        cm.modifier_value,
        cm.modifier_data,
        cm.is_homebrew
    FROM characters c
    LEFT JOIN character_modifiers cm ON cm.character_id = c.id
    ORDER BY c.street_name, cm.source
""")

current_char = None
for row in cursor.fetchall():
    if row['street_name'] != current_char:
        current_char = row['street_name']
        print(f"\n{'='*100}")
        print(f"{row['street_name']} ({row['real_name']})")
        print('='*100)
    
    if row['source']:
        modifier_data_str = ""
        if row['modifier_data']:
            modifier_data_str = f" | DATA: {json.dumps(row['modifier_data'])}"
        
        homebrew = " [HOMEBREW]" if row['is_homebrew'] else ""
        print(f"  {row['source']:45s} | {row['source_type']:10s} | {row['modifier_type']:15s} | {row['target_name']:20s} | {row['modifier_value']:+3d}{homebrew}{modifier_data_str}")
    else:
        print("  (No modifiers)")

conn.close()
