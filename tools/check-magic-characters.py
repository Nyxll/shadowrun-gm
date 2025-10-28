#!/usr/bin/env python3
"""Check which characters have magic rating"""
import os
import sys
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', '127.0.0.1'),
    'port': int(os.getenv('POSTGRES_PORT', '5434')),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'dbname': os.getenv('POSTGRES_DB', 'postgres')
}

conn = psycopg.connect(**DB_CONFIG, row_factory=dict_row)
cursor = conn.cursor()

# First show magic characters
cursor.execute("""
    SELECT name, current_magic, totem
    FROM characters
    WHERE current_magic > 0
    ORDER BY name
""")

results = cursor.fetchall()

print("\nCharacters with Magic Rating:")
print("=" * 50)
for char in results:
    print(f"{char['name']}: Magic {char['current_magic']}, Totem: {char.get('totem', 'None')}")

# Now show Simon Stalman's spells
print("\n" + "=" * 80)
print("Simon Stalman's Spells:")
print("=" * 80)

cursor.execute("""
    SELECT spell_name, learned_force, spell_category
    FROM character_spells cs
    JOIN characters c ON c.id = cs.character_id
    WHERE LOWER(c.name) = 'simon stalman'
    ORDER BY spell_category, spell_name
""")

spells = cursor.fetchall()

if spells:
    for spell in spells:
        print(f"{spell['spell_name']:30} Force {spell['learned_force']:2}  ({spell['spell_category']})")
else:
    print("No spells found!")

# Check for Levitate spells
print("\n" + "=" * 80)
print("All Levitate spells in database:")
print("=" * 80)

cursor.execute("""
    SELECT c.name, cs.spell_name, cs.learned_force
    FROM character_spells cs
    JOIN characters c ON c.id = cs.character_id
    WHERE LOWER(cs.spell_name) LIKE '%levitate%'
    ORDER BY c.name
""")

levitate_spells = cursor.fetchall()

if levitate_spells:
    for spell in levitate_spells:
        print(f"{spell['name']:20} {spell['spell_name']:25} Force {spell['learned_force']}")
else:
    print("No Levitate spells found!")

cursor.close()
conn.close()
