#!/usr/bin/env python3
"""
Test cast_spell operation with real spell data
"""
import os
import sys
from dotenv import load_dotenv
import psycopg

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.spellcasting import SpellcastingEngine, DrainFormulaParser

load_dotenv()

def test_drain_formula_parser():
    """Test drain formula parsing"""
    print("\n=== Testing Drain Formula Parser ===")
    
    parser = DrainFormulaParser()
    
    test_cases = [
        ("(F/2)S", 6, (3, "S")),
        ("[(F/2)+1]D", 6, (4, "D")),
        ("[(F/2)-1]M", 6, (2, "M")),
        ("(F/2)L", 4, (2, "L")),
        ("[(F/2)+2]S", 8, (6, "S"))
    ]
    
    for formula, force, expected in test_cases:
        result = parser.parse_formula(formula, force)
        status = "✓" if result == expected else "✗"
        print(f"{status} {formula} at Force {force} = {result} (expected {expected})")

def test_spell_lookup():
    """Test looking up spells from master_spells"""
    print("\n=== Testing Spell Lookup ===")
    
    conn = psycopg.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB')
    )
    
    engine = SpellcastingEngine(conn)
    
    # Test a few known spells
    test_spells = ["Manabolt", "Heal", "Invisibility", "Armor"]
    
    for spell_name in test_spells:
        spell = engine.get_spell_info(spell_name)
        if spell:
            print(f"✓ {spell_name}: {spell['spell_class']}, {spell['drain_formula']}")
        else:
            print(f"✗ {spell_name}: Not found")
    
    conn.close()

def test_cast_spell_oak():
    """Test casting a spell with Oak (has totem modifiers)"""
    print("\n=== Testing Cast Spell with Oak ===")
    
    conn = psycopg.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB')
    )
    
    engine = SpellcastingEngine(conn)
    
    # Get Oak's character ID
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM characters WHERE street_name = 'Oak'")
    result = cursor.fetchone()
    
    if not result:
        print("✗ Oak not found in database")
        conn.close()
        return
    
    oak_id = result[0]
    
    # Check if Oak has any spells
    cursor.execute("""
        SELECT spell_name, force, drain_code 
        FROM character_spells 
        WHERE character_id = %s AND deleted_at IS NULL
        ORDER BY spell_name
    """, (oak_id,))
    
    spells = cursor.fetchall()
    cursor.close()
    
    if not spells:
        print("✗ Oak has no spells to test")
        conn.close()
        return
    
    print(f"Oak has {len(spells)} spells")
    
    # Find Mind Probe (the one we linked)
    mind_probe = next((s for s in spells if s[0] == 'Mind Probe'), None)
    
    if not mind_probe:
        print("✗ Mind Probe not found in Oak's spells")
        conn.close()
        return
    
    spell_name = mind_probe[0]
    learned_force = mind_probe[1]
    
    print(f"\nCasting {spell_name} (learned at Force {learned_force})...")
    
    result = engine.cast_spell(oak_id, spell_name)
    
    if 'error' in result:
        print(f"✗ Error: {result['error']}")
    else:
        print(f"✓ {result['summary']}")
        print(f"  Drain: {result['drain_calculation']['drain_string']}")
        print(f"  Totem modifier: {result['drain_calculation']['totem_modifier']}")
        print(f"  Resistance: {result['drain_resistance']['successes']} successes")
        print(f"  Damage taken: {result['drain_resistance']['damage_taken']}")
    
    conn.close()

def main():
    """Run all tests"""
    print("=" * 60)
    print("SPELLCASTING TESTS")
    print("=" * 60)
    
    try:
        test_drain_formula_parser()
        test_spell_lookup()
        test_cast_spell_oak()
        
        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETE")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
