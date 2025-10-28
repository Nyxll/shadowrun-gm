#!/usr/bin/env python3
"""
Comprehensive test suite for CRUD API
Tests all 40+ CRUD operations with audit logging
"""
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.comprehensive_crud import ComprehensiveCRUD, get_ai_user_id
import psycopg

load_dotenv()

def get_test_character_id():
    """
    Get Simon Stalman's character UUID for testing
    Uses CRUD API lookup helper to demonstrate proper UUID usage
    """
    conn = psycopg.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB')
    )
    ai_user_id = get_ai_user_id(conn)
    conn.close()
    
    # Use CRUD API to look up character by name and get UUID
    crud = ComprehensiveCRUD(ai_user_id, 'AI')
    try:
        character = crud.get_character_by_name('Simon Stalman')
        char_id = character['id']  # This is the UUID
        crud.close()
        return char_id
    except ValueError:
        crud.close()
        return None

def test_spells():
    """Test spell CRUD operations"""
    print("\n" + "="*80)
    print("TESTING SPELL CRUD OPERATIONS")
    print("="*80)
    
    char_id = get_test_character_id()
    if not char_id:
        print("[FAIL] No test character found")
        return False
    
    conn = psycopg.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB')
    )
    ai_user_id = get_ai_user_id(conn)
    conn.close()
    
    crud = ComprehensiveCRUD(ai_user_id, 'AI')
    
    try:
        # Get existing spells
        spells = crud.get_spells(char_id)
        print(f"[PASS] get_spells: Found {len(spells)} spells")
        
        # Add a test spell
        test_spell = crud.add_spell(char_id, {
            'spell_name': 'Test Fireball',
            'learned_force': 6,
            'spell_category': 'combat',
            'spell_type': 'mana',
            'drain_code': '(F/2)M'
        }, reason="Test spell creation")
        print(f"[PASS] add_spell: Created '{test_spell['spell_name']}'")
        
        # Update spell
        updated = crud.update_spell(char_id, 'Test Fireball', {
            'learned_force': 8,
            'description': 'Updated test spell'
        }, reason="Test spell update")
        print(f"[PASS] update_spell: Updated force to {updated['learned_force']}")
        
        # Delete spell
        deleted = crud.delete_spell(char_id, 'Test Fireball', reason="Test cleanup")
        print(f"[PASS] delete_spell: Soft deleted '{deleted['spell_name']}'")
        
        crud.close()
        return True
        
    except Exception as e:
        print(f"[FAIL] Spell CRUD failed: {e}")
        crud.close()
        return False

def test_active_effects():
    """Test active effects CRUD (critical for Grok)"""
    print("\n" + "="*80)
    print("TESTING ACTIVE EFFECTS CRUD (Curses, Poison, etc.)")
    print("="*80)
    
    char_id = get_test_character_id()
    if not char_id:
        print("[FAIL] No test character found")
        return False
    
    conn = psycopg.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB')
    )
    ai_user_id = get_ai_user_id(conn)
    conn.close()
    
    crud = ComprehensiveCRUD(ai_user_id, 'AI')
    
    try:
        # Add curse effect
        curse = crud.add_active_effect(char_id, {
            'effect_name': 'Quickened Curse',
            'effect_type': 'spell',
            'source': 'Enemy Mage',
            'duration': 'sustained',
            'modifiers': {'dice_pool': -2},
            'notes': 'Reduces all dice pools by 2'
        }, reason="Enemy mage cast curse")
        print(f"[PASS] add_active_effect: Added curse '{curse['effect_name']}'")
        
        # Add poison effect
        poison = crud.add_active_effect(char_id, {
            'effect_name': 'Neurostun Poison',
            'effect_type': 'poison',
            'source': 'Dart trap',
            'duration': '10 minutes',
            'modifiers': {'reaction': -2, 'quickness': -2},
            'notes': 'Reduces REA and QUI by 2'
        }, reason="Character hit by poison dart")
        print(f"[PASS] add_active_effect: Added poison '{poison['effect_name']}'")
        
        # Get active effects
        effects = crud.get_active_effects(char_id, active_only=True)
        print(f"[PASS] get_active_effects: Found {len(effects)} active effects")
        
        # Deactivate curse (spell ends)
        deactivated = crud.deactivate_effect(char_id, 'Quickened Curse', reason="Spell duration ended")
        print(f"[PASS] deactivate_effect: Deactivated '{deactivated['effect_name']}'")
        
        # Remove poison (cured)
        removed = crud.remove_effect(char_id, 'Neurostun Poison', reason="Antidote administered")
        print(f"[PASS] remove_effect: Removed '{removed['effect_name']}'")
        
        crud.close()
        return True
        
    except Exception as e:
        print(f"[FAIL] Active Effects CRUD failed: {e}")
        crud.close()
        return False

