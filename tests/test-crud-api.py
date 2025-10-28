#!/usr/bin/env python3
"""
Test suite for Character CRUD API with audit logging
Tests all CRUD operations, soft deletes, and RAG supplementation
"""
import os
import sys
from dotenv import load_dotenv
import psycopg

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.character_crud_api import CharacterCRUDAPI, get_ai_user_id, get_system_user_id

load_dotenv()

def get_test_character_id(conn):
    """Get a test character ID (using Simon Stalman - has magic)"""
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM characters WHERE name = 'Simon Stalman' LIMIT 1")
    result = cursor.fetchone()
    cursor.close()
    if not result:
        raise ValueError("Test character 'Simon Stalman' not found")
    return result[0]


def test_spell_crud_operations():
    """Test complete CRUD lifecycle for spells"""
    print("\n" + "="*80)
    print("TEST: Spell CRUD Operations")
    print("="*80)
    
    # Connect to database
    conn = psycopg.connect(
        host=os.getenv('POSTGRES_HOST', '127.0.0.1'),
        port=int(os.getenv('POSTGRES_PORT', '5434')),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB', 'postgres')
    )
    
    # Get AI user ID
    ai_user_id = get_ai_user_id(conn)
    print(f"✓ AI User ID: {ai_user_id}")
    
    # Get test character
    char_id = get_test_character_id(conn)
    print(f"✓ Test Character ID: {char_id}")
    
    conn.close()
    
    # Initialize CRUD API
    api = CharacterCRUDAPI(user_id=ai_user_id, user_type='AI')
    
    # Test 1: Add spell with minimal data
    print("\n1. Testing ADD spell with minimal data...")
    spell_data = {
        'spell_name': 'Test Fireball',
        'learned_force': 6
    }
    
    try:
        spell = api.add_spell(
            character_id=char_id,
            spell_data=spell_data,
            reason="Testing CRUD API"
        )
        print(f"✓ Spell added: {spell['spell_name']}")
        print(f"  - ID: {spell['id']}")
        print(f"  - Force: {spell['learned_force']}")
        print(f"  - Created by: {spell['created_by']}")
        spell_id = spell['id']
    except Exception as e:
        print(f"✗ Failed to add spell: {e}")
        api.close()
        return False
    
    # Test 2: Get all spells
    print("\n2. Testing GET all spells...")
    try:
        spells = api.get_character_spells(char_id)
        print(f"✓ Retrieved {len(spells)} spells")
        test_spell = [s for s in spells if s['spell_name'] == 'Test Fireball']
        if test_spell:
            print(f"  - Found test spell: {test_spell[0]['spell_name']}")
    except Exception as e:
        print(f"✗ Failed to get spells: {e}")
        api.close()
        return False
    
    # Test 3: Update spell force
    print("\n3. Testing UPDATE spell force...")
    try:
        updated = api.update_spell_force(
            character_id=char_id,
            spell_name='Test Fireball',
            new_force=8,
            reason="Testing force update"
        )
        print(f"✓ Spell force updated: {updated['learned_force']}")
        print(f"  - Modified by: {updated['modified_by']}")
        print(f"  - Modified at: {updated['modified_at']}")
    except Exception as e:
        print(f"✗ Failed to update spell: {e}")
        api.close()
        return False
    
    # Test 4: Update multiple fields
    print("\n4. Testing UPDATE multiple fields...")
    try:
        updates = {
            'spell_category': 'combat',
            'drain_code': '6S',
            'target_type': 'M/S/D',
            'spell_notes': 'Test spell for CRUD operations'
        }
        updated = api.update_spell(
            character_id=char_id,
            spell_name='Test Fireball',
            updates=updates,
            reason="Testing multi-field update"
        )
        print(f"✓ Multiple fields updated:")
        print(f"  - Category: {updated['spell_category']}")
        print(f"  - Drain: {updated['drain_code']}")
        print(f"  - Target: {updated['target_type']}")
    except Exception as e:
        print(f"✗ Failed to update fields: {e}")
        api.close()
        return False
    
    # Test 5: Soft delete
    print("\n5. Testing SOFT DELETE...")
    try:
        deleted = api.soft_delete_spell(
            character_id=char_id,
            spell_name='Test Fireball',
            reason="Testing soft delete"
        )
        print(f"✓ Spell soft deleted:")
        print(f"  - Deleted at: {deleted['deleted_at']}")
        print(f"  - Deleted by: {deleted['deleted_by']}")
    except Exception as e:
        print(f"✗ Failed to soft delete: {e}")
        api.close()
        return False
    
    # Test 6: Verify soft delete (should not appear in active list)
    print("\n6. Testing soft delete verification...")
    try:
        active_spells = api.get_character_spells(char_id, include_deleted=False)
        test_spell = [s for s in active_spells if s['spell_name'] == 'Test Fireball']
        if not test_spell:
            print(f"✓ Spell not in active list (correctly soft deleted)")
        else:
            print(f"✗ Spell still in active list!")
            api.close()
            return False
    except Exception as e:
        print(f"✗ Failed to verify soft delete: {e}")
        api.close()
        return False
    
    # Test 7: Get deleted spells
    print("\n7. Testing GET deleted spells...")
    try:
        all_spells = api.get_character_spells(char_id, include_deleted=True)
        test_spell = [s for s in all_spells if s['spell_name'] == 'Test Fireball']
        if test_spell and test_spell[0]['deleted_at']:
            print(f"✓ Found deleted spell in full list")
            print(f"  - Deleted at: {test_spell[0]['deleted_at']}")
    except Exception as e:
        print(f"✗ Failed to get deleted spells: {e}")
        api.close()
        return False
    
    # Test 8: Restore spell
    print("\n8. Testing RESTORE spell...")
    try:
        restored = api.restore_spell(
            character_id=char_id,
            spell_name='Test Fireball',
            reason="Testing restore"
        )
        print(f"✓ Spell restored:")
        print(f"  - Deleted at: {restored['deleted_at']} (should be None)")
        print(f"  - Modified by: {restored['modified_by']}")
    except Exception as e:
        print(f"✗ Failed to restore spell: {e}")
        api.close()
        return False
    
    # Test 9: Verify restore
    print("\n9. Testing restore verification...")
    try:
        active_spells = api.get_character_spells(char_id, include_deleted=False)
        test_spell = [s for s in active_spells if s['spell_name'] == 'Test Fireball']
        if test_spell:
            print(f"✓ Spell back in active list (correctly restored)")
        else:
            print(f"✗ Spell not in active list after restore!")
            api.close()
            return False
    except Exception as e:
        print(f"✗ Failed to verify restore: {e}")
        api.close()
        return False
    
    # Test 10: Get audit log
    print("\n10. Testing AUDIT LOG...")
    try:
        audit_log = api.get_audit_log(
            table_name='character_spells',
            limit=20
        )
        print(f"✓ Retrieved {len(audit_log)} audit log entries")
        
        # Find entries for our test spell
        test_entries = [e for e in audit_log if 'Test Fireball' in str(e.get('new_values', {}))]
        if test_entries:
            print(f"  - Found {len(test_entries)} entries for test spell")
            for entry in test_entries[:3]:  # Show first 3
                print(f"    • {entry['operation']} by {entry['changed_by_type']} at {entry['changed_at']}")
                if entry.get('change_reason'):
                    print(f"      Reason: {entry['change_reason']}")
    except Exception as e:
        print(f"✗ Failed to get audit log: {e}")
        api.close()
        return False
    
    # Cleanup: Delete test spell permanently
    print("\n11. Cleanup: Deleting test spell...")
    try:
        api.soft_delete_spell(
            character_id=char_id,
            spell_name='Test Fireball',
            reason="Cleanup after testing"
        )
        print(f"✓ Test spell cleaned up")
    except Exception as e:
        print(f"⚠ Warning: Failed to cleanup: {e}")
    
    api.close()
    
    print("\n" + "="*80)
    print("✓ ALL CRUD TESTS PASSED!")
    print("="*80)
    return True


