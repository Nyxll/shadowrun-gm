#!/usr/bin/env python3
"""
Enable pg_trgm extension for fuzzy text matching
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

print("Enabling pg_trgm extension for fuzzy text matching...")

try:
    cur.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
    conn.commit()
    print("✓ pg_trgm extension enabled")
except Exception as e:
    print(f"✗ Error: {e}")
    conn.rollback()

# Verify it's enabled
cur.execute("SELECT * FROM pg_extension WHERE extname = 'pg_trgm';")
result = cur.fetchone()

if result:
    print(f"✓ Verified: pg_trgm extension is active (OID: {result[0]})")
else:
    print("✗ pg_trgm extension not found")

cur.close()
conn.close()
