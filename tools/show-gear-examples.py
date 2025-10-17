#!/usr/bin/env python3
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('POSTGRES_HOST', 'localhost'),
    port=int(os.getenv('POSTGRES_PORT', '5432')),
    user=os.getenv('POSTGRES_USER', 'postgres'),
    password=os.getenv('POSTGRES_PASSWORD'),
    database=os.getenv('POSTGRES_DB', 'postgres')
)

cur = conn.cursor()

# Show a few complete gear chunks as examples
print("=" * 80)
print("EXAMPLE GEAR CHUNKS (showing complete content)")
print("=" * 80)

examples = [
    'BARRET MODEL 121 HEAVY SNIPER RIFLE',
    'WALTHER PB-120',
    'COLT COBRA',
    'ARES ALPHA COMBAT GUN'
]

for title in examples:
    cur.execute("""
        SELECT title, category, content_type, content
        FROM rules_content 
        WHERE title = %s
    """, (title,))
    
    row = cur.fetchone()
    if row:
        print(f"\n{'=' * 80}")
        print(f"Title: {row[0]}")
        print(f"Category: {row[1]}")
        print(f"Content Type: {row[2]}")
        print(f"{'=' * 80}")
        print(row[3])
        print()

# Count total gear items across all sources
print("\n" + "=" * 80)
print("TOTAL GEAR ITEMS BY SOURCE")
print("=" * 80)

cur.execute("""
    SELECT source_file, COUNT(*) as count
    FROM rules_content 
    WHERE category IN ('gear', 'gear_mechanics')
    GROUP BY source_file
    ORDER BY count DESC
""")

total = 0
for row in cur.fetchall():
    print(f"{row[0]}: {row[1]} items")
    total += row[1]

print(f"\nTotal gear items: {total}")

conn.close()
