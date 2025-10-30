#!/usr/bin/env python3
"""
Check if Platinum has bioware that requires body index
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

# Get Platinum's character ID
cur.execute("SELECT id, name, street_name FROM characters WHERE street_name = 'Platinum'")
char = cur.fetchone()

if not char:
    print("Platinum not found!")
    cur.close()
    conn.close()
    exit(1)

char_id = char[0]
print(f"Character: {char[2]} ({char[1]})")
print(f"ID: {char_id}")

# Check for bioware in character_modifiers
cur.execute("""
    SELECT 
        source,
        source_type,
        body_index_cost,
        modifier_data
    FROM character_modifiers
    WHERE character_id = %s 
    AND source_type = 'bioware'
""", (char_id,))

bioware = cur.fetchall()

print(f"\n{'='*80}")
print(f"BIOWARE FROM character_modifiers TABLE")
print(f"{'='*80}")

if bioware:
    for item in bioware:
        print(f"\nName: {item[0]}")
        print(f"Type: {item[1]}")
        print(f"Data: {item[2]}")
else:
    print("\nNo bioware found in character_modifiers")

print(f"\n{'='*80}")

cur.close()
conn.close()
