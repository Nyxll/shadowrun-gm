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

# Get gear chunks from Fields of Fire
print("=" * 80)
print("FIELDS OF FIRE GEAR CHUNKS")
print("=" * 80)
cur.execute("""
    SELECT title, category, content_type, LEFT(content, 200) as preview
    FROM rules_content 
    WHERE source_file = 'FieldsofFire-gear-ocr.txt'
    ORDER BY title
""")

count = 0
for row in cur.fetchall():
    count += 1
    print(f"\n{count}. Title: {row[0]}")
    print(f"   Category: {row[1]}")
    print(f"   Type: {row[2]}")
    print(f"   Preview: {row[3]}...")

print(f"\n\nTotal Fields of Fire gear chunks: {count}")

# Check if multiple gear items are in single chunks
print("\n" + "=" * 80)
print("CHECKING FOR MULTIPLE ITEMS IN SINGLE CHUNKS")
print("=" * 80)

cur.execute("""
    SELECT title, content
    FROM rules_content 
    WHERE source_file = 'FieldsofFire-gear-ocr.txt'
    AND content_type = 'stat_block'
""")

for row in cur.fetchall():
    # Count how many "##" headers are in the content (each gear item should have one)
    header_count = row[1].count('##')
    if header_count > 1:
        print(f"\n⚠️  MULTIPLE ITEMS FOUND: {row[0]}")
        print(f"   Contains {header_count} items")
        # Show the headers
        lines = row[1].split('\n')
        headers = [line for line in lines if line.startswith('##')]
        for h in headers[:5]:  # Show first 5
            print(f"   - {h}")

conn.close()
