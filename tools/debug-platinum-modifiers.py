#!/usr/bin/env python3
"""
Debug Platinum's modifiers to see exact database content
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
    
    # Get modifiers using CRUD API - filter by source_type
    print("=" * 80)
    print("TESTING: crud.get_modifiers(char_id, source_type='cyberware')")
    print("=" * 80)
    modifiers = crud.get_modifiers(character['id'], source_type='cyberware')
    
    print(f"\nReturned {len(modifiers)} modifiers\n")
    
    for i, mod in enumerate(modifiers, 1):
        print(f"{i}. Modifier ID: {mod.get('id')}")
        print(f"   source: {mod.get('source')}")
        print(f"   source_type: {mod.get('source_type')}")
        print(f"   modifier_type: {mod.get('modifier_type')}")
        print(f"   target_name: {mod.get('target_name')}")
        print(f"   modifier_value: {mod.get('modifier_value')}")
        print(f"   modifier_data: {mod.get('modifier_data')}")
        print()
    
    # Also try direct SQL query
    print("=" * 80)
    print("TESTING: Direct SQL query")
    print("=" * 80)
    
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute("""
            SELECT id, source, source_type, modifier_type, target_name, modifier_value, modifier_data
            FROM character_modifiers
            WHERE character_id = %s
            AND source_type = 'cyberware'
            AND deleted_at IS NULL
            ORDER BY source, modifier_type DESC
        """, (character['id'],))
        
        rows = cur.fetchall()
        print(f"\nDirect SQL returned {len(rows)} rows\n")
        
        for i, row in enumerate(rows, 1):
            print(f"{i}. {row['source']}")
            print(f"   source_type: {row['source_type']}")
            print(f"   modifier_type: {row['modifier_type']}")
            print(f"   target_name: {row['target_name']}")
            print(f"   modifier_value: {row['modifier_value']}")
            print()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    crud.close()
    conn.close()
