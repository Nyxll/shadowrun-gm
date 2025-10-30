#!/usr/bin/env python3
"""
Safely clean up test data with deadlock handling
"""
import os
import sys
import time
from dotenv import load_dotenv
import psycopg

load_dotenv()

def safe_cleanup():
    """Clean up test data with retry logic"""
    print("\n" + "="*70)
    print("SAFE TEST DATA CLEANUP")
    print("="*70 + "\n")
    
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1}/{max_retries}...")
            
            conn = psycopg.connect(
                host=os.getenv('POSTGRES_HOST'),
                port=int(os.getenv('POSTGRES_PORT')),
                user=os.getenv('POSTGRES_USER'),
                password=os.getenv('POSTGRES_PASSWORD'),
                dbname=os.getenv('POSTGRES_DB'),
                autocommit=True  # Avoid transaction deadlocks
            )
            
            cur = conn.cursor()
            
            # 1. Clean up test spells first (no foreign key dependencies)
            print("\n1. Cleaning up test spells...")
            cur.execute("""
                DELETE FROM character_spells 
                WHERE spell_name IN ('Manabolt', 'Test Spell')
                AND character_id IN (
                    SELECT id FROM characters 
                    WHERE name LIKE '%Test%' OR name LIKE '%CRUD%'
                )
            """)
            print(f"   Deleted {cur.rowcount} test spells")
            
            # 2. Clean up test active effects
            print("\n2. Cleaning up test active effects...")
            cur.execute("""
                DELETE FROM character_active_effects 
                WHERE effect_name LIKE '%Test%'
            """)
            print(f"   Deleted {cur.rowcount} test effects")
            
            # 3. Clean up test modifiers
            print("\n3. Cleaning up test modifiers...")
            cur.execute("""
                DELETE FROM character_modifiers 
                WHERE source LIKE '%Test%' OR source LIKE '%Smartlink%'
            """)
            print(f"   Deleted {cur.rowcount} test modifiers")
            
            # 4. Clean up test skills
            print("\n4. Cleaning up test skills...")
            cur.execute("""
                DELETE FROM character_skills
                WHERE character_id IN (
                    SELECT id FROM characters 
                    WHERE name LIKE '%Test%' OR name LIKE '%CRUD%'
                )
            """)
            print(f"   Deleted {cur.rowcount} test skills")
            
            # 5. Clean up test gear
            print("\n5. Cleaning up test gear...")
            cur.execute("""
                DELETE FROM character_gear
                WHERE character_id IN (
                    SELECT id FROM characters 
                    WHERE name LIKE '%Test%' OR name LIKE '%CRUD%'
                )
            """)
            print(f"   Deleted {cur.rowcount} test gear")
            
            # 6. Finally, clean up test characters
            print("\n6. Cleaning up test characters...")
            cur.execute("""
                DELETE FROM characters 
                WHERE name LIKE '%Test%' OR name LIKE '%CRUD%'
            """)
            print(f"   Deleted {cur.rowcount} test characters")
            
            cur.close()
            conn.close()
            
            print("\n" + "="*70)
            print("✓ Test data cleanup complete!")
            print("="*70 + "\n")
            return True
            
        except psycopg.errors.DeadlockDetected as e:
            print(f"\n⚠ Deadlock detected on attempt {attempt + 1}")
            if attempt < max_retries - 1:
                print(f"   Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("\n✗ Failed after all retries")
                print("   Please close other database connections and try again")
                return False
                
        except Exception as e:
            print(f"\n✗ Error: {e}")
            return False
    
    return False

if __name__ == "__main__":
    success = safe_cleanup()
    sys.exit(0 if success else 1)
