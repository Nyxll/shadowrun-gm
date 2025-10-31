#!/usr/bin/env python3
"""
Link character_spells to master_spells using fuzzy matching
Uses similarity threshold of 0.5 and takes highest match
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

# Get all unlinked character spells
cur.execute("""
    SELECT id, spell_name, character_id
    FROM character_spells
    WHERE master_spell_id IS NULL
    ORDER BY spell_name
""")

unlinked_spells = cur.fetchall()
print(f"Found {len(unlinked_spells)} unlinked character spells")
print("=" * 70)

linked_count = 0
no_match_count = 0

for spell_id, spell_name, char_id in unlinked_spells:
    # Find best fuzzy match with threshold 0.5
    cur.execute("""
        SELECT id, spell_name, similarity(spell_name, %s) as sim
        FROM master_spells
        WHERE similarity(spell_name, %s) > 0.5
        ORDER BY sim DESC
        LIMIT 1
    """, (spell_name, spell_name))
    
    result = cur.fetchone()
    
    if result:
        master_id, master_name, similarity = result
        
        # Update the character spell
        cur.execute("""
            UPDATE character_spells
            SET master_spell_id = %s
            WHERE id = %s
        """, (master_id, spell_id))
        
        print(f"✓ '{spell_name}' -> '{master_name}' (similarity: {similarity:.3f})")
        linked_count += 1
    else:
        print(f"✗ '{spell_name}' -> No match found")
        no_match_count += 1

conn.commit()
cur.close()
conn.close()

print("=" * 70)
print(f"✓ Linked {linked_count} spells")
print(f"✗ No match for {no_match_count} spells")
print(f"Total: {linked_count + no_match_count} processed")
