#!/usr/bin/env python3
"""Check Math SPU modifiers in database"""
import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

conn = psycopg.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=os.getenv('POSTGRES_PORT'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    dbname=os.getenv('POSTGRES_DB')
)

cur = conn.cursor()

# Get Manticore's ID
cur.execute("SELECT id, name FROM characters WHERE LOWER(name) LIKE LOWER('%manticore%') OR LOWER(street_name) LIKE LOWER('%manticore%')")
result = cur.fetchone()
if not result:
    print("Manticore not found!")
    cur.close()
    conn.close()
    exit(1)

char_id = result[0]
print(f"Found character: {result[1]} (ID: {char_id})\n")

# Get all Math SPU related modifiers
cur.execute("""
    SELECT id, source, source_type, modifier_type, target_name, modifier_value, parent_modifier_id
    FROM character_modifiers
    WHERE character_id = %s 
      AND (source LIKE '%%Math%%' OR source LIKE '%%SPU%%')
    ORDER BY source, id
""", (char_id,))

print("Math SPU modifiers:")
math_spu_id = None
for row in cur.fetchall():
    print(f"  ID: {row[0]}")
    print(f"    Source: {row[1]}")
    print(f"    Type: {row[2]}/{row[3]}")
    print(f"    Target: {row[4]} = {row[5]}")
    print(f"    Parent ID: {row[6]}")
    print()
    if row[1] == "Math SPU 4" and row[3] == "augmentation":
        math_spu_id = row[0]

# Now check for orphaned modifiers that should be children
print("\nChecking for orphaned modifiers that might belong to Math SPU:")
cur.execute("""
    SELECT id, source, source_type, modifier_type, target_name, modifier_value, parent_modifier_id
    FROM character_modifiers
    WHERE character_id = %s 
      AND parent_modifier_id IS NULL
      AND modifier_type != 'augmentation'
      AND (source LIKE '%%calculation%%' OR source LIKE '%%technical%%' OR source LIKE '%%computer%%')
    ORDER BY source
""", (char_id,))

for row in cur.fetchall():
    print(f"  ID: {row[0]}")
    print(f"    Source: {row[1]}")
    print(f"    Type: {row[2]}/{row[3]}")
    print(f"    Target: {row[4]} = {row[5]}")
    print(f"    Parent ID: {row[6]} (SHOULD BE: {math_spu_id})")
    print()

cur.close()
conn.close()
