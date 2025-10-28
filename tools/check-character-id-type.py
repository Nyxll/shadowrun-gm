#!/usr/bin/env python3
"""
Check the data type of character ID and list all characters with their UUIDs
"""
import os
from dotenv import load_dotenv
import psycopg

load_dotenv()

conn = psycopg.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=os.getenv('POSTGRES_PORT'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    dbname=os.getenv('POSTGRES_DB')
)

cur = conn.cursor()

# Check ID column type
cur.execute("""
    SELECT column_name, data_type, character_maximum_length
    FROM information_schema.columns 
    WHERE table_name = 'characters' AND column_name = 'id'
""")
print("Character ID Column Type:")
print("=" * 60)
result = cur.fetchone()
if result:
    print(f"Column: {result[0]}")
    print(f"Type: {result[1]}")
    if result[2]:
        print(f"Max Length: {result[2]}")
else:
    print("ID column not found!")

# List all characters with their IDs
print("\n" + "=" * 60)
print("All Characters with UUIDs:")
print("=" * 60)
cur.execute("SELECT id, name FROM characters ORDER BY name")
for row in cur.fetchall():
    print(f"{row[1]:30} UUID: {row[0]}")

cur.close()
conn.close()