def test_rag_supplementation():
    """Test RAG supplementation for spell data"""
    print("\n" + "="*80)
    print("TEST: RAG Supplementation")
    print("="*80)
    
    # Connect to database
    conn = psycopg.connect(
        host=os.getenv('POSTGRES_HOST', '127.0.0.1'),
        port=int(os.getenv('POSTGRES_PORT', '5434')),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB', 'postgres')
    )
    
    ai_user_id = get_ai_user_id(conn)
    conn.close()
    
    api = CharacterCRUDAPI(user_id=ai_user_id, user_type='AI')
    
    # Test RAG supplementation for common spell
    print("\n1. Testing RAG supplementation for 'Heal' spell...")
    try:
        rag_data = api.supplement_spell_from_rag('Heal')
        print(f"✓ RAG data retrieved:")
        print(f"  - Drain code: {rag_data.get('drain_code')}")
        print(f"  - Target type: {rag_data.get('target_type')}")
        print(f"  - Category: {rag_data.get('spell_category')}")
        if rag_data.get('spell_notes'):
            print(f"  - Notes: {rag_data['spell_notes'][:100]}...")
    except Exception as e:
        print(f"✗ Failed to get RAG data: {e}")
        api.close()
        return False
    
    # Test RAG supplementation for another spell
    print("\n2. Testing RAG supplementation for 'Fireball' spell...")
    try:
        rag_data = api.supplement_spell_from_rag('Fireball')
        print(f"✓ RAG data retrieved:")
        print(f"  - Drain code: {rag_data.get('drain_code')}")
        print(f"  - Target type: {rag_data.get('target_type')}")
        print(f"  - Category: {rag_data.get('spell_category')}")
    except Exception as e:
        print(f"✗ Failed to get RAG data: {e}")
        api.close()
        return False
    
    api.close()
    
    print("\n" + "="*80)
    print("✓ RAG SUPPLEMENTATION TESTS PASSED!")
    print("="*80)
    return True


