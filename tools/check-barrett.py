#!/usr/bin/env python3
"""Check Block's character data in database"""
import os
import json
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
cur.execute("""
    SELECT name, street_name, nuyen, karma_pool, karma_total, attributes, relationships
    FROM characters 
    WHERE name LIKE '%Block%' OR street_name LIKE '%Block%'
""")

char = cur.fetchone()
if char:
    print("Block's Database Record:")
    print("=" * 60)
    print(f"Name: {char['name']}")
    print(f"Street Name: {char['street_name']}")
    print(f"Nuyen (column): {char['nuyen']}")
    print(f"Karma Pool (column): {char['karma_pool']}")
    print(f"Karma Total (column): {char['karma_total']}")
    print(f"\nAttributes JSONB:")
    print(json.dumps(char['attributes'], indent=2))
    print(f"\nRelationships JSONB:")
    print(json.dumps(char['relationships'], indent=2))
else:
    print("Block not found!")

conn.close()
