#!/usr/bin/env python3
"""Test gear and contacts import"""
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

# Get Platinum's ID
cur.execute("SELECT id FROM characters WHERE street_name = %s ORDER BY created_at DESC LIMIT 1", ('Platinum',))
char_id = cur.fetchone()['id']

print("=" * 70)
print("PLATINUM'S GEAR")
print("=" * 70)

cur.execute("""
    SELECT gear_name, gear_type, modifications
    FROM character_gear
    WHERE character_id = %s
    ORDER BY gear_type, gear_name
""", (char_id,))

for gear in cur.fetchall():
    print(f"\n{gear['gear_name']} ({gear['gear_type']})")
    if gear['modifications']:
        print(f"  Modifications: {gear['modifications']}")

print("\n" + "=" * 70)
print("PLATINUM'S CONTACTS")
print("=" * 70)

cur.execute("""
    SELECT name, archetype, loyalty, connection
    FROM character_contacts
    WHERE character_id = %s
    ORDER BY name
""", (char_id,))

for contact in cur.fetchall():
    print(f"\n{contact['name']}")
    print(f"  Role: {contact['archetype']}")
    print(f"  Loyalty: {contact['loyalty']}, Connection: {contact['connection']}")

conn.close()
