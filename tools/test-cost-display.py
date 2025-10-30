#!/usr/bin/env python3
"""Test that cyberware/bioware costs display correctly"""
import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.comprehensive_crud import ComprehensiveCRUD, get_system_user_id
import psycopg

load_dotenv()

# Get system user
conn = psycopg.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=os.getenv('POSTGRES_PORT'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    dbname=os.getenv('POSTGRES_DB')
)
user_id = get_system_user_id(conn)
conn.close()

# Create CRUD instance
crud = ComprehensiveCRUD(user_id=user_id, user_type='SYSTEM')

# Get Platinum character
chars = crud.list_characters()
platinum = [c for c in chars if 'Kent' in c['name']][0]

print(f"Testing cost display for: {platinum['name']}")
print("=" * 80)

# Get cyberware
cyber = crud.get_character_cyberware(platinum['id'])
print("\nCYBERWARE:")
print("-" * 80)
for c in cyber:
    essence = c.get('essence_cost')
    print(f"  {c['name']}: essence_cost={essence}")
    if essence is None:
        print(f"    ⚠️  MISSING ESSENCE COST!")

# Get bioware
bio = crud.get_character_bioware(platinum['id'])
print("\nBIOWARE:")
print("-" * 80)
for b in bio:
    body_index = b.get('body_index_cost')
    print(f"  {b['name']}: body_index_cost={body_index}")
    if body_index is None:
        print(f"    ⚠️  MISSING BODY INDEX COST!")

crud.close()
print("\n" + "=" * 80)
print("Test complete!")
