#!/usr/bin/env python3
"""
Check what skill modifiers Platinum should have based on character file
"""
import os
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row

load_dotenv()

# Connect to database
conn = psycopg.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=os.getenv('POSTGRES_PORT'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    dbname=os.getenv('POSTGRES_DB'),
    row_factory=dict_row
)
cur = conn.cursor()

# Get Platinum's character ID
cur.execute("SELECT id, street_name FROM characters WHERE street_name = 'Platinum'")
char = cur.fetchone()

if not char:
    print("Platinum not found!")
    exit(1)

char_id = char['id']
print(f"Platinum ID: {char_id}")
print()

# Check current modifiers
print("Current modifiers in database:")
print("=" * 80)
cur.execute("""
    SELECT modifier_type, target_name, modifier_value, source, source_type
    FROM character_modifiers
    WHERE character_id = %s
    ORDER BY modifier_type, target_name
""", (char_id,))

for row in cur.fetchall():
    print(f"{row['modifier_type']:15} | {row['target_name']:20} | {row['modifier_value']:+3} | {row['source']:30} | {row['source_type']}")

print()
print("Expected skill modifiers from character file:")
print("=" * 80)
print("From Skills section explanations:")
print("  Gunnery: +1 Enhanced Articulation, +1 Project Aegis")
print("  Athletics: +1 Enhanced Articulation")
print("  Stealth: +1 Enhanced Articulation")
print("  Firearms: +1 Reflex Recorder, +1 Enhanced Articulation, -3 TN Smartlink 3")
print("  Whips: +1 Enhanced Articulation")
print("  Monowhip: +1 Enhanced Articulation")
print("  Demolitions: +2 Mnemonic Enhancer")
print("  Physical Sciences: +2 Mnemonic Enhancer")
print("  Magical Theory: +2 Mnemonic Enhancer")
print("  Military Theory: +2 Mnemonic Enhancer")
print("  English: +2 Mnemonic Enhancer")
print("  French: +2 Mnemonic Enhancer")
print("  Cooking: +2 Mnemonic Enhancer")

conn.close()
