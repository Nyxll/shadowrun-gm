#!/usr/bin/env python3
"""
Apply character_powers UUID migration
"""
import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

conn = psycopg.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=int(os.getenv('POSTGRES_PORT')),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    dbname=os.getenv('POSTGRES_DB')
)

print("Applying character_powers UUID migration...")

with open('migrations/020_fix_character_powers_uuid.sql', 'r') as f:
    migration_sql = f.read()

cursor = conn.cursor()
cursor.execute(migration_sql)
conn.commit()

print("Migration applied successfully!")

# Verify the change
cursor.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'character_powers' 
    AND column_name = 'character_id'
""")

result = cursor.fetchone()
if result:
    print(f"✓ character_powers.character_id is now: {result[1]}")
else:
    print("✗ character_powers table not found or column missing")

cursor.close()
conn.close()
