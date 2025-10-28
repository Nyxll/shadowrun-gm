#!/usr/bin/env python3
"""Check cyberdeck data in database"""
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=os.getenv('POSTGRES_PORT'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    dbname=os.getenv('POSTGRES_DB'),
    cursor_factory=RealDictCursor
)

cur = conn.cursor()

# Check for cyberdeck tables
print("Tables with 'deck' in name:")
cur.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
      AND table_name LIKE '%deck%'
    ORDER BY table_name
""")
for row in cur.fetchall():
    print(f"  {row['table_name']}")

# Check Manticore's gear for cyberdecks
print("\nManticore's gear with 'deck' in name:")
cur.execute("""
    SELECT gear_name, gear_type, notes
    FROM character_gear
    WHERE character_id = (SELECT id FROM characters WHERE street_name = 'Manticore')
      AND LOWER(gear_name) LIKE '%deck%'
""")
for row in cur.fetchall():
    print(f"  {row['gear_name']}")
    print(f"    Type: {row['gear_type']}")
    if row['notes']:
        print(f"    Notes: {row['notes'][:100]}...")

# Check if there's a character_cyberdecks table
print("\nChecking for character_cyberdecks table:")
cur.execute("""
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'character_cyberdecks'
    )
""")
exists = cur.fetchone()['exists']
print(f"  character_cyberdecks table exists: {exists}")

if exists:
    cur.execute("SELECT * FROM character_cyberdecks WHERE character_id = (SELECT id FROM characters WHERE street_name = 'Manticore')")
    decks = cur.fetchall()
    print(f"\n  Found {len(decks)} cyberdeck(s) for Manticore:")
    for deck in decks:
        print(f"    {deck}")

conn.close()
