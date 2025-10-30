#!/usr/bin/env python3
import os
from dotenv import load_dotenv
import psycopg

load_dotenv()

conn = psycopg.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=os.getenv('POSTGRES_PORT'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    dbname=os.getenv('POSTGRES_DB')
)

cursor = conn.cursor()

print("character_modifiers table structure:")
cursor.execute("""
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns 
    WHERE table_name = 'character_modifiers' 
    ORDER BY ordinal_position
""")

for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]} (nullable: {row[2]})")

print("\nSample modifiers:")
cursor.execute("""
    SELECT id, character_id, modifier_name, source_type, modifier_type, modifier_data
    FROM character_modifiers
    LIMIT 3
""")

for row in cursor.fetchall():
    print(f"\n  ID: {row[0]}")
    print(f"  Character: {row[1]}")
    print(f"  Name: {row[2]}")
    print(f"  Source: {row[3]}")
    print(f"  Type: {row[4]}")
    print(f"  Data: {row[5]}")

conn.close()