def test_user_attribution():
    """Test different user types (USER, AI, SYSTEM)"""
    print("\n" + "="*80)
    print("TEST: User Attribution")
    print("="*80)
    
    # Connect to database
    conn = psycopg.connect(
        host=os.getenv('POSTGRES_HOST', '127.0.0.1'),
        port=int(os.getenv('POSTGRES_PORT', '5434')),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB', 'postgres')
    )
    
    # Get different user IDs
    ai_user_id = get_ai_user_id(conn)
    system_user_id = get_system_user_id(conn)
    
    print(f"✓ AI User ID: {ai_user_id}")
    print(f"✓ System User ID: {system_user_id}")
    
    # Get test character
    char_id = get_test_character_id(conn)
    conn.close()
    
    # Test with AI user
    print("\n1. Testing with AI user...")
    api_ai = CharacterCRUDAPI(user_id=ai_user_id, user_type='AI')
    try:
        spell_data = {'spell_name': 'Test AI Spell', 'learned_force': 4}
        spell = api_ai.add_spell(char_id, spell_data, reason="AI test")
        print(f"✓ Spell created by AI user")
        print(f"  - Created by: {spell['created_by']}")
        
        # Cleanup
        api_ai.soft_delete_spell(char_id, 'Test AI Spell', reason="Cleanup")
    except Exception as e:
        print(f"✗ Failed: {e}")
        api_ai.close()
        return False
    api_ai.close()
    
    # Test with SYSTEM user
    print("\n2. Testing with SYSTEM user...")
    api_system = CharacterCRUDAPI(user_id=system_user_id, user_type='SYSTEM')
    try:
        spell_data = {'spell_name': 'Test System Spell', 'learned_force': 4}
        spell = api_system.add_spell(char_id, spell_data, reason="System test")
        print(f"✓ Spell created by SYSTEM user")
        print(f"  - Created by: {spell['created_by']}")
        
        # Cleanup
        api_system.soft_delete_spell(char_id, 'Test System Spell', reason="Cleanup")
    except Exception as e:
        print(f"✗ Failed: {e}")
        api_system.close()
        return False
    api_system.close()
    
    print("\n" + "="*80)
    print("✓ USER ATTRIBUTION TESTS PASSED!")
    print("="*80)
    return True


if __name__ == "__main__":
    print("\n" + "="*80)
    print("CHARACTER CRUD API TEST SUITE")
    print("="*80)
    
    all_passed = True
    
    # Run all tests
    try:
        if not test_spell_crud_operations():
            all_passed = False
    except Exception as e:
        print(f"\n✗ CRUD operations test failed with exception: {e}")
        all_passed = False
    
    try:
        if not test_rag_supplementation():
            all_passed = False
    except Exception as e:
        print(f"\n✗ RAG supplementation test failed with exception: {e}")
        all_passed = False
    
    try:
        if not test_user_attribution():
            all_passed = False
    except Exception as e:
        print(f"\n✗ User attribution test failed with exception: {e}")
        all_passed = False
    
    # Final summary
    print("\n" + "="*80)
    if all_passed:
        print("✓✓✓ ALL TESTS PASSED! ✓✓✓")
    else:
        print("✗✗✗ SOME TESTS FAILED ✗✗✗")
    print("="*80)
    
    sys.exit(0 if all_passed else 1)
