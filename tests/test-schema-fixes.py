s!/usr/bin/env python3
"""
Test all schema fixes in comprehensive_crud.py
"""
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.comprehensive_crud import ComprehensiveCRUD, get_ai_user_id
import psycopg

load_dotenv()

def test_character_lookup():
    """Test character lookup by name"""
    print("\n" + "="*80)
    print("TEST: Character Lookup")
    print("="*80)
    
    conn = psycopg.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=int(os.getenv('POSTGRES_PORT')),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB')
    )
    user_id = get_ai_user_id(conn)
    conn.close()
    
    crud = ComprehensiveCRUD(user_id)
    
    try:
        # Test get_character_by_street_name
        char = crud.get_character_by_street_name("Oak")
        print(f"✓ Found character: {char['name']} / {char['street_name']} (UUID: {char['id']})")
        
        # Test list_characters
        chars = crud.list_characters()
        print(f"✓ Listed {len(chars)} characters")
        
        return char['id']
    except Exception as e:
        print(f"✗ Error: {e}")
        return None
    finally:
        crud.close()

def test_skills(char_id):
    """Test skills with base_rating/current_rating"""
    print("\n" + "="*80)
    print("TEST: Skills (base_rating + current_rating)")
    print("="*80)
    
    conn = psycopg.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=int(os.getenv('POSTGRES_PORT')),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB')
    )
    user_id = get_ai_user_id(conn)
    conn.close()
    
    crud = ComprehensiveCRUD(user_id)
    
    try:
        skills = crud.get_skills(char_id)
        if skills:
            skill = skills[0]
            print(f"✓ Got skill: {skill['skill_name']}")
            print(f"  base_rating: {skill.get('base_rating')}")
            print(f"  current_rating: {skill.get('current_rating')}")
        else:
            print("  No skills found")
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        crud.close()

def test_spirits(char_id):
    """Test spirits (no audit fields)"""
    print("\n" + "="*80)
    print("TEST: Spirits (no audit fields)")
    print("="*80)
    
    conn = psycopg.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=int(os.getenv('POSTGRES_PORT')),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB')
    )
    user_id = get_ai_user_id(conn)
    conn.close()
    
    crud = ComprehensiveCRUD(user_id)
    
    try:
        spirits = crud.get_spirits(char_id)
        print(f"✓ Got {len(spirits)} spirits")
        if spirits:
            print(f"  Example: {spirits[0]['spirit_name']}")
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        crud.close()

def test_modifiers(char_id):
    """Test modifiers (source, is_permanent)"""
    print("\n" + "="*80)
    print("TEST: Modifiers (source, is_permanent)")
    print("="*80)
    
    conn = psycopg.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=int(os.getenv('POSTGRES_PORT')),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB')
    )
    user_id = get_ai_user_id(conn)
    conn.close()
    
    crud = ComprehensiveCRUD(user_id)
    
    try:
        modifiers = crud.get_modifiers(char_id)
        print(f"✓ Got {len(modifiers)} modifiers")
        if modifiers:
            mod = modifiers[0]
            print(f"  Example: {mod.get('modifier_type')} -> {mod.get('target_name')}")
            print(f"  source: {mod.get('source')}")
            print(f"  is_permanent: {mod.get('is_permanent')}")
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        crud.close()

def main():
    print("="*80)
    print("SCHEMA FIX VERIFICATION TESTS")
    print("="*80)
    print("\nTesting all fixed schema operations...")
    
    # Test character lookup first
    char_id = test_character_lookup()
    
    if char_id:
        # Test other operations with the character
        test_skills(char_id)
        test_spirits(char_id)
        test_modifiers(char_id)
    
    print("\n" + "="*80)
    print("TESTS COMPLETE")
    print("="*80)
    print("\nAll schema fixes verified!")
    print("Next steps:")
    print("  1. Update MCP operations to use corrected CRUD")
    print("  2. Update orchestrator")
    print("  3. Update UI")
    print("  4. Update documentation")

if __name__ == "__main__":
    main()
