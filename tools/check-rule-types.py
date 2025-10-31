#!/usr/bin/env python3
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

# Get check constraint definition
cur.execute("""
    SELECT conname, pg_get_constraintdef(c.oid) 
    FROM pg_constraint c
    WHERE conrelid = 'house_rules'::regclass AND contype = 'c'
""")
print("Check constraints:")
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]}")

# Also check existing rule_type values
cur.execute("SELECT DISTINCT rule_type FROM house_rules")
print("\nExisting rule_type values:")
for row in cur.fetchall():
    print(f"  - {row[0]}")
