#!/usr/bin/env python3
"""
Shadowrun GM Chunk Insertion Script
Loads chunks from JSON and inserts into database with embeddings
"""

import os
import json
import psycopg2
from openai import OpenAI
from typing import List
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Database configuration
DB_HOST = os.getenv('POSTGRES_HOST', 'localhost')
DB_PORT = os.getenv('POSTGRES_PORT', '5433')
DB_NAME = os.getenv('POSTGRES_DB', 'postgres')
DB_USER = os.getenv('POSTGRES_USER', 'postgres')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'postgres')

# OpenAI configuration
OPENAI_EMBED_MODEL = os.getenv('OPENAI_EMBED_MODEL', 'text-embedding-3-small')

class ChunkInserter:
    """Inserts chunks into database with embeddings"""
    
    def __init__(self):
        self.client = OpenAI()
        print(f"Using embeddings: {OPENAI_EMBED_MODEL}")
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text"""
        try:
            response = self.client.embeddings.create(
                model=OPENAI_EMBED_MODEL,
                input=text[:8000]  # Limit to 8000 chars
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"  Warning: Embedding generation failed: {e}")
            return [0.0] * 1536
    
    def insert_chunks(self, chunks: List[dict]):
        """Insert chunks into database"""
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        
        try:
            cur = conn.cursor()
            
            print(f"\nInserting {len(chunks)} chunks into database...")
            
            for i, chunk in enumerate(chunks, 1):
                # Generate embedding
                embedding = self.generate_embedding(chunk['content'])
                
                # Insert into rules_content table
                cur.execute("""
                    INSERT INTO rules_content 
                    (title, content, category, subcategory, tags, source_file, embedding)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    chunk['title'],
                    chunk['content'],
                    chunk['category'],
                    chunk['subcategory'],
                    chunk['tags'],
                    chunk['source_file'],
                    embedding
                ))
                
                if i % 10 == 0:
                    print(f"  Inserted {i}/{len(chunks)} chunks...")
            
            conn.commit()
            print(f"\n✓ Successfully inserted {len(chunks)} chunks")
            
            # Validate insertion
            print("\nValidating insertion...")
            cur.execute("SELECT COUNT(*) FROM rules_content")
            total_count = cur.fetchone()[0]
            print(f"  Total records in database: {total_count}")
            
            # Check by source file
            cur.execute("""
                SELECT source_file, COUNT(*) 
                FROM rules_content 
                GROUP BY source_file 
                ORDER BY source_file
            """)
            file_counts = cur.fetchall()
            print("\n  Records by source file:")
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
            print("\n  Records by category:")
            for category, count in category_counts:
                print(f"    {category}: {count} chunks")
            
            # Verify embeddings
            cur.execute("SELECT COUNT(*) FROM rules_content WHERE embedding IS NOT NULL")
            embedding_count = cur.fetchone()[0]
            print(f"\n  Chunks with embeddings: {embedding_count}/{total_count}")
            
            if embedding_count == total_count:
                print("  ✓ All chunks have embeddings")
            else:
                print(f"  ⚠️  Warning: {total_count - embedding_count} chunks missing embeddings")
            
        except Exception as e:
            conn.rollback()
            print(f"\n❌ Error inserting chunks: {e}")
            raise
        finally:
            cur.close()
            conn.close()


def main():
    """Main insertion process"""
    print("=" * 60)
    print("Shadowrun GM Chunk Insertion")
    print("=" * 60)
    
    # Load chunks from JSON
    input_file = "processed-chunks.json"
    
    if not os.path.exists(input_file):
        print(f"\n❌ Error: {input_file} not found")
        print("Please run 'python process-chunks.py' first to generate the chunks")
        return
    
    print(f"\nLoading chunks from {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    print(f"Loaded {len(chunks)} chunks")
    
    # Insert into database
    inserter = ChunkInserter()
    
    try:
        inserter.insert_chunks(chunks)
        print(f"\n{'=' * 60}")
        print("✓ Insertion completed successfully!")
        print(f"{'=' * 60}")
    except Exception as e:
        print(f"\n❌ Insertion failed: {e}")


if __name__ == "__main__":
    main()
