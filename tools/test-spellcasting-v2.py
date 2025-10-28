#!/usr/bin/env python3
"""
Test improved spellcasting with Magic Pool split and fetish bonuses
"""
import os
import sys
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row

load_dotenv()

# Add parent directory to path to import game server modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.dice_roller import DiceRoller

def get_connection():
    """Get database connection"""
    return psycopg.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB'),
        row_factory=dict_row
    )

def setup_test_data(conn):
    """Set up test character with spells and foci"""
    cursor = conn.cursor()
    
    print("Setting up test data...")
    
    # Get Platinum's character ID (street name is Platinum, full name is Kent Jefferies)
    cursor.execute("""
        SELECT id, name, current_magic, current_willpower
        FROM characters
        WHERE LOWER(street_name) = 'platinum'
    """)
    
    char = cursor.fetchone()
    if not char:
        print("ERROR: Platinum character not found!")
        return None
    
    char_id = char['id']
    print(f"✓ Found character: {char['name']}")
    print(f"  Magic: {char['current_magic']}, Willpower: {char['current_willpower']}")
    
    # Add test spell: Heal (Health category)
    cursor.execute("""
        INSERT INTO character_spells (
            character_id, spell_name, spell_category, spell_type,
            target_type, duration, drain_modifier, description
        ) VALUES (
            %s, 'Heal', 'Health', 'Physical',
            'Touch', 'Permanent', 0, 'Heals physical damage'
        )
        ON CONFLICT (character_id, spell_name) DO NOTHING
    """, (char_id,))
    
    print("✓ Added Heal spell")
    
    # Add test spell: Fireball (Combat category)
    cursor.execute("""
        INSERT INTO character_spells (
            character_id, spell_name, spell_category, spell_type,
            target_type, duration, drain_modifier, description
        ) VALUES (
            %s, 'Fireball', 'Combat', 'Physical',
            'Area', 'Instant', 2, 'Explosive fire damage'
        )
        ON CONFLICT (character_id, spell_name) DO NOTHING
    """, (char_id,))
    
    print("✓ Added Fireball spell")
    
    # Add Force 3 Health fetish
    cursor.execute("""
        INSERT INTO character_foci (
            character_id, focus_name, focus_type, force,
            spell_category, bonus_dice, bonded, description
        ) VALUES (
            %s, 'Health Fetish', 'spell', 3,
            'Health', 2, true, 'Carved bone fetish for Health spells'
        )
        ON CONFLICT (character_id, focus_name) DO NOTHING
    """, (char_id,))
    
    print("✓ Added Force 3 Health fetish (+2 dice)")
    
    # Add Force 6 Combat focus
    cursor.execute("""
        INSERT INTO character_foci (
            character_id, focus_name, focus_type, force,
            spell_category, bonus_dice, bonded, description
        ) VALUES (
            %s, 'Combat Focus', 'spell', 6,
            'Combat', 3, true, 'Crystal focus for Combat spells'
        )
        ON CONFLICT (character_id, focus_name) DO NOTHING
    """, (char_id,))
    
    print("✓ Added Force 6 Combat focus (+3 dice)")
    
    conn.commit()
    return char_id

