#!/usr/bin/env python3
"""Check cyberware data structure"""
import sys
sys.path.insert(0, '.')

from lib.comprehensive_crud import ComprehensiveCRUD, get_ai_user_id
import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=int(os.getenv('POSTGRES_PORT')),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    dbname=os.getenv('POSTGRES_DB')
)

ai_id = get_ai_user_id(conn)
conn.close()

crud = ComprehensiveCRUD(user_id=ai_id, user_type='AI')
char = crud.get_character_by_street_name('Platinum')
mods = crud.get_modifiers(char['id'])

cyber = [m for m in mods if m.get('source_type') == 'cyberware']

print(f"Total cyberware modifiers: {len(cyber)}\n")
print("Cyberware modifiers:")
for m in cyber:
    desc = m.get('modifier_data', {}).get('description', 'NO DESC')
    print(f"  {m['source']:40} | {m['modifier_type']:15} | {desc}")

crud.close()
