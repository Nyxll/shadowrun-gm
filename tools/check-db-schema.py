#!/usr/bin/env python3
"""Check current database schema"""
import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

conn = psycopg.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=os.getenv('POSTGRES_PORT'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    dbname=os.getenv('POSTGRES_DB')
)

cursor = conn.cursor()

# Check character_modifiers table
print("=" * 70)
print("CHARACTER_MODIFIERS TABLE STRUCTURE")
print("=" * 70)
cursor.execute("""
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns 
    WHERE table_name = 'character_modifiers' 
    ORDER BY ordinal_position
""")

cols = cursor.fetchall()
if cols:
    for col in cols:
        print(f"  {col[0]:<30} {col[1]:<20} {'NULL' if col[2] == 'YES' else 'NOT NULL'}")
else:
    print("  Table does not exist")

# Check characters table
print("\n" + "=" * 70)
print("CHARACTERS TABLE STRUCTURE")
print("=" * 70)
cursor.execute("""
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns 
    WHERE table_name = 'characters' 
    ORDER BY ordinal_position
""")

cols = cursor.fetchall()
if cols:
    for col in cols:
        print(f"  {col[0]:<30} {col[1]:<20} {'NULL' if col[2] == 'YES' else 'NOT NULL'}")
else:
    print("  Table does not exist")

# Check house_rules table
print("\n" + "=" * 70)
print("HOUSE_RULES TABLE")
print("=" * 70)
cursor.execute("""
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns 
    WHERE table_name = 'house_rules' 
    ORDER BY ordinal_position
""")

cols = cursor.fetchall()
if cols:
    for col in cols:
        print(f"  {col[0]:<30} {col[1]:<20} {'NULL' if col[2] == 'YES' else 'NOT NULL'}")
else:
    print("  Table does not exist")

cursor.close()
conn.close()
