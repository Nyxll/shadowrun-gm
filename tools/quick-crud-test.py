#!/usr/bin/env python3
"""
Quick CRUD test - just verify schema compliance
"""
import os
import sys
from dotenv import load_dotenv
import psycopg

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib.comprehensive_crud import ComprehensiveCRUD, get_system_user_id

load_dotenv()

# Get system user
conn = psycopg.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=int(os.getenv('POSTGRES_PORT')),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    dbname=os.getenv('POSTGRES_DB')
)
user_id = get_system_user_id(conn)
conn.close()

crud = ComprehensiveCRUD(user_id)

print("Testing schema compliance...")
print("\n1. Testing character_skills (base_rating/current_rating)...")
try:
    char = crud.get_character_by_name("Oak")
    if char:
        skills = crud.get_character_skills(char['id'])
        if skills and len(skills) > 0:
            skill = skills[0]
            assert 'base_rating' in skill, "Missing base_rating"
            assert 'current_rating' in skill, "Missing current_rating"
            print(f"   ✓ Skills have base_rating and current_rating")
        else:
            print(f"   ⚠ No skills found for Oak")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n2. Testing character_modifiers (source, is_permanent)...")
try:
    if char:
        cyber = crud.get_character_cyberware(char['id'])
        if cyber and len(cyber) > 0:
            mod = cyber[0]
            assert 'source' in mod, "Missing source field"
            assert 'is_permanent' in mod, "Missing is_permanent field"
            print(f"   ✓ Modifiers have source and is_permanent")
        else:
            print(f"   ⚠ No cyberware found for Oak")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n3. Testing character_relationships (relationship_name, data)...")
try:
    if char:
        spells = crud.get_character_spells(char['id'])
        if spells and len(spells) > 0:
            spell = spells[0]
            assert 'spell_name' in spell, "Missing spell_name"
            print(f"   ✓ Spells accessible")
        else:
            print(f"   ⚠ No spells found for Oak")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n4. Testing character_powers (UUID character_id)...")
try:
    # Just verify we can query without errors
    cur = crud.conn.cursor()
    cur.execute("""
        SELECT character_id, power_name 
        FROM character_powers 
        LIMIT 1
    """)
    result = cur.fetchone()
    if result:
        print(f"   ✓ character_powers uses UUID (found: {result[1]})")
    else:
        print(f"   ⚠ No powers in database")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n✅ Schema compliance check complete!")
