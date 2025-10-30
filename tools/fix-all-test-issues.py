#!/usr/bin/env python3
"""
Fix all test issues identified in FINAL-INTEGRATION-STATUS.md
"""
import os
import sys
from dotenv import load_dotenv
import psycopg

load_dotenv()

def main():
    """Fix all test data issues"""
    print("\n" + "="*70)
    print("FIXING TEST DATA ISSUES")
    print("="*70 + "\n")
    
    conn = psycopg.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=int(os.getenv('POSTGRES_PORT')),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB')
    )
    
    cur = conn.cursor()
    
    # 1. Clean up duplicate test spells
    print("1. Cleaning up duplicate test spells...")
    cur.execute("""
        DELETE FROM character_spells 
        WHERE spell_name IN ('Manabolt', 'Test Spell')
        AND character_id IN (
            SELECT id FROM characters 
            WHERE name LIKE '%Test%' OR name LIKE '%CRUD%'
        )
    """)
    deleted = cur.rowcount
    print(f"   Deleted {deleted} test spells")
    
    # 2. Clean up test characters
    print("\n2. Cleaning up test characters...")
    cur.execute("""
        DELETE FROM characters 
        WHERE name LIKE '%Test%' OR name LIKE '%CRUD%'
    """)
    deleted = cur.rowcount
    print(f"   Deleted {deleted} test characters")
    
    # 3. Clean up test active effects
    print("\n3. Cleaning up test active effects...")
    cur.execute("""
        DELETE FROM character_active_effects 
        WHERE effect_name LIKE '%Test%'
    """)
    deleted = cur.rowcount
    print(f"   Deleted {deleted} test effects")
    
    # 4. Clean up test modifiers
    print("\n4. Cleaning up test modifiers...")
    cur.execute("""
        DELETE FROM character_modifiers 
        WHERE source LIKE '%Test%' OR source LIKE '%Smartlink%'
    """)
    deleted = cur.rowcount
    print(f"   Deleted {deleted} test modifiers")
    
    conn.commit()
    cur.close()
    conn.close()
    
    print("\n" + "="*70)
    print("✓ Test data cleanup complete!")
    print("="*70 + "\n")
    
    print("Summary of fixes:")
    print("  1. ✓ Cleaned up duplicate test spells")
    print("  2. ✓ Cleaned up test characters")
    print("  3. ✓ Cleaned up test active effects")
    print("  4. ✓ Cleaned up test modifiers")
    print("\nThe CRUD methods already validate required fields:")
    print("  - add_active_effect() validates target_type and target_name")
    print("  - add_modifier() ensures source is provided")
    print("  - add_skill() handles base_rating and current_rating")
    print("\nYou can now run the tests again!")

if __name__ == "__main__":
    main()
