#!/usr/bin/env python3
"""Verify character imports with full details"""

import psycopg2
import json
from dotenv import load_dotenv
import os

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=os.getenv('POSTGRES_PORT'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    database=os.getenv('POSTGRES_DB')
)

cur = conn.cursor()
cur.execute("""
    SELECT name, street_name, character_type, archetype, 
           nuyen, karma_pool, karma_total,
           attributes, skills, notes
    FROM characters 
    ORDER BY name
""")

print("✅ Characters Successfully Imported:")
print("="*80)

for row in cur.fetchall():
    name, street_name, char_type, archetype, nuyen, karma_pool, karma_total, attributes, skills, notes = row
    
    print(f"\n{name} \"{street_name}\"")
    print(f"  Type: {char_type}")
    print(f"  Archetype: {archetype}")
    print(f"  Nuyen: {nuyen:,}¥")
    print(f"  Karma Pool: {karma_pool}")
    print(f"  Total Karma: {karma_total}")
    
    # Show attributes
    if attributes:
        attrs = json.loads(attributes) if isinstance(attributes, str) else attributes
        print(f"  Attributes: {len(attrs)} - " + ", ".join([f"{k.title()}: {v}" for k, v in sorted(attrs.items())]))
    
    # Show skills count
    if skills:
        skills_list = json.loads(skills) if isinstance(skills, str) else skills
        print(f"  Skills: {len(skills_list)} total")
    
    # Show magic info if present
    if notes:
        notes_data = json.loads(notes) if isinstance(notes, str) else notes
        if notes_data.get('magic_pool'):
            print(f"  Magic Pool: {notes_data['magic_pool']}")
        if notes_data.get('initiate_level'):
            print(f"  Initiate Level: {notes_data['initiate_level']}")
        if notes_data.get('metamagics'):
            print(f"  Metamagics: {', '.join(notes_data['metamagics'])}")
        if notes_data.get('spells'):
            print(f"  Spells: {len(notes_data['spells'])} known")
        if notes_data.get('adept_powers'):
            print(f"  Adept Powers: {len(notes_data['adept_powers'])}")

cur.execute("SELECT COUNT(*) FROM characters")
count = cur.fetchone()[0]

print("\n" + "="*80)
print(f"Total: {count} characters imported with comprehensive data")
print("="*80)
