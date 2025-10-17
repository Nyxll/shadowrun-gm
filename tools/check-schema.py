#!/usr/bin/env python3
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('POSTGRES_HOST', '127.0.0.1'),
    port=os.getenv('POSTGRES_PORT', '5434'),
    database=os.getenv('POSTGRES_DB', 'postgres'),
    user=os.getenv('POSTGRES_USER', 'postgres'),
    password=os.getenv('POSTGRES_PASSWORD', 'postgres')
)

cur = conn.cursor()

print("rules_content table schema:")
print("=" * 60)
cur.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'rules_content' 
    ORDER BY ordinal_position
""")
for row in cur.fetchall():
    print(f"{row[0]:30} {row[1]}")

print("\n" + "=" * 60)
print("\nSample record:")
cur.execute("SELECT * FROM rules_content LIMIT 1")
columns = [desc[0] for desc in cur.description]
row = cur.fetchone()
if row:
    for col, val in zip(columns, row):
        if col == 'embedding':
            print(f"{col:30} [vector with {len(val) if val else 0} dimensions]")
        elif col == 'tags':
            print(f"{col:30} {val}")
        else:
            val_str = str(val)[:100] if val else 'NULL'
            print(f"{col:30} {val_str}")

cur.close()
conn.close()
