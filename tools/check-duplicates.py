#!/usr/bin/env python3
"""
Check for duplicate chunks in the database
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
print("Checking for Duplicate Chunks")
print("=" * 70)

# Find duplicates based on source_file, title, and content
cur.execute("""
    SELECT source_file, title, COUNT(*) as count
    FROM rules_content
    GROUP BY source_file, title, content
    HAVING COUNT(*) > 1
    ORDER BY source_file, COUNT(*) DESC
""")

duplicates = cur.fetchall()

if not duplicates:
    print("\n✓ No duplicates found!")
    print("All chunks are unique.")
else:
    print(f"\n⚠️  Found {len(duplicates)} sets of duplicate chunks:\n")
    
    # Group by source file
    by_file = {}
    total_dupes = 0
    for source, title, count in duplicates:
        if source not in by_file:
            by_file[source] = []
        by_file[source].append((title, count))
        total_dupes += (count - 1)
    
    for source in sorted(by_file.keys()):
        dupes = by_file[source]
        file_total = sum(count - 1 for _, count in dupes)
        print(f"{source}: {file_total} duplicate chunks")
        for title, count in dupes[:5]:  # Show first 5
            title_short = title[:40] + "..." if len(title) > 40 else title
            print(f"  - {title_short}: {count} copies")
        if len(dupes) > 5:
            print(f"  ... and {len(dupes) - 5} more")
        print()
    
    print("-" * 70)
    print(f"Total duplicate chunks to remove: {total_dupes}")

# Get current total
cur.execute("SELECT COUNT(*) FROM rules_content")
current_total = cur.fetchone()[0]
print(f"\nCurrent total chunks: {current_total}")

if duplicates:
    print(f"After cleanup: {current_total - total_dupes}")

conn.close()