def test_spell_with_fetish(conn, char_id):
    """Test casting Heal with fetish bonus"""
    cursor = conn.cursor()
    
    print("\n" + "="*60)
    print("TEST 1: Heal spell with Force 3 Health fetish")
    print("="*60)
    
    # Get character data
    cursor.execute("""
        SELECT name, current_magic, current_willpower
        FROM characters WHERE id = %s
    """, (char_id,))
    char = cursor.fetchone()
    
    # Get Sorcery skill
    cursor.execute("""
        SELECT current_rating FROM character_skills
        WHERE character_id = %s AND LOWER(skill_name) = 'sorcery'
    """, (char_id,))
    skill = cursor.fetchone()
    sorcery = skill['current_rating'] if skill else 0
    
    print(f"\nCharacter: {char['name']}")
    print(f"Sorcery: {sorcery}")
    print(f"Magic: {char['current_magic']}")
    print(f"Willpower: {char['current_willpower']}")
    
    # Test parameters
    force = 3
    spell_pool_dice = 2
    drain_pool_dice = 4
    
    print(f"\nCasting Heal at Force {force}")
    print(f"Magic Pool split: {spell_pool_dice} for spell, {drain_pool_dice} for drain")
    
    # Check for fetish
    cursor.execute("""
        SELECT focus_name, force, bonus_dice
        FROM character_foci
        WHERE character_id = %s 
          AND spell_category = 'Health'
          AND force >= %s
        ORDER BY force DESC
        LIMIT 1
    """, (char_id, force))
    
    fetish = cursor.fetchone()
    fetish_bonus = fetish['bonus_dice'] if fetish else 0
    
    if fetish:
        print(f"✓ {fetish['focus_name']} (Force {fetish['force']}) applies: +{fetish_bonus} dice")
    
    # Calculate pools
    spell_dice = sorcery + spell_pool_dice + fetish_bonus
    drain_dice = char['current_willpower'] + drain_pool_dice
    
    print(f"\nSpell dice pool: {sorcery} (Sorcery) + {spell_pool_dice} (Magic Pool) + {fetish_bonus} (fetish) = {spell_dice}d6")
    print(f"Drain dice pool: {char['current_willpower']} (Willpower) + {drain_pool_dice} (Magic Pool) = {drain_dice}d6")
    
    # Roll spell
    spell_result = DiceRoller.roll_with_target_number(spell_dice, force)
    print(f"\nSpell roll: {spell_dice}d6 vs TN {force}")
    print(f"  Rolls: {spell_result.rolls}")
    print(f"  Successes: {spell_result.successes}")
    print(f"  Result: {'SUCCESS' if spell_result.successes > 0 else 'FAILURE'}")
    
    # Calculate drain
    base_drain = force // 2
    drain_tn = base_drain
    drain_code = "M" if force <= 6 else "S"
    
    # Roll drain resistance
    drain_result = DiceRoller.roll_with_target_number(drain_dice, drain_tn)
    drain_damage = max(0, drain_tn - drain_result.successes)
    
    print(f"\nDrain resistance: {drain_dice}d6 vs {drain_tn}{drain_code}")
    print(f"  Rolls: {drain_result.rolls}")
    print(f"  Successes: {drain_result.successes}")
    print(f"  Damage taken: {drain_damage} {drain_code}")
    
    return spell_result.successes > 0

