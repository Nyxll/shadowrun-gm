#!/usr/bin/env python3
"""
Test cyberware lookup to see what format CRUD API returns
"""
import os
import sys
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.comprehensive_crud import ComprehensiveCRUD, get_ai_user_id

load_dotenv()

# Get database connection
conn = psycopg.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=int(os.getenv('POSTGRES_PORT')),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    dbname=os.getenv('POSTGRES_DB')
)

# Get AI user ID
ai_user_id = get_ai_user_id(conn)

# Create CRUD instance
crud = ComprehensiveCRUD(user_id=ai_user_id, user_type='AI')

# Get Platinum's character
try:
    character = crud.get_character_by_street_name('Platinum')
    print(f"Character ID: {character['id']}\n")
    
    # Get cyberware using CRUD API
    cyberware = crud.get_character_cyberware(character['id'])
    
    print(f"CRUD API returned {len(cyberware)} cyberware items:\n")
    for i, cyber in enumerate(cyberware, 1):
        print(f"{i}. {cyber.get('source', 'NO SOURCE')}")
        print(f"   Keys: {list(cyber.keys())}")
        print(f"   target_name: {cyber.get('target_name')}")
        print(f"   modifier_value: {cyber.get('modifier_value')}")
        print(f"   modifier_data: {cyber.get('modifier_data')}")
        print()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    crud.close()
    conn.close()
