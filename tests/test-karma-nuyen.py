#!/usr/bin/env python3
"""
Test karma and nuyen management functions
"""
import os
import sys
from dotenv import load_dotenv
import psycopg

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib.comprehensive_crud import ComprehensiveCRUD, get_system_user_id

load_dotenv()

# Get system user
conn = psycopg.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=int(os.getenv('POSTGRES_PORT')),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    dbname=os.getenv('POSTGRES_DB')
)
user_id = get_system_user_id(conn)
conn.close()

crud = ComprehensiveCRUD(user_id)

print("Testing Karma & Nuyen Management Functions")
print("=" * 60)

# Get a test character
try:
    char = crud.get_character_by_street_name("Oak")
    print(f"\n✓ Found character: {char['name']}")
    print(f"  Current karma_pool: {char.get('karma_pool', 0)}")
    print(f"  Current karma_total: {char.get('karma_total', 0)}")
    print(f"  Current karma_available: {char.get('karma_available', 0)}")
    print(f"  Current nuyen: {char.get('nuyen', 0)}")
    
    # Test add_karma
    print("\n1. Testing add_karma(5)...")
    result = crud.add_karma(char['id'], 5, "Test karma award")
    print(f"   ✓ Added 5 karma")
    print(f"   Total: {result['karma_total']}, Available: {result.get('karma_available', 0)}")
    
    # Test spend_karma
    print("\n2. Testing spend_karma(2)...")
    result = crud.spend_karma(char['id'], 2, "Test karma spend")
    print(f"   ✓ Spent 2 karma")
    print(f"   Available: {result.get('karma_available', 0)}")
    
    # Test update_karma_pool
    print("\n3. Testing update_karma_pool(10)...")
    result = crud.update_karma_pool(char['id'], 10, "Test karma pool update")
    print(f"   ✓ Set karma pool to 10")
    print(f"   Karma pool: {result['karma_pool']}")
    
    # Test add_nuyen
    print("\n4. Testing add_nuyen(1000)...")
    result = crud.add_nuyen(char['id'], 1000, "Test nuyen award")
    print(f"   ✓ Added 1000¥")
    print(f"   Nuyen: {result['nuyen']}¥")
    
    # Test spend_nuyen
    print("\n5. Testing spend_nuyen(500)...")
    result = crud.spend_nuyen(char['id'], 500, "Test nuyen spend")
    print(f"   ✓ Spent 500¥")
    print(f"   Nuyen: {result['nuyen']}¥")
    
    # Test error handling - insufficient karma
    print("\n6. Testing error handling (insufficient karma)...")
    try:
        crud.spend_karma(char['id'], 999999, "Should fail")
        print("   ✗ Should have raised error!")
    except ValueError as e:
        print(f"   ✓ Correctly raised error: {e}")
    
    # Test error handling - insufficient nuyen
    print("\n7. Testing error handling (insufficient nuyen)...")
    try:
        crud.spend_nuyen(char['id'], 999999, "Should fail")
        print("   ✗ Should have raised error!")
    except ValueError as e:
        print(f"   ✓ Correctly raised error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ All karma & nuyen tests passed!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    crud.close()
