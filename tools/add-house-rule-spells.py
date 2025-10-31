#!/usr/bin/env python3
"""
Add house rule spells to master_spells and link to character_spells
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

print("=" * 70)
print("STEP 1: Fix Physical Barrier -> Personal Barrier")
print("=" * 70)

# Update character_spells
cur.execute("""
    UPDATE character_spells
    SET spell_name = 'Personal Barrier'
    WHERE spell_name = 'Physical Barrier'
    RETURNING id, character_id
""")
updated = cur.fetchall()
print(f"✓ Updated {len(updated)} character spell(s)")

# Now link to master_spells
cur.execute("""
    UPDATE character_spells
    SET master_spell_id = (
        SELECT id FROM master_spells WHERE spell_name = 'Personal Barrier'
    )
    WHERE spell_name = 'Personal Barrier'
    AND master_spell_id IS NULL
""")
print(f"✓ Linked to master_spells")

print("\n" + "=" * 70)
print("STEP 2: Add House Rule Spells")
print("=" * 70)

# Add Stop Regeneration (house rule)
cur.execute("""
    INSERT INTO master_spells (
        spell_name, spell_class, spell_type, duration, drain_formula,
        is_house_rule, description
    ) VALUES (
        'Stop Regeneration',
        'Health',
        'mana',
        'sustained',
        '[(F/2)+1]M',
        TRUE,
        'House rule spell that stops magical regeneration powers. Must be sustained to prevent regeneration.'
    )
    ON CONFLICT (spell_name) DO NOTHING
    RETURNING id
""")
result = cur.fetchone()
if result:
    print(f"✓ Added 'Stop Regeneration' (house rule)")
    stop_regen_id = result[0]
else:
    cur.execute("SELECT id FROM master_spells WHERE spell_name = 'Stop Regeneration'")
    stop_regen_id = cur.fetchone()[0]
    print(f"✓ 'Stop Regeneration' already exists")

# Add Recharge (house rule)
cur.execute("""
    INSERT INTO master_spells (
        spell_name, spell_class, spell_type, duration, drain_formula,
        is_house_rule, description
    ) VALUES (
        'Recharge',
        'Manipulation',
        'physical',
        'sustained',
        '[(F/2)+1]M',
        TRUE,
        'House rule spell that safely recharges electronic devices. Similar to Spark but sustained for 1 minute to become permanent. Drain similar to Spark.'
    )
    ON CONFLICT (spell_name) DO NOTHING
    RETURNING id
""")
result = cur.fetchone()
if result:
    print(f"✓ Added 'Recharge' (house rule)")
    recharge_id = result[0]
else:
    cur.execute("SELECT id FROM master_spells WHERE spell_name = 'Recharge'")
    recharge_id = cur.fetchone()[0]
    print(f"✓ 'Recharge' already exists")

print("\n" + "=" * 70)
print("STEP 3: Link House Rule Spells to Character Spells")
print("=" * 70)

# Link Stop Regeneration
cur.execute("""
    UPDATE character_spells
    SET master_spell_id = %s
    WHERE spell_name = 'Stop Regeneration'
    AND master_spell_id IS NULL
    RETURNING id
""", (stop_regen_id,))
linked = cur.fetchall()
print(f"✓ Linked {len(linked)} 'Stop Regeneration' spell(s)")

# Link Recharge
cur.execute("""
    UPDATE character_spells
    SET master_spell_id = %s
    WHERE spell_name = 'Recharge'
    AND master_spell_id IS NULL
    RETURNING id
""", (recharge_id,))
linked = cur.fetchall()
print(f"✓ Linked {len(linked)} 'Recharge' spell(s)")

conn.commit()

print("\n" + "=" * 70)
print("VERIFICATION")
print("=" * 70)

# Check all character spells are now linked
cur.execute("""
    SELECT COUNT(*) 
    FROM character_spells 
    WHERE master_spell_id IS NULL
""")
unlinked = cur.fetchone()[0]
print(f"Unlinked character spells: {unlinked}")

# Show house rule spells
cur.execute("""
    SELECT spell_name, spell_class, drain_formula, description
    FROM master_spells
    WHERE is_house_rule = TRUE
    ORDER BY spell_name
""")
print(f"\nHouse Rule Spells:")
for row in cur.fetchall():
    print(f"  - {row[0]} ({row[1]}): {row[2]}")
    print(f"    {row[3]}")

cur.close()
conn.close()

print("\n" + "=" * 70)
print("COMPLETE")
print("=" * 70)
