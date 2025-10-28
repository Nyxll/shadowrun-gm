#!/usr/bin/env python3
"""Check character_modifiers table columns"""
import os
from dotenv import load_dotenv
import psycopg

load_dotenv()

conn = psycopg.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=os.getenv('POSTGRES_PORT'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    dbname=os.getenv('POSTGRES_DB')
)

cur = conn.cursor()
cur.execute("""
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns 
    WHERE table_name='character_modifiers' 
    ORDER BY ordinal_position
""")

print("character_modifiers table columns:")
print("=" * 80)
for row in cur.fetchall():
    nullable = "NULL" if row[2] == "YES" else "NOT NULL"
    print(f"{row[0]:<30} {row[1]:<20} {nullable}")

cur.close()
conn.close()
