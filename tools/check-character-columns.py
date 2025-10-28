#!/usr/bin/env python3
"""Check what columns exist in the characters table"""
import os
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row

load_dotenv()

conn = psycopg.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=os.getenv('POSTGRES_PORT'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    dbname=os.getenv('POSTGRES_DB'),
    row_factory=dict_row
)
cursor = conn.cursor()

# Get column information
cursor.execute("""
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns
    WHERE table_name = 'characters'
    ORDER BY ordinal_position
""")

print("Characters table columns:")
print("=" * 80)
for row in cursor.fetchall():
    nullable = "NULL" if row['is_nullable'] == 'YES' else "NOT NULL"
    print(f"{row['column_name']:30s} {row['data_type']:20s} {nullable}")

# Get a sample character to see actual data
cursor.execute("""
    SELECT * FROM characters WHERE street_name = 'Platinum' LIMIT 1
""")

char = cursor.fetchone()
if char:
    print("\n" + "=" * 80)
    print("Sample character (Platinum) fields:")
    print("=" * 80)
    for key, value in char.items():
        value_str = str(value)[:100] if value else "NULL"
        print(f"{key:30s}: {value_str}")

conn.close()
