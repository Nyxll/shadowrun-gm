#!/usr/bin/env python3
"""
Show examples of duplicate chunks to verify they are truly duplicates
"""

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

print("=" * 70)
print("Duplicate Chunk Examples")
print("=" * 70)

# Get a few examples of duplicates
cur.execute("""
    SELECT source_file, title, content, COUNT(*) as count
    FROM rules_content
    GROUP BY source_file, title, content
    HAVING COUNT(*) > 1
    ORDER BY source_file
    LIMIT 3
""")

duplicates = cur.fetchall()

for i, (source, title, content, count) in enumerate(duplicates, 1):
    print(f"\n{'=' * 70}")
    print(f"Example {i}: {source}")
    print(f"Title: {title}")
    print(f"Copies: {count}")
    print("-" * 70)
    
    # Get the actual IDs of these duplicates
    cur.execute("""
        SELECT id, category, subcategory, content_type
        FROM rules_content
        WHERE source_file = %s AND title = %s AND content = %s
        ORDER BY id
    """, (source, title, content))
    
    copies = cur.fetchall()
    
    print(f"\nFound {len(copies)} identical copies:")
    for copy_id, category, subcategory, content_type in copies:
        print(f"  ID: {copy_id} | category: {category:20} | subcategory: {subcategory:20} | content_type: {content_type}")
    
    print(f"\nContent preview (first 300 chars):")
    print("-" * 70)
    print(content[:300] + "..." if len(content) > 300 else content)
    print("-" * 70)
    print(f"\nContent length: {len(content)} characters")
    print(f"Content hash: {hash(content)}")

print("\n" + "=" * 70)
print("Duplicate Detection Method")
print("=" * 70)
print("""
Duplicates are identified by matching ALL of these fields:
1. source_file - Same source file
2. title - Same section title
3. content - EXACT same content (character-for-character match)

If all three match, the chunks are considered duplicates.
Only the first occurrence (lowest ID) is kept, others are removed.
""")

conn.close()