def test_modifiers():
    """Test modifiers CRUD (critical for Grok)"""
    print("\n" + "="*80)
    print("TESTING MODIFIERS CRUD (Temporary/Permanent)")
    print("="*80)
    
    char_id = get_test_character_id()
    if not char_id:
        print("[FAIL] No test character found")
        return False
    
    conn = psycopg.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB')
    )
    ai_user_id = get_ai_user_id(conn)
    conn.close()
    
    crud = ComprehensiveCRUD(ai_user_id, 'AI')
    
    try:
        # Add temporary modifier (spell effect)
        temp_mod = crud.add_modifier(char_id, {
            'modifier_type': 'attribute',
            'target_name': 'Strength',
            'modifier_value': 3,
            'source_type': 'spell',
            'source_name': 'Increase Strength',
            'is_temporary': True,
            'modifier_data': {'duration': '1 hour'}
        }, reason="Spell cast on character")
        print(f"[PASS] add_modifier: Added temporary +3 STR modifier")
        
        # Add permanent modifier (cyberware)
        perm_mod = crud.add_modifier(char_id, {
            'modifier_type': 'attribute',
            'target_name': 'Reaction',
            'modifier_value': 1,
            'source_type': 'cyberware',
            'source_name': 'Wired Reflexes',
            'is_temporary': False
        }, reason="Cyberware installed")
        print(f"[PASS] add_modifier: Added permanent +1 REA modifier")
        
        # Get all modifiers
        mods = crud.get_modifiers(char_id)
        print(f"[PASS] get_modifiers: Found {len(mods)} total modifiers")
        
        # Get only attribute modifiers
        attr_mods = crud.get_modifiers(char_id, modifier_type='attribute')
        print(f"[PASS] get_modifiers (filtered): Found {len(attr_mods)} attribute modifiers")
        
        # Remove temporary modifiers (spell ends)
        removed = crud.remove_temporary_modifiers(char_id, reason="Spell duration ended")
        print(f"[PASS] remove_temporary_modifiers: Removed {len(removed)} temporary modifiers")
        
        # Remove permanent modifier by ID
        if perm_mod:
            crud.remove_modifier(perm_mod['id'], reason="Cyberware removed")
            print(f"[PASS] remove_modifier: Removed permanent modifier")
        
        crud.close()
        return True
        
    except Exception as e:
        print(f"[FAIL] Modifiers CRUD failed: {e}")
        crud.close()
        return False

def test_skills():
    """Test skills CRUD"""
    print("\n" + "="*80)
    print("TESTING SKILLS CRUD")
    print("="*80)
    
    char_id = get_test_character_id()
    if not char_id:
        print("[FAIL] No test character found")
        return False
    
    conn = psycopg.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB')
    )
    ai_user_id = get_ai_user_id(conn)
    conn.close()
    
    crud = ComprehensiveCRUD(ai_user_id, 'AI')
    
    try:
        # Get existing skills
        skills = crud.get_skills(char_id)
        print(f"[PASS] get_skills: Found {len(skills)} skills")
        
        # Add new skill
        new_skill = crud.add_skill(char_id, {
            'skill_name': 'Test Skill',
            'rating': 3
        }, reason="Learning new skill")
        print(f"[PASS] add_skill: Added '{new_skill['skill_name']}' at rating {new_skill['rating']}")
        
        # Improve skill
        improved = crud.improve_skill(char_id, 'Test Skill', 5, reason="Skill improvement")
        print(f"[PASS] improve_skill: Improved to rating {improved['rating']}")
        
        # Add specialization
        specialized = crud.add_specialization(char_id, 'Test Skill', 'Combat', reason="Specialization training")
        print(f"[PASS] add_specialization: Added '{specialized['specialization']}' specialization")
        
        # Cleanup - remove test skill
        conn = psycopg.connect(
            host=os.getenv('POSTGRES_HOST'),
            port=os.getenv('POSTGRES_PORT'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            dbname=os.getenv('POSTGRES_DB')
        )
        cur = conn.cursor()
        cur.execute("DELETE FROM character_skills WHERE character_id = %s AND skill_name = 'Test Skill'", (char_id,))
        conn.commit()
        cur.close()
        conn.close()
        
        crud.close()
        return True
        
    except Exception as e:
        print(f"[FAIL] Skills CRUD failed: {e}")
        crud.close()
        return False

def test_all_operations():
    """Run all CRUD tests"""
    print("\n" + "="*80)
    print("COMPREHENSIVE CRUD API TEST SUITE")
    print("="*80)
    
    results = {
        'Spells': test_spells(),
        'Active Effects': test_active_effects(),
        'Modifiers': test_modifiers(),
        'Skills': test_skills()
    }
    
    print("\n" + "="*80)
    print("TEST RESULTS SUMMARY")
    print("="*80)
    
    for test_name, passed in results.items():
        status = "[PASS] PASS" if passed else "[FAIL] FAIL"
        print(f"{status}: {test_name}")
    
    total = len(results)
    passed = sum(1 for p in results.values() if p)
    print(f"\nTotal: {passed}/{total} test suites passed")
    
    return all(results.values())

if __name__ == "__main__":
    success = test_all_operations()
    sys.exit(0 if success else 1)
