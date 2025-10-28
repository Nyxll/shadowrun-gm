#!/usr/bin/env python3
"""Check for orphaned modifiers in database"""
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

cur = conn.cursor()

# Find modifiers that look like they should be children but aren't
cur.execute("""
    SELECT id, source, source_type, modifier_type, parent_modifier_id, character_id
    FROM character_modifiers
    WHERE source LIKE '%for calculations%' 
       OR source LIKE '%for technical%' 
       OR source LIKE '%social dice%'
       OR source LIKE '%die with%'
    ORDER BY character_id, source
""")

rows = cur.fetchall()

print("Orphaned modifiers that should be children:")
print("=" * 70)
for r in rows:
    print(f"ID: {r['id']}")
    print(f"  Source: {r['source']}")
    print(f"  Type: {r['source_type']}")
    print(f"  Modifier Type: {r['modifier_type']}")
    print(f"  Parent ID: {r['parent_modifier_id']}")
    print()

conn.close()
