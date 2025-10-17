#!/usr/bin/env python3
import psycopg2
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent.parent / '.env')

conn = psycopg2.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=os.getenv('POSTGRES_PORT'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    database=os.getenv('POSTGRES_DB')
)

cur = conn.cursor()

# Check all schemas that have these tables
cur.execute("""
    SELECT table_schema, table_name
    FROM information_schema.tables 
    WHERE table_name IN ('spells', 'powers', 'totems')
    ORDER BY table_schema, table_name
""")

print("Schema | Table")
print("-" * 40)
for row in cur.fetchall():
    schema, table = row
    cur.execute(f'SELECT COUNT(*) FROM {schema}.{table}')
    count = cur.fetchone()[0]
    print(f"{schema} | {table} | {count} rows")

conn.close()
