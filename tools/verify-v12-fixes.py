#!/usr/bin/env python3
"""
Verify all three fixes from v12 import
"""
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

print("=" * 70)
print("FIX 1: ESSENCE VALUES")
print("=" * 70)
cur.execute("""
    SELECT street_name, base_essence, essence_hole, current_essence
    FROM characters
    ORDER BY street_name
""")

for street_name, base, hole, current in cur.fetchall():
    print(f"{street_name:12} | base={base:4.2f} | hole={hole if hole else 0:4.2f} | current={current:4.2f}")

print("\n" + "=" * 70)
print("FIX 2: NOTES (first 100 chars)")
print("=" * 70)
cur.execute("""
    SELECT street_name, LEFT(notes, 100) as notes_preview
    FROM characters
    WHERE notes IS NOT NULL
    ORDER BY street_name
""")

for street_name, notes in cur.fetchall():
    print(f"{street_name:12} | {notes}...")

print("\n" + "=" * 70)
print("FIX 3: SPELL LINKING TO MASTER_SPELLS")
print("=" * 70)
cur.execute("""
    SELECT 
        c.street_name,
        cs.spell_name,
        cs.master_spell_id IS NOT NULL as is_linked
    FROM character_spells cs
    JOIN characters c ON c.id = cs.character_id
    ORDER BY c.street_name, cs.spell_name
""")

current_char = None
linked_count = 0
total_count = 0

for street_name, spell_name, is_linked in cur.fetchall():
    if current_char != street_name:
        if current_char:
            print(f"  Total: {linked_count}/{total_count} linked")
        current_char = street_name
        print(f"\n{street_name}:")
        linked_count = 0
        total_count = 0
    
    total_count += 1
    if is_linked:
        linked_count += 1
        print(f"  ✓ {spell_name}")
    else:
        print(f"  ✗ {spell_name} (not linked)")

if current_char:
    print(f"  Total: {linked_count}/{total_count} linked")

cur.close()
conn.close()

print("\n" + "=" * 70)
print("VERIFICATION COMPLETE")
print("=" * 70)
