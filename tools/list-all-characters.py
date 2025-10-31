#!/usr/bin/env python3
"""
List all characters in the database
"""
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=os.getenv('POSTGRES_PORT'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    dbname=os.getenv('POSTGRES_DB')
)

cur = conn.cursor()

cur.execute("""
    SELECT street_name, base_essence, essence_hole
    FROM characters
    ORDER BY street_name
""")

print("Characters in database (by street name):")
print("=" * 60)
for street_name, base_ess, ess_hole in cur.fetchall():
    current_ess = (base_ess or 0) - (ess_hole or 0)
    print(f"{street_name}: base={base_ess}, hole={ess_hole}, current={current_ess}")

cur.close()
conn.close()
