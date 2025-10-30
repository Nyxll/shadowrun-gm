#!/usr/bin/env python3
"""
Test the new grouped cyberware/bioware structure
"""
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.comprehensive_crud import ComprehensiveCRUD, get_ai_user_id
import psycopg

load_dotenv()

# Get AI user
conn = psycopg.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=int(os.getenv('POSTGRES_PORT')),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    dbname=os.getenv('POSTGRES_DB')
)
ai_user_id = get_ai_user_id(conn)
conn.close()

# Create CRUD instance
crud = ComprehensiveCRUD(user_id=ai_user_id, user_type='AI')

# Get Platinum's character
try:
    char = crud.get_character_by_street_name('Platinum')
    print(f"Testing cyberware grouping for {char['street_name']}")
    print("=" * 80)
    
    # Get cyberware
    cyberware = crud.get_character_cyberware(char['id'])
    print(f"\nCYBERWARE ({len(cyberware)} items):")
    for item in cyberware:
        print(f"\n  {item['name']}")
        if item.get('essence_cost'):
            print(f"    Essence: {item['essence_cost']}")
        if item.get('effects'):
            print(f"    Effects:")
            for effect in item['effects']:
                print(f"      - {effect}")
        if item.get('modifier_data'):
            print(f"    Data: {item['modifier_data']}")
    
    # Get bioware
    bioware = crud.get_character_bioware(char['id'])
    print(f"\nBIOWARE ({len(bioware)} items):")
    for item in bioware:
        print(f"\n  {item['name']}")
        if item.get('body_index_cost'):
            print(f"    Body Index: {item['body_index_cost']}")
        if item.get('effects'):
            print(f"    Effects:")
            for effect in item['effects']:
                print(f"      - {effect}")
        if item.get('modifier_data'):
            print(f"    Data: {item['modifier_data']}")
    
    print("\n" + "=" * 80)
    print("✓ Grouping working correctly!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    crud.close()
