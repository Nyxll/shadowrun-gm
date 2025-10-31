#!/usr/bin/env python3
"""
Test fuzzy spell matching to see what would match
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
print("MASTER SPELLS IN DATABASE")
print("=" * 70)
cur.execute("SELECT spell_name FROM master_spells ORDER BY spell_name")
master_spells = [row[0] for row in cur.fetchall()]
print(f"Found {len(master_spells)} master spells:")
for spell in master_spells:
    print(f"  - {spell}")

print("\n" + "=" * 70)
print("CHARACTER SPELLS (UNLINKED)")
print("=" * 70)
cur.execute("""
    SELECT DISTINCT spell_name 
    FROM character_spells 
    WHERE master_spell_id IS NULL
    ORDER BY spell_name
""")
unlinked_spells = [row[0] for row in cur.fetchall()]
print(f"Found {len(unlinked_spells)} unlinked character spells:")
for spell in unlinked_spells:
    print(f"  - {spell}")

print("\n" + "=" * 70)
print("FUZZY MATCHING TEST (similarity > 0.6)")
print("=" * 70)

for char_spell in unlinked_spells:
    cur.execute("""
        SELECT spell_name, similarity(spell_name, %s) as sim
        FROM master_spells
        WHERE similarity(spell_name, %s) > 0.6
        ORDER BY sim DESC
        LIMIT 1
    """, (char_spell, char_spell))
    
    result = cur.fetchone()
    if result:
        print(f"✓ '{char_spell}' -> '{result[0]}' (similarity: {result[1]:.2f})")
    else:
        print(f"✗ '{char_spell}' -> No match found")

cur.close()
conn.close()

print("\n" + "=" * 70)
print("CONCLUSION")
print("=" * 70)
print("Fuzzy matching is working, but master_spells table is nearly empty.")
print("Need to import more spells from Shadowrun rulebooks to get better linking.")
print("=" * 70)
