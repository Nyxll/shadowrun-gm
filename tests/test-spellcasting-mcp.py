#!/usr/bin/env python3
"""
Test spellcasting with totem modifiers
Tests Oak (favors Health +2, opposes Combat -2)
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
    print("TOTEM MODIFIER TESTS")
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
    
    # Get Oak's character ID
    cursor = conn.cursor()
    cursor.execute("SELECT id, totem FROM characters WHERE street_name = 'Oak'")
    result = cursor.fetchone()
    
    if not result:
        print("✗ Oak not found in database")
        conn.close()
        return
    
    oak_id, totem = result
    print(f"\n=== Testing with Oak (Totem: {totem}) ===")
    
    # Get Oak's spells
    cursor.execute("""
        SELECT cs.spell_name, ms.spell_class, ms.drain_formula
        FROM character_spells cs
        JOIN master_spells ms ON cs.master_spell_id = ms.id
        WHERE cs.character_id = %s AND cs.deleted_at IS NULL
        ORDER BY ms.spell_class, cs.spell_name
    """, (oak_id,))
    
    spells = cursor.fetchall()
    cursor.close()
    
    if not spells:
        print("✗ Oak has no spells linked to master_spells")
        conn.close()
        return
    
    print(f"\nOak has {len(spells)} spell(s) linked to master database:")
    for spell_name, spell_class, drain_formula in spells:
        print(f"  - {spell_name} ({spell_class}): {drain_formula}")
    
    # Test totem modifiers
    print("\n=== Testing Totem Modifiers ===")
    
    test_cases = [
        ('Health', 'Should get +2 bonus (favored)'),
        ('Combat', 'Should get -2 penalty (opposed)'),
        ('Detection', 'Should get 0 (neutral)'),
        ('Illusion', 'Should get 0 (neutral)'),
        ('Manipulation', 'Should get 0 (neutral)')
    ]
    
    for spell_class, expected in test_cases:
        modifier = engine.get_totem_modifier(oak_id, spell_class)
        status = "✓" if (
            (spell_class == 'Health' and modifier == 2) or
            (spell_class == 'Combat' and modifier == -2) or
            (spell_class not in ['Health', 'Combat'] and modifier == 0)
        ) else "✗"
        print(f"{status} {spell_class}: {modifier:+d} dice ({expected})")
    
    # Cast a spell to see totem modifier in action
    if spells:
        spell_name = spells[0][0]  # Use first spell
        spell_class = spells[0][1]
        
        print(f"\n=== Casting {spell_name} ({spell_class}) ===")
        result = engine.cast_spell(oak_id, spell_name)
        
        if 'error' in result:
            print(f"✗ {result['error']}")
        else:
            drain_calc = result['drain_calculation']
            print(f"✓ {result['summary']}")
            print(f"  Base drain: {drain_calc['drain_value']}{drain_calc['damage_code']}")
            print(f"  Totem modifier: {drain_calc['totem_modifier']:+d} dice")
            print(f"  Modified drain: {drain_calc['drain_string']}")
    
    conn.close()
    print("\n" + "=" * 60)
    print("TESTS COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()
