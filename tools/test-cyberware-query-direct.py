#!/usr/bin/env python3
"""Test the exact query that get_character_cyberware uses"""
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

# Get Platinum's ID
cur.execute("SELECT id FROM characters WHERE street_name = 'Platinum'")
char_id = cur.fetchone()[0]

# Run the EXACT query from get_character_cyberware
sql = "SELECT * FROM character_modifiers WHERE character_id = %s AND source_type = 'cyberware' AND deleted_at IS NULL ORDER BY source"
cur.execute(sql, (char_id,))

cols = [d[0] for d in cur.description]
rows = cur.fetchall()

print(f"Query returned {len(rows)} rows")
print(f"\nColumns: {cols}\n")

if rows:
    print("First row:")
    row_dict = dict(zip(cols, rows[0]))
    for key, value in row_dict.items():
        print(f"  {key}: {value}")

cur.close()
conn.close()
