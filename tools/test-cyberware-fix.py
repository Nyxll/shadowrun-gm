#!/usr/bin/env python3
"""
Test cyberware/bioware retrieval after fix
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.comprehensive_crud import ComprehensiveCRUD, get_ai_user_id
import psycopg

# Get AI user
conn = psycopg.connect(
    host=os.getenv('POSTGRES_HOST', '127.0.0.1'),
    port=int(os.getenv('POSTGRES_PORT', '5434')),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    dbname=os.getenv('POSTGRES_DB')
)

ai_user_id = get_ai_user_id(conn)
conn.close()

# Create CRUD instance
crud = ComprehensiveCRUD(user_id=ai_user_id, user_type='AI')

# Get Platinum
try:
    character = crud.get_character_by_street_name('Platinum')
    char_id = character['id']
    
    print(f"Character: {character['name']} ({character['street_name']})")
    print(f"ID: {char_id}")
    print()
    
    # Test cyberware retrieval
    print("Testing get_character_cyberware...")
    cyberware = crud.get_character_cyberware(char_id)
    print(f"Found {len(cyberware)} cyberware items")
    if cyberware:
        print("\nFirst cyberware item:")
        print(f"  Source: {cyberware[0].get('source')}")
        print(f"  Source Type: {cyberware[0].get('source_type')}")
        print(f"  Modifier Type: {cyberware[0].get('modifier_type')}")
        print(f"  Target: {cyberware[0].get('target_name')}")
        print(f"  Value: {cyberware[0].get('modifier_value')}")
    print()
    
    # Test bioware retrieval
    print("Testing get_character_bioware...")
    bioware = crud.get_character_bioware(char_id)
    print(f"Found {len(bioware)} bioware items")
    if bioware:
        print("\nFirst bioware item:")
        print(f"  Source: {bioware[0].get('source')}")
        print(f"  Source Type: {bioware[0].get('source_type')}")
        print(f"  Modifier Type: {bioware[0].get('modifier_type')}")
        print(f"  Target: {bioware[0].get('target_name')}")
        print(f"  Value: {bioware[0].get('modifier_value')}")
    
    print("\n" + "="*80)
    print("SUCCESS: Cyberware/bioware retrieval is working!")
    print("="*80)
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
finally:
    crud.close()
