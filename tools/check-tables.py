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

# List all tables
print("All tables in database:")
cur.execute("SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename")
for table in cur.fetchall():
    print(f"  - {table[0]}")

# Check rules_content table (where chunks are stored)
print("\nChecking rules_content table:")
cur.execute("""
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_name = 'rules_content'
    )
""")
if cur.fetchone()[0]:
    cur.execute("SELECT COUNT(*) FROM rules_content")
    total_count = cur.fetchone()[0]
    print(f"  Total chunks: {total_count}")
    
    if total_count > 0:
        # Check by source file
        cur.execute("""
            SELECT source_file, COUNT(*) 
            FROM rules_content 
            GROUP BY source_file 
            ORDER BY source_file
        """)
        file_counts = cur.fetchall()
        print("\n  Chunks by source file:")
        for source_file, count in file_counts:
            print(f"    {source_file}: {count} chunks")
        
        # Check by category
        cur.execute("""
            SELECT category, COUNT(*) 
            FROM rules_content 
            GROUP BY category 
            ORDER BY COUNT(*) DESC
        """)
        category_counts = cur.fetchall()
        print("\n  Chunks by category:")
        for category, count in category_counts:
            print(f"    {category}: {count} chunks")
        
        # Verify embeddings
        cur.execute("SELECT COUNT(*) FROM rules_content WHERE embedding IS NOT NULL")
        embedding_count = cur.fetchone()[0]
        print(f"\n  Chunks with embeddings: {embedding_count}/{total_count}")
else:
    print("  Table does not exist")

# Also check document_metadata if it exists
print("\nChecking document_metadata table:")
cur.execute("""
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_name = 'document_metadata'
    )
""")
if cur.fetchone()[0]:
    cur.execute("SELECT COUNT(*) FROM document_metadata")
    count = cur.fetchone()[0]
    print(f"  Found {count} records")
    
    if count > 0:
        cur.execute("SELECT title, created_at FROM document_metadata ORDER BY created_at")
        print("\n  Documents in document_metadata:")
        for row in cur.fetchall():
            print(f"    {row[0]} (added {row[1]})")
else:
    print("  Table does not exist")

cur.close()
conn.close()