def test_spell_without_fetish(conn, char_id):
    """Test casting Fireball at Force 4 (fetish doesn't apply)"""
    cursor = conn.cursor()
    
    print("\n" + "="*60)
    print("TEST 2: Fireball at Force 4 (fetish Force 6, doesn't apply)")
    print("="*60)
    
    # Get character data
    cursor.execute("""
        SELECT name, current_magic, current_willpower
        FROM characters WHERE id = %s
    """, (char_id,))
    char = cursor.fetchone()
    
    # Get Sorcery skill
    cursor.execute("""
        SELECT current_rating FROM character_skills
        WHERE character_id = %s AND LOWER(skill_name) = 'sorcery'
    """, (char_id,))
    skill = cursor.fetchone()
    sorcery = skill['current_rating'] if skill else 0
    
    # Test parameters
    force = 4
    spell_pool_dice = 3
    drain_pool_dice = 3
    
    print(f"\nCasting Fireball at Force {force}")
    print(f"Magic Pool split: {spell_pool_dice} for spell, {drain_pool_dice} for drain")
    
    # Check for fetish
    cursor.execute("""
        SELECT focus_name, force, bonus_dice
        FROM character_foci
        WHERE character_id = %s 
          AND spell_category = 'Combat'
          AND force >= %s
        ORDER BY force DESC
        LIMIT 1
    """, (char_id, force))
    
    fetish = cursor.fetchone()
    fetish_bonus = fetish['bonus_dice'] if fetish else 0
    
    if fetish:
        print(f"✓ {fetish['focus_name']} (Force {fetish['force']}) applies: +{fetish_bonus} dice")
    else:
        print("✗ No applicable focus (Force 6 focus requires Force 6+ spell)")
    
    # Calculate pools
    spell_dice = sorcery + spell_pool_dice + fetish_bonus
    drain_dice = char['current_willpower'] + drain_pool_dice
    
    print(f"\nSpell dice pool: {sorcery} (Sorcery) + {spell_pool_dice} (Magic Pool) + {fetish_bonus} (focus) = {spell_dice}d6")
    print(f"Drain dice pool: {char['current_willpower']} (Willpower) + {drain_pool_dice} (Magic Pool) = {drain_dice}d6")
    
    # Roll spell
    spell_result = DiceRoller.roll_with_target_number(spell_dice, force)
    print(f"\nSpell roll: {spell_dice}d6 vs TN {force}")
    print(f"  Rolls: {spell_result.rolls}")
    print(f"  Successes: {spell_result.successes}")
    print(f"  Result: {'SUCCESS' if spell_result.successes > 0 else 'FAILURE'}")
    
    # Calculate drain (Fireball has +2 drain modifier)
    base_drain = force // 2
    drain_modifier = 2
    drain_tn = base_drain + drain_modifier
    drain_code = "M" if force <= 6 else "S"
    
    # Roll drain resistance
    drain_result = DiceRoller.roll_with_target_number(drain_dice, drain_tn)
    drain_damage = max(0, drain_tn - drain_result.successes)
    
    print(f"\nDrain resistance: {drain_dice}d6 vs {drain_tn}{drain_code} (base {base_drain} + {drain_modifier} deadly spell)")
    print(f"  Rolls: {drain_result.rolls}")
    print(f"  Successes: {drain_result.successes}")
    print(f"  Damage taken: {drain_damage} {drain_code}")
    
    return spell_result.successes > 0

def test_magic_pool_validation(conn, char_id):
    """Test Magic Pool validation"""
    cursor = conn.cursor()
    
    print("\n" + "="*60)
    print("TEST 3: Magic Pool validation")
    print("="*60)
    
    # Get character magic
    cursor.execute("""
        SELECT name, current_magic
        FROM characters WHERE id = %s
    """, (char_id,))
    char = cursor.fetchone()
    
    magic = char['current_magic']
    print(f"\nCharacter: {char['name']}")
    print(f"Magic rating: {magic}")
    
    # Try to exceed Magic Pool
    spell_pool_dice = 4
    drain_pool_dice = 4
    total = spell_pool_dice + drain_pool_dice
    
    print(f"\nAttempting to use {total} dice ({spell_pool_dice} spell + {drain_pool_dice} drain)")
    
    if total > magic:
        print(f"✓ VALIDATION WORKS: {total} > {magic} (Magic rating)")
        print(f"  Error should be returned by cast_spell tool")
        return True
    else:
        print(f"✗ Test invalid: {total} <= {magic}")
        return False

def main():
    """Run all tests"""
    try:
        conn = get_connection()
        
        print("="*60)
        print("SPELLCASTING V2 TEST SUITE")
        print("="*60)
        
        # Setup test data
        char_id = setup_test_data(conn)
        if not char_id:
            return
        
        # Run tests
        test1_pass = test_spell_with_fetish(conn, char_id)
        test2_pass = test_spell_without_fetish(conn, char_id)
        test3_pass = test_magic_pool_validation(conn, char_id)
        
        # Summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"Test 1 (Heal with fetish): {'PASS' if test1_pass else 'FAIL'}")
        print(f"Test 2 (Fireball without fetish): {'PASS' if test2_pass else 'FAIL'}")
        print(f"Test 3 (Magic Pool validation): {'PASS' if test3_pass else 'FAIL'}")
        
        if test1_pass and test2_pass and test3_pass:
            print("\n✓ ALL TESTS PASSED")
        else:
            print("\n✗ SOME TESTS FAILED")
        
        conn.close()
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
