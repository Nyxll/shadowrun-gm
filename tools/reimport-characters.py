#!/usr/bin/env python3
"""
Re-import characters with correct data
Deletes existing imports and re-imports with actual nuyen/karma values
"""

import psycopg
from dotenv import load_dotenv
import os

load_dotenv()

conn = psycopg.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=os.getenv('POSTGRES_PORT'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    dbname=os.getenv('POSTGRES_DB')
)

print("🗑️  Deleting existing character imports...")
cur = conn.cursor()
cur.execute("DELETE FROM characters")
deleted = cur.rowcount
conn.commit()
print(f"✅ Deleted {deleted} characters\n")

conn.close()

print("Now run: python tools/import-characters-v4.py")
print("This will re-import with enhanced parser (v4)")
