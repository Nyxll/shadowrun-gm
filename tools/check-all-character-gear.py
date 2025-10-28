#!/usr/bin/env python3
"""Check gear counts for all characters"""
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

# Get all characters
cur.execute("SELECT id, name, street_name FROM characters ORDER BY name")
characters = cur.fetchall()

print("=" * 80)
print("GEAR COUNTS FOR ALL CHARACTERS")
print("=" * 80)

for char in characters:
    char_id = char['id']
    display_name = char['street_name'] or char['name']
    
    # Get gear counts by type
    cur.execute("""
        SELECT gear_type, COUNT(*) as count
        FROM character_gear
        WHERE character_id = %s
        GROUP BY gear_type
        ORDER BY gear_type
    """, (char_id,))
    
    gear_counts = cur.fetchall()
    
    print(f"\n{display_name} ({char['name']}):")
    
    total = 0
    for gc in gear_counts:
        print(f"  {gc['gear_type']}: {gc['count']}")
        total += gc['count']
    
    print(f"  TOTAL: {total}")
    
    # Show sample items
    cur.execute("""
        SELECT gear_type, gear_name
        FROM character_gear
        WHERE character_id = %s
        ORDER BY gear_type, gear_name
        LIMIT 5
    """, (char_id,))
    
    samples = cur.fetchall()
    if samples:
        print("  Sample items:")
        for s in samples:
            print(f"    - {s['gear_type']}: {s['gear_name']}")

print("\n" + "=" * 80)

conn.close()
