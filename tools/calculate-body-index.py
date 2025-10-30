#!/usr/bin/env python3
"""
Calculate and update body index for all characters with bioware.

In Shadowrun 2E, Body Index tracks bioware implantation.
Body Index Max = (Body + Willpower) / 2
Body Index Current = Sum of all bioware body_index_cost values
"""
import os
from dotenv import load_dotenv
import psycopg2
from decimal import Decimal

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=os.getenv('POSTGRES_PORT'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    dbname=os.getenv('POSTGRES_DB')
)

cur = conn.cursor()

# Get all characters
cur.execute("""
    SELECT 
        id, 
        name, 
        street_name,
        base_body,
        base_willpower
    FROM characters
""")

characters = cur.fetchall()

print("=" * 80)
print("CALCULATING BODY INDEX FOR ALL CHARACTERS")
print("=" * 80)

for char in characters:
    char_id, name, street_name, base_body, base_willpower = char
    display_name = street_name or name
    
    # Calculate Body Index Max = (Body + Willpower) / 2
    body_index_max = Decimal(base_body + base_willpower) / Decimal(2)
    
    # Get sum of bioware body_index_cost
    cur.execute("""
        SELECT COALESCE(SUM(body_index_cost), 0)
        FROM character_modifiers
        WHERE character_id = %s
        AND source_type = 'bioware'
        AND body_index_cost IS NOT NULL
    """, (char_id,))
    
    body_index_current = cur.fetchone()[0] or Decimal(0)
    
    # Only update if character has bioware OR if body_index fields are NULL
    if body_index_current > 0 or body_index_max > 0:
        print(f"\n{display_name}:")
        print(f"  Body Index Max: {body_index_max} (Body {base_body} + Will {base_willpower}) / 2")
        print(f"  Body Index Current: {body_index_current}")
        
        # Update character
        cur.execute("""
            UPDATE characters
            SET body_index_max = %s,
                body_index_current = %s
            WHERE id = %s
        """, (body_index_max, body_index_current, char_id))

conn.commit()
print(f"\n{'='*80}")
print("Body index calculation complete!")
print(f"{'='*80}")

cur.close()
conn.close()
