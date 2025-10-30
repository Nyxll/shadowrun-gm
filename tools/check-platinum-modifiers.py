#!/usr/bin/env python3
"""Check Platinum's modifiers in database"""
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
print(f"Platinum's ID: {char_id}\n")

# Check modifiers
cur.execute("""
    SELECT source, source_type, modifier_type, target_name, modifier_value
    FROM character_modifiers 
    WHERE character_id = %s 
    AND deleted_at IS NULL
    ORDER BY source
    LIMIT 10
""", (char_id,))

print("Platinum's modifiers:")
for row in cur.fetchall():
    print(f"  {row[0]} | source_type={row[1]} | modifier_type={row[2]} | {row[3]} {row[4]:+d}")

cur.close()
conn.close()
