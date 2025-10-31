#!/usr/bin/env python3
"""Check Platinum's Firearms skill and cyberware bonuses"""
import os
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row

load_dotenv()

conn = psycopg.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=int(os.getenv('POSTGRES_PORT')),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    dbname=os.getenv('POSTGRES_DB')
)

with conn.cursor(row_factory=dict_row) as cur:
    # Get Platinum
    cur.execute("SELECT id, street_name FROM characters WHERE street_name = 'Platinum'")
    char = cur.fetchone()
    print(f"Character: {char['street_name']} ({char['id']})")
    
    # Get Firearms skill
    cur.execute("""
        SELECT skill_name, base_rating, current_rating, specialization
        FROM character_skills
        WHERE character_id = %s AND skill_name ILIKE '%%firearm%%'
    """, (char['id'],))
    
    skills = cur.fetchall()
    print(f"\nFirearms Skills:")
    for skill in skills:
        print(f"  {skill['skill_name']}: base={skill['base_rating']}, current={skill['current_rating']}, spec={skill.get('specialization')}")
    
    # Get cyberware that affects Firearms
    cur.execute("""
        SELECT source, target_name, modifier_value, modifier_data
        FROM character_modifiers
        WHERE character_id = %s 
        AND source_type = 'cyberware'
        AND (target_name ILIKE '%%firearm%%' OR source ILIKE '%%firearm%%')
    """, (char['id'],))
    
    cyber = cur.fetchall()
    print(f"\nFirearms Cyberware:")
    for c in cyber:
        print(f"  {c['source']}: target={c['target_name']}, value={c['modifier_value']}")
    
    # Get ALL cyberware to see what's there
    cur.execute("""
        SELECT source, target_name, modifier_value, modifier_data
        FROM character_modifiers
        WHERE character_id = %s 
        AND source_type = 'cyberware'
        ORDER BY source
    """, (char['id'],))
    
    all_cyber = cur.fetchall()
    print(f"\nALL Cyberware:")
    for c in all_cyber:
        data_str = str(c['modifier_data'])[:100] if c['modifier_data'] else 'None'
        print(f"  {c['source']}: target={c['target_name']}, value={c['modifier_value']}, data={data_str}")

conn.close()
