#!/usr/bin/env python3
"""
Test sustained spell tracking using character_modifiers table
"""
import os
import sys
from dotenv import load_dotenv
import psycopg

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.spellcasting import SpellcastingEngine

load_dotenv()

def main():
    print("=" * 60)
    print("SUSTAINED SPELL TRACKING TESTS")
    print("=" * 60)
    
    # Connect to database
    conn = psycopg.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB')
    )
    
    engine = SpellcastingEngine(conn)
    cursor = conn.cursor()
    
    # Get Oak's character ID
    cursor.execute("SELECT id FROM characters WHERE street_name = 'Oak'")
    result = cursor.fetchone()
    
    if not result:
        print("✗ Oak not found in database")
        conn.close()
        return
    
    oak_id = result[0]
    print(f"\n=== Testing with Oak (ID: {oak_id}) ===")
    
    # Test 1: Check initial state (no sustained spells)
    print("\n--- Test 1: Initial State ---")
    sustained = engine.get_sustained_spells(oak_id)
    penalty = engine.calculate_sustaining_penalty(oak_id)
    print(f"Sustained spells: {len(sustained)}")
    print(f"Sustaining penalty: {penalty} dice")
    status1 = "✓" if len(sustained) == 0 and penalty == 0 else "✗"
    print(f"{status1} No sustained spells initially")
    
    # Test 2: Add a sustained spell effect (Armor)
    print("\n--- Test 2: Add Sustained Spell (Armor) ---")
    cursor.execute("""
        INSERT INTO character_modifiers (
            character_id, modifier_type, target_name, modifier_value,
            source, source_type, is_permanent, is_sustained, sustained_by, spell_force
        ) VALUES 
        (%s, 'armor', 'impact', 6, 'Armor', 'spell', false, true, %s, 6),
        (%s, 'armor', 'ballistic', 6, 'Armor', 'spell', false, true, %s, 6)
    """, (oak_id, oak_id, oak_id, oak_id))
    conn.commit()
    print("✓ Added Armor spell modifiers")
    
    sustained = engine.get_sustained_spells(oak_id)
    penalty = engine.calculate_sustaining_penalty(oak_id)
    print(f"Sustained spells: {len(sustained)}")
    for spell in sustained:
        print(f"  - {spell['spell_name']} (Force {spell['force']})")
    print(f"Sustaining penalty: {penalty} dice")
    status2 = "✓" if len(sustained) == 1 and penalty == -2 else "✗"
    print(f"{status2} One sustained spell, -2 penalty")
    
    # Test 3: Add another sustained spell (Increase Strength)
    print("\n--- Test 3: Add Second Sustained Spell ---")
    cursor.execute("""
        INSERT INTO character_modifiers (
            character_id, modifier_type, target_name, modifier_value,
            source, source_type, is_permanent, is_sustained, sustained_by, spell_force
        ) VALUES 
        (%s, 'attribute', 'strength', 2, 'Increase Strength', 'spell', false, true, %s, 4)
    """, (oak_id, oak_id))
    conn.commit()
    print("✓ Added Increase Strength modifier")
    
    sustained = engine.get_sustained_spells(oak_id)
    penalty = engine.calculate_sustaining_penalty(oak_id)
    print(f"Sustained spells: {len(sustained)}")
    for spell in sustained:
        print(f"  - {spell['spell_name']} (Force {spell['force']})")
    print(f"Sustaining penalty: {penalty} dice")
    status3 = "✓" if len(sustained) == 2 and penalty == -4 else "✗"
    print(f"{status3} Two sustained spells, -4 penalty")
    
    # Test 4: Drop one sustained spell
    print("\n--- Test 4: Drop Sustained Spell (Armor) ---")
    dropped = engine.drop_sustained_spell(oak_id, 'Armor')
    print(f"Dropped Armor: {dropped}")
    
    sustained = engine.get_sustained_spells(oak_id)
    penalty = engine.calculate_sustaining_penalty(oak_id)
    print(f"Sustained spells: {len(sustained)}")
    for spell in sustained:
        print(f"  - {spell['spell_name']} (Force {spell['force']})")
    print(f"Sustaining penalty: {penalty} dice")
    status4 = "✓" if len(sustained) == 1 and penalty == -2 and dropped else "✗"
    print(f"{status4} One sustained spell remaining, -2 penalty")
    
    # Test 5: Drop remaining spell
    print("\n--- Test 5: Drop Remaining Spell ---")
    dropped = engine.drop_sustained_spell(oak_id, 'Increase Strength')
    print(f"Dropped Increase Strength: {dropped}")
    
    sustained = engine.get_sustained_spells(oak_id)
    penalty = engine.calculate_sustaining_penalty(oak_id)
    print(f"Sustained spells: {len(sustained)}")
    print(f"Sustaining penalty: {penalty} dice")
    status5 = "✓" if len(sustained) == 0 and penalty == 0 and dropped else "✗"
    print(f"{status5} No sustained spells, no penalty")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 60)
    all_passed = all([
        status1 == "✓", status2 == "✓", status3 == "✓", 
        status4 == "✓", status5 == "✓"
    ])
    if all_passed:
        print("ALL TESTS PASSED ✓")
    else:
        print("SOME TESTS FAILED ✗")
    print("=" * 60)

if __name__ == "__main__":
    main()
