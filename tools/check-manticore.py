#!/usr/bin/env python3
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv
import os

load_dotenv()

conn = psycopg.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=int(os.getenv('POSTGRES_PORT')),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    dbname=os.getenv('POSTGRES_DB'),
    row_factory=dict_row
)

cur = conn.cursor()
cur.execute("""
    SELECT id, name, street_name 
    FROM characters 
    WHERE LOWER(name) LIKE '%manticore%' 
       OR LOWER(COALESCE(street_name, '')) LIKE '%manticore%'
       OR LOWER(name) LIKE '%edom%'
""")

results = cur.fetchall()
print(f"Found {len(results)} characters:")
for r in results:
    print(f"  ID: {r['id']}")
    print(f"  Name: {r['name']}")
    print(f"  Street Name: {r['street_name']}")
    print()

conn.close()
