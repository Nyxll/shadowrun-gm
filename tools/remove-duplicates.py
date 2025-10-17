#!/usr/bin/env python3
"""
Remove duplicate chunks from the database
Keeps the first occurrence of each unique chunk based on source_file, title, and content
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
print("Removing Duplicate Chunks")
print("=" * 70)

# First, let's see how many duplicates we have
cur.execute("""
    SELECT source_file, title, content, COUNT(*) as count
    FROM rules_content
    GROUP BY source_file, title, content
    HAVING COUNT(*) > 1
    ORDER BY COUNT(*) DESC, source_file
""")

duplicates = cur.fetchall()

if not duplicates:
    print("\n✓ No duplicates found!")
    conn.close()
    exit(0)

print(f"\nFound {len(duplicates)} sets of duplicate chunks:")
print("-" * 70)

total_to_delete = 0
for source, title, content, count in duplicates[:10]:  # Show first 10
    content_preview = content[:50].replace('\n', ' ') + "..."
    print(f"{source:30} | {title[:20]:20} | {count} copies")
    total_to_delete += (count - 1)

if len(duplicates) > 10:
    print(f"... and {len(duplicates) - 10} more sets of duplicates")

print("-" * 70)
print(f"\nTotal duplicate chunks to remove: {total_to_delete}")

# Get current total
cur.execute("SELECT COUNT(*) FROM rules_content")
current_total = cur.fetchone()[0]
print(f"Current total chunks: {current_total}")
print(f"After cleanup: {current_total - total_to_delete}")

# Ask for confirmation
print("\nThis will keep the first occurrence of each duplicate and remove the rest.")
response = input("Proceed with deletion? (yes/no): ")
if response.lower() != 'yes':
    print("Cancelled.")
    conn.close()
    exit(0)

# Delete duplicates, keeping only the first occurrence (lowest id)
print("\nDeleting duplicates...")

cur.execute("""
    DELETE FROM rules_content
    WHERE id IN (
        SELECT id
        FROM (
            SELECT id,
                   ROW_NUMBER() OVER (
                       PARTITION BY source_file, title, content
                       ORDER BY id
                   ) as row_num
            FROM rules_content
        ) t
        WHERE row_num > 1
    )
""")

deleted_count = cur.rowcount
conn.commit()

print(f"✓ Deleted {deleted_count} duplicate chunks")

# Verify final count
cur.execute("SELECT COUNT(*) FROM rules_content")
final_total = cur.fetchone()[0]

print(f"\nFinal total chunks: {final_total}")
print(f"Expected: {current_total - total_to_delete}")

if final_total == current_total - total_to_delete:
    print("✓ Counts match!")
else:
    print("⚠️  Warning: Count mismatch!")

# Show updated file counts
print("\n" + "=" * 70)
print("Updated File Counts")
print("=" * 70)

cur.execute("""
    SELECT source_file, COUNT(*) as chunk_count 
    FROM rules_content 
    GROUP BY source_file 
    ORDER BY source_file
""")

for source, count in cur.fetchall():
    print(f"{source:50} {count:5} chunks")

conn.close()

print("\n" + "=" * 70)
print("✓ Cleanup complete!")
print("=" * 70)
