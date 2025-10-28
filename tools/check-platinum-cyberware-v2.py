#!/usr/bin/env python3
import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

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

# Get Platinum's cyberware
# Get all gear with smartlink
cursor.execute("""
    SELECT gear_name, gear_type, notes 
    FROM character_gear 
    WHERE character_id = (
        SELECT id FROM characters 
        WHERE LOWER(name) = 'kent jefferies' OR LOWER(street_name) = 'platinum'
    ) 
    AND LOWER(gear_name) LIKE '%%smartlink%%'
    ORDER BY gear_name
""")

print("Platinum's Smartlink Gear:")
print("=" * 70)
smartlink_rows = cursor.fetchall()
if smartlink_rows:
    for row in smartlink_rows:
        print(f"\nGear: {row['gear_name']}")
        print(f"Type: {row['gear_type']}")
        if row['notes']:
            print(f"Notes: {row['notes'][:200]}")
        else:
            print("Notes: (none)")
else:
    print("No smartlink gear found!")

print("\n")
print("=" * 70)
print("Checking all cyberware for 'smartlink' in notes:")
print("=" * 70)

cursor.execute("""
    SELECT gear_name, gear_type, notes 
    FROM character_gear 
    WHERE character_id = (
        SELECT id FROM characters 
        WHERE LOWER(name) = 'kent jefferies' OR LOWER(street_name) = 'platinum'
    ) 
    AND gear_type = 'cyberware'
    ORDER BY gear_name
""")

for row in cursor.fetchall():
    notes_lower = (row['notes'] or '').lower()
    if 'smartlink' in notes_lower or 'smart' in notes_lower:
        print(f"\nGear: {row['gear_name']}")
        print(f"Type: {row['gear_type']}")
        print(f"Notes: {row['notes'][:200]}")

cursor.close()
conn.close()
