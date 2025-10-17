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

# Check Fields of Fire gear chunks
print("Fields of Fire Gear Chunks:")
print("=" * 60)
cur.execute("""
    SELECT title, LEFT(content, 150) 
    FROM rules_content 
    WHERE source_file = 'FieldsofFire-gear-ocr.txt' 
    ORDER BY title
""")

for row in cur.fetchall():
    print(f"\nTitle: {row[0]}")
    print(f"Content: {row[1]}...")

# Search for Barrett specifically
print("\n\n" + "=" * 60)
print("Searching for 'Barrett' or 'Barret':")
print("=" * 60)
cur.execute("""
    SELECT title, content, source_file
    FROM rules_content 
    WHERE content ILIKE '%barret%' OR title ILIKE '%barret%'
""")

results = cur.fetchall()
if results:
    for row in results:
        print(f"\nTitle: {row[0]}")
        print(f"Source: {row[2]}")
        print(f"Content: {row[1][:200]}...")
else:
    print("No results found for 'Barrett' or 'Barret'")

conn.close()
