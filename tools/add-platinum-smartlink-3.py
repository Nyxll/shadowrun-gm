#!/usr/bin/env python3
"""
Add Platinum's Smartlink 3 (house rule: Smartlink 2 + Project AEGIS)
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

cursor = conn.cursor()

print("=" * 70)
print("ADDING PLATINUM'S SMARTLINK 3 (PROJECT AEGIS)")
print("=" * 70)

# Get Platinum's character ID (Kent Jefferies)
cursor.execute("SELECT id, name, street_name FROM characters WHERE name ILIKE '%kent%' OR street_name ILIKE '%platinum%'")
result = cursor.fetchone()

if not result:
    print("✗ Platinum (Kent Jefferies) character not found!")
    print("Available characters:")
    cursor.execute("SELECT name, street_name FROM characters LIMIT 10")
    for char in cursor.fetchall():
        print(f"  - {char[0]} ({char[1]})")
    cursor.close()
    conn.close()
    exit(1)

platinum_id = result[0]
print(f"✓ Found character: {result[1]} / {result[2]} (ID: {platinum_id})")

# First, add the house rule for Project AEGIS
print("\n1. Creating house rule for Project AEGIS...")
cursor.execute("""
    INSERT INTO house_rules (
        rule_name,
        rule_type,
        rule_config,
        description,
        is_active,
        created_by
    ) VALUES (
        'Project AEGIS Smartlink Enhancement',
        'custom',
        '{"base_item": "smartlink_2", "bonus_tn": -1, "essence_cost": 0, "availability": "unique_story_loot"}'::jsonb,
        'Project AEGIS software enhancement adds +1 to smartlink rating (total -3 TN). Provides all Smartlink 2 benefits plus additional targeting assistance.',
        true,
        'GM'
    )
    ON CONFLICT (campaign_id, rule_name) 
    WHERE campaign_id IS NULL
    DO UPDATE SET
        rule_config = EXCLUDED.rule_config,
        description = EXCLUDED.description
    RETURNING id
""")

house_rule_id = cursor.fetchone()[0]
print(f"✓ Created house rule (ID: {house_rule_id})")

# Check if Platinum already has a smartlink modifier
cursor.execute("""
    SELECT id, source, modifier_value 
    FROM character_modifiers 
    WHERE character_id = %s 
    AND source_type = 'cyberware'
    AND LOWER(source) LIKE '%%smartlink%%'
""", (platinum_id,))

existing = cursor.fetchone()

if existing:
    print(f"\n2. Updating existing smartlink modifier (ID: {existing[0]})...")
    print(f"   Old: {existing[1]} ({existing[2]:+d} TN)")
    
    cursor.execute("""
        UPDATE character_modifiers
        SET 
            source = 'Smartlink 2 + Project AEGIS',
            modifier_value = -3,
            source_type = 'cyberware',
            is_homebrew = true,
            house_rule_id = %s,
            modifier_data = '{
                "base_rating": 2,
                "aegis_enhancement": true,
                "aegis_bonus": -1,
                "essence_cost": 0.5,
                "special_abilities": {
                    "grenade_bonus": true,
                    "no_magnification_penalty": true,
                    "called_shot_bonus": true,
                    "tn_modifier": -3
                }
            }'::jsonb,
            notes = 'Smartlink 2 enhanced with Project AEGIS software for additional -1 TN (total -3)'
        WHERE id = %s
    """, (house_rule_id, existing[0]))
    
    print(f"   New: Smartlink 2 + Project AEGIS (-3 TN)")
    
else:
    print("\n2. Creating new smartlink modifier...")
    
    cursor.execute("""
        INSERT INTO character_modifiers (
            character_id,
            modifier_type,
            target_name,
            modifier_value,
            source,
            source_type,
            is_permanent,
            is_homebrew,
            house_rule_id,
            modifier_data,
            notes
        ) VALUES (
            %s,
            'combat',
            'ranged_tn',
            -3,
            'Smartlink 2 + Project AEGIS',
            'cyberware',
            true,
            true,
            %s,
            '{
                "base_rating": 2,
                "aegis_enhancement": true,
                "aegis_bonus": -1,
                "essence_cost": 0.5,
                "special_abilities": {
                    "grenade_bonus": true,
                    "no_magnification_penalty": true,
                    "called_shot_bonus": true,
                    "tn_modifier": -3
                }
            }'::jsonb,
            'Smartlink 2 enhanced with Project AEGIS software for additional -1 TN (total -3)'
        )
    """, (platinum_id, house_rule_id))
    
    print("✓ Created new smartlink modifier")

conn.commit()

print("\n" + "=" * 70)
print("SMARTLINK 3 CONFIGURATION COMPLETE")
print("=" * 70)

# Verify the configuration
cursor.execute("""
    SELECT 
        cm.source,
        cm.modifier_value,
        cm.source_type,
        cm.is_homebrew,
        cm.modifier_data,
        hr.rule_name
    FROM character_modifiers cm
    LEFT JOIN house_rules hr ON hr.id = cm.house_rule_id
    WHERE cm.character_id = %s
    AND cm.source_type = 'cyberware'
    AND LOWER(cm.source) LIKE '%%smartlink%%'
""", (platinum_id,))

result = cursor.fetchone()
if result:
    print(f"\nVerification:")
    print(f"  Source: {result[0]}")
    print(f"  TN Modifier: {result[1]:+d}")
    print(f"  Type: {result[2]}")
    print(f"  Homebrew: {result[3]}")
    print(f"  House Rule: {result[5]}")
    print(f"  Special Abilities:")
    for key, value in result[4].get('special_abilities', {}).items():
        print(f"    - {key}: {value}")

cursor.close()
conn.close()
