#!/usr/bin/env python3
"""Test the v3 import to verify data"""
import os
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row

load_dotenv()

conn = psycopg.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=os.getenv('POSTGRES_PORT'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    dbname=os.getenv('POSTGRES_DB'),
    row_factory=dict_row
)
cur = conn.cursor()

# Check Platinum's attributes (get most recent)
cur.execute("""
    SELECT id, name, street_name,
           base_quickness, current_quickness,
           base_intelligence, current_intelligence,
           base_body, current_body,
           power_points_total, power_points_used, power_points_available
    FROM characters 
    WHERE street_name = %s
    ORDER BY created_at DESC
    LIMIT 1
""", ('Platinum',))

row = cur.fetchone()
if row:
    print("=" * 70)
    print(f"Character: {row['name']} ({row['street_name']})")
    print("=" * 70)
    print(f"\nAttributes (base -> current):")
    print(f"  Body: {row['base_body']} -> {row['current_body']}")
    print(f"  Quickness: {row['base_quickness']} -> {row['current_quickness']}")
    print(f"  Intelligence: {row['base_intelligence']} -> {row['current_intelligence']}")
    
    print(f"\nPower Points:")
    print(f"  Total: {row['power_points_total']}")
    print(f"  Used: {row['power_points_used']}")
    print(f"  Available: {row['power_points_available']}")
    
    # Get attribute modifiers
    char_id = row['id']
    cur.execute("""
        SELECT target_name, modifier_value, source, source_type
        FROM character_modifiers 
        WHERE character_id = %s
        AND modifier_type = 'attribute'
        ORDER BY target_name, modifier_value DESC
    """, (char_id,))
    
    print(f"\nAttribute Modifiers:")
    for mod in cur.fetchall():
        print(f"  {mod['target_name']}: +{mod['modifier_value']} from {mod['source']} ({mod['source_type']})")
    
    # Get skills
    cur.execute("""
        SELECT skill_name, base_rating, current_rating, skill_type
        FROM character_skills
        WHERE character_id = %s
        ORDER BY skill_type, skill_name
    """, (char_id,))
    
    print(f"\nSkills (base -> current):")
    current_type = None
    for skill in cur.fetchall():
        if skill['skill_type'] != current_type:
            current_type = skill['skill_type']
            print(f"\n  {current_type.title()} Skills:")
        print(f"    {skill['skill_name']}: {skill['base_rating']} -> {skill['current_rating']}")
    
    # Get skill modifiers
    cur.execute("""
        SELECT target_name, modifier_value, source, source_type, modifier_type
        FROM character_modifiers 
        WHERE character_id = %s
        AND modifier_type IN ('skill', 'combat')
        ORDER BY modifier_type, target_name
    """, (char_id,))
    
    print(f"\nSkill Modifiers:")
    for mod in cur.fetchall():
        print(f"  {mod['target_name']}: {mod['modifier_value']:+d} from {mod['source']} ({mod['source_type']}, {mod['modifier_type']})")

else:
    print("Platinum not found!")

conn.close()
