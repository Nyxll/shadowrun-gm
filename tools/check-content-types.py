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

print("Content Distribution by Category and Type:")
print("=" * 70)

cur.execute("""
    SELECT category, content_type, COUNT(*) 
    FROM rules_content 
    GROUP BY category, content_type 
    ORDER BY category, COUNT(*) DESC
""")

current_category = None
for row in cur.fetchall():
    category, content_type, count = row
    if category != current_category:
        if current_category is not None:
            print()
        current_category = category
        print(f"\n{category.upper()}:")
    print(f"  {content_type:25} {count:5} chunks")

print("\n" + "=" * 70)

# Check for any quality metrics
print("\nChecking for quality/performance tables...")
cur.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_name LIKE '%quality%' OR table_name LIKE '%performance%' OR table_name LIKE '%log%'
    ORDER BY table_name
""")
tables = cur.fetchall()
if tables:
    print("Found these related tables:")
    for table in tables:
        print(f"  - {table[0]}")
else:
    print("  No quality/performance tracking tables found")

cur.close()
conn.close()
