#!/usr/bin/env python3
"""
Fix orphaned Math SPU modifiers for Manticore
Links child modifiers to their parent Math SPU 4
"""
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

# Get Math SPU 4 parent ID
cur.execute("""
    SELECT id FROM character_modifiers
    WHERE character_id = %s 
      AND source = 'Math SPU 4'
      AND modifier_type = 'augmentation'
      AND source_type = 'cyberware'
""", (char_id,))

math_spu_row = cur.fetchone()
if not math_spu_row:
    print("Math SPU 4 not found!")
    cur.close()
    conn.close()
    exit(1)

math_spu_id = math_spu_row[0]
print(f"Math SPU 4 ID: {math_spu_id}\n")

# Find orphaned modifiers that should be children
cur.execute("""
    SELECT id, source, modifier_type, target_name, modifier_value
    FROM character_modifiers
    WHERE character_id = %s 
      AND parent_modifier_id IS NULL
      AND modifier_type = 'skill'
      AND source_type = 'unknown'
      AND (source LIKE '%%calculation%%' OR source LIKE '%%technical%%')
    ORDER BY source
""", (char_id,))

orphaned = cur.fetchall()

if not orphaned:
    print("No orphaned modifiers found!")
else:
    print(f"Found {len(orphaned)} orphaned modifiers to link:\n")
    
    for row in orphaned:
        mod_id = row[0]
        source = row[1]
        mod_type = row[2]
        target = row[3]
        value = row[4]
        
        print(f"  Linking: {source} ({mod_type}: {target} = {value})")
        
        # Update to link to Math SPU and fix source_type
        cur.execute("""
            UPDATE character_modifiers
            SET parent_modifier_id = %s,
                source_type = 'cyberware'
            WHERE id = %s
        """, (math_spu_id, mod_id))
    
    conn.commit()
    print(f"\n✓ Successfully linked {len(orphaned)} modifiers to Math SPU 4")

# Verify the fix
cur.execute("""
    SELECT 
        parent.source as parent_name,
        child.source as child_name,
        child.modifier_type,
        child.target_name,
        child.modifier_value
    FROM character_modifiers parent
    LEFT JOIN character_modifiers child ON child.parent_modifier_id = parent.id
    WHERE parent.id = %s
    ORDER BY child.source
""", (math_spu_id,))

print("\nVerification - Math SPU 4 with children:")
for row in cur.fetchall():
    if row[1]:  # Has child
        print(f"  └─ {row[1]}: {row[2]} {row[3]} = {row[4]}")
    else:
        print(f"  {row[0]} (parent)")

cur.close()
conn.close()
