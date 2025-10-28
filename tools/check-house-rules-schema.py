#!/usr/bin/env python3
"""Check house_rules table schema"""
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

cursor.execute("""
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns 
    WHERE table_name = 'house_rules' 
    ORDER BY ordinal_position
""")

print('\nhouse_rules table columns:')
print('='*80)
for r in cursor.fetchall():
    print(f"  {r['column_name']:30s} {r['data_type']:20s} nullable: {r['is_nullable']}")

conn.close()
