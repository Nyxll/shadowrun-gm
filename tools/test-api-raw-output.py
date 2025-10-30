#!/usr/bin/env python3
"""Test raw API output for cyberware/bioware"""
import os
import sys
import json
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

print(f"Testing API output for: {platinum['name']}")
print("=" * 80)

# Get cyberware
cyber = crud.get_character_cyberware(platinum['id'])
print("\nCYBERWARE (RAW JSON):")
print(json.dumps(cyber, indent=2, default=str))

# Get bioware
bio = crud.get_character_bioware(platinum['id'])
print("\nBIOWARE (RAW JSON):")
print(json.dumps(bio, indent=2, default=str))

crud.close()
