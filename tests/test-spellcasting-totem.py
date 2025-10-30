#!/usr/bin/env python3
"""
Test spellcasting with totem modifiers
Uses Test Leviathan character (Leviathan totem: favors Combat +2, opposes Illusion -2)
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
    print("TOTEM MODIFIER TESTS - Test Leviathan")
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
    
    # Get Test Leviathan's character ID
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, totem FROM characters WHERE name = 'Test Leviathan'")
    result = cursor.fetchone()
    
    if not result:
        print("✗ Test Leviathan not found in database")
        print("  Creating Test Leviathan character...")
        
        # Create Test Leviathan character
        cursor.execute("""
            INSERT INTO characters (
                name, street_name, totem, character_type,
                base_body, base_quickness, base_strength, base_charisma,
                base_intelligence, base_willpower, base_essence, base_magic, base_reaction,
                current_body, current_quickness, current_strength, current_charisma,
                current_intelligence, current_willpower, current_essence, current_magic, current_reaction
            ) VALUES (
                'Test Leviathan', 'Leviathan', 'Leviathan', 'Shaman',
                5, 4, 4, 4, 5, 6, 6, 6, 4,
                5, 4, 4, 4, 5, 6, 6, 6, 4
            ) RETURNING id
        """)
        lev_id = cursor.fetchone()[0]
        conn.commit()
        print(f"  ✓ Created Test Leviathan (ID: {lev_id})")
    else:
        lev_id, name, totem = result
        print(f"\n=== Testing with {name} (Totem: {totem}) ===")
    
    # Check Leviathan totem data
    cursor.execute("""
        SELECT totem_name, favored_categories, opposed_categories
        FROM totems WHERE LOWER(totem_name) = 'leviathan'
    """)
    totem_data = cursor.fetchone()
    if totem_data:
        print(f"\nLeviathan Totem:")
        print(f"  Favored: {totem_data[1]}")
        print(f"  Opposed: {totem_data[2]}")
    
    # Test totem modifiers
    print("\n=== Testing Totem Modifiers ===")
    
    test_cases = [
        ('Manipulation', +2, 'Should get +2 bonus (favored)'),
        ('Illusion', -2, 'Should get -2 penalty (opposed)'),
        ('Health', 0, 'Should get 0 (neutral)'),
        ('Combat', 0, 'Should get 0 (neutral)'),
        ('Detection', 0, 'Should get 0 (neutral)')
    ]
    
    for spell_class, expected, description in test_cases:
        modifier = engine.get_totem_modifier(lev_id, spell_class)
        status = "✓" if modifier == expected else "✗"
        print(f"{status} {spell_class}: {modifier:+d} dice (expected {expected:+d}) - {description}")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 60)
    print("TESTS COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()
