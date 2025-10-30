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
result = cur.fetchone()
if not result:
    print("Platinum not found!")
    exit(1)
    
char_id = result[0]
print(f"Platinum's ID: {char_id}\n")

# Check modifiers with source_type
cur.execute("""
    SELECT source, source_type, modifier_type, COUNT(*)
    FROM character_modifiers 
    WHERE character_id = %s 
    AND deleted_at IS NULL
    GROUP BY source, source_type, modifier_type
    ORDER BY source
    LIMIT 20
""", (char_id,))

print("Platinum's modifiers grouped:")
print("SOURCE | SOURCE_TYPE | MODIFIER_TYPE | COUNT")
print("-" * 60)
for row in cur.fetchall():
    print(f"{row[0][:30]:30} | {str(row[1])[:15]:15} | {row[2][:15]:15} | {row[3]}")

cur.close()
conn.close()
