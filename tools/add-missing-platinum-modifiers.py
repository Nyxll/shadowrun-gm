#!/usr/bin/env python3
"""Add missing modifiers for Platinum's cyberware"""
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
cursor = conn.cursor()

# Get Platinum's character ID
cursor.execute("SELECT id FROM characters WHERE name = 'Kent Jefferies'")
char = cursor.fetchone()
char_id = char[0]

print(f"Adding missing modifiers for Platinum (ID: {char_id})")

# Add Wired Reflexes +3D6 Initiative
cursor.execute("""
    SELECT id FROM character_modifiers 
    WHERE character_id = %s 
      AND source = 'Wired Reflexes 3 (Beta-Grade)' 
      AND modifier_type = 'augmentation'
""", (char_id,))
parent = cursor.fetchone()
if parent:
    parent_id = parent[0]
    cursor.execute("""
        INSERT INTO character_modifiers (
            character_id, modifier_type, target_name, modifier_value,
            source, source_type, is_permanent, parent_modifier_id
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (char_id, 'initiative', 'initiative_dice', 3,
          'Wired Reflexes 3 (Beta-Grade)', 'cyberware', True, parent_id))
    print("✓ Added Wired Reflexes +3D6 Initiative")

# Add Smartlink 2 AEGIS -3 TN
cursor.execute("""
    SELECT id FROM character_modifiers 
    WHERE character_id = %s 
      AND source = 'Smartlink 2 AEGIS' 
      AND modifier_type = 'augmentation'
""", (char_id,))
parent = cursor.fetchone()
if parent:
    parent_id = parent[0]
    cursor.execute("""
        INSERT INTO character_modifiers (
            character_id, modifier_type, target_name, modifier_value,
            source, source_type, is_permanent, parent_modifier_id
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (char_id, 'combat', 'ranged_tn', -3,
          'Smartlink 2 AEGIS', 'cyberware', True, parent_id))
    print("✓ Added Smartlink 2 AEGIS -3 TN")

conn.commit()
cursor.close()
conn.close()

print("\n✓ Missing modifiers added!")
