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

# Get total count
cur.execute('SELECT COUNT(*) FROM rules_content')
total = cur.fetchone()[0]

# Get content_type distribution
cur.execute('''
    SELECT content_type, COUNT(*) 
    FROM rules_content 
    GROUP BY content_type 
    ORDER BY COUNT(*) DESC
''')

print(f"\nContent Type Distribution (All {total} chunks):")
print("=" * 70)

for ct, count in cur.fetchall():
    ct_display = ct if ct else 'NULL'
    percentage = count / total * 100
    print(f"{ct_display:25} {count:5} chunks ({percentage:5.1f}%)")

# Check for NULLs
cur.execute('SELECT COUNT(*) FROM rules_content WHERE content_type IS NULL')
null_count = cur.fetchone()[0]

print("=" * 70)
print(f"\nChunks with NULL content_type: {null_count}")

if null_count == 0:
    print("✅ All chunks have content_type!")
else:
    print(f"⚠️  {null_count} chunks missing content_type")

conn.close()
