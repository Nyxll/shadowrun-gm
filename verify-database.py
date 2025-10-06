#!/usr/bin/env python3
"""
Database Verification Script
Checks the current state of the rules_content table
"""

import os
import psycopg2
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Database configuration
DB_HOST = os.getenv('POSTGRES_HOST', 'localhost')
DB_PORT = os.getenv('POSTGRES_PORT', '5433')
DB_NAME = os.getenv('POSTGRES_DB', 'postgres')
DB_USER = os.getenv('POSTGRES_USER', 'postgres')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'postgres')

def verify_database():
    """Verify database state"""
    print("=" * 60)
    print("Database Verification")
    print("=" * 60)
    
    try:
        # Connect to database
        print(f"\nConnecting to database...")
        print(f"  Host: {DB_HOST}")
        print(f"  Port: {DB_PORT}")
        print(f"  Database: {DB_NAME}")
        
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        
        cur = conn.cursor()
        print("  ✓ Connected successfully")
        
        # Check if table exists
        print("\nChecking if rules_content table exists...")
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'rules_content'
            )
        """)
        table_exists = cur.fetchone()[0]
        
        if not table_exists:
            print("  ❌ Table 'rules_content' does not exist!")
            print("\nPlease run the schema.sql file first to create the table:")
            print("  psql -h localhost -p 5433 -U postgres -d postgres -f schema.sql")
            return
        
        print("  ✓ Table exists")
        
        # Get total count
        print("\nTotal Records:")
        cur.execute("SELECT COUNT(*) FROM rules_content")
        total_count = cur.fetchone()[0]
        print(f"  {total_count} chunks in database")
        
        if total_count == 0:
            print("\n  ⚠️  Database is empty - no chunks have been inserted yet")
            return
        
        # Check by source file
        print("\nRecords by Source File:")
        cur.execute("""
            SELECT source_file, COUNT(*) 
            FROM rules_content 
            GROUP BY source_file 
            ORDER BY source_file
        """)
        file_counts = cur.fetchall()
        for source_file, count in file_counts:
            print(f"  {source_file}: {count} chunks")
        
        # Check by category
        print("\nRecords by Category:")
        cur.execute("""
            SELECT category, COUNT(*) 
            FROM rules_content 
            GROUP BY category 
            ORDER BY COUNT(*) DESC
        """)
        category_counts = cur.fetchall()
        for category, count in category_counts:
            print(f"  {category}: {count} chunks")
        
        # Verify embeddings
        print("\nEmbedding Status:")
        cur.execute("SELECT COUNT(*) FROM rules_content WHERE embedding IS NOT NULL")
        embedding_count = cur.fetchone()[0]
        print(f"  Chunks with embeddings: {embedding_count}/{total_count}")
        
        if embedding_count == total_count:
            print("  ✓ All chunks have embeddings")
        else:
            missing = total_count - embedding_count
            print(f"  ⚠️  Warning: {missing} chunks missing embeddings")
        
        # Sample some content
        print("\nSample Records:")
        cur.execute("""
            SELECT title, category, LENGTH(content) as content_length
            FROM rules_content 
            ORDER BY id 
            LIMIT 5
        """)
        samples = cur.fetchall()
        for title, category, length in samples:
            print(f"  '{title}' ({category}): {length} chars")
        
        print(f"\n{'=' * 60}")
        print("Verification Complete")
        print(f"{'=' * 60}")
        
        cur.close()
        conn.close()
        
    except psycopg2.OperationalError as e:
        print(f"\n❌ Database connection error: {e}")
        print("\nPlease check:")
        print("  1. Docker container is running")
        print("  2. Database credentials in .env are correct")
        print("  3. Port 5433 is accessible")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    verify_database()
