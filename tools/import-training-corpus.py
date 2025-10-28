#!/usr/bin/env python3
"""
Import Training Corpus from Roleplay Logs
Imports GM teaching examples and rule explanations into the database
"""

import os
import json
import psycopg2
from dotenv import load_dotenv
from datetime import datetime
from typing import Dict, List

# Load environment variables
load_dotenv()

# PostgreSQL connection from .env
DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', '127.0.0.1'),
    'port': os.getenv('POSTGRES_PORT', '5434'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'database': os.getenv('POSTGRES_DB', 'postgres')
}

# Data path
TRAINING_FILE = 'parsed-roleplay-data/training-examples.json'

def create_training_corpus_table(conn):
    """Create training_corpus table if it doesn't exist"""
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS training_corpus (
                id SERIAL PRIMARY KEY,
                text TEXT NOT NULL,
                category VARCHAR(50) NOT NULL,
                source VARCHAR(100),
                word_count INTEGER,
                has_example BOOLEAN DEFAULT FALSE,
                has_dice_notation BOOLEAN DEFAULT FALSE,
                has_rule_reference BOOLEAN DEFAULT FALSE,
                metadata JSONB DEFAULT '{}',
                created_at TIMESTAMP DEFAULT NOW()
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_training_corpus_category 
            ON training_corpus(category)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_training_corpus_has_example 
            ON training_corpus(has_example) WHERE has_example = TRUE
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_training_corpus_text_search 
            ON training_corpus USING gin(to_tsvector('english', text))
        ''')
        
        conn.commit()
        print("✅ Training corpus table ready")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error creating training_corpus table: {e}")
        raise

def import_training_items(conn, category: str, items: List[Dict]) -> int:
    """Import training items for a specific category"""
    cursor = conn.cursor()
    imported = 0
    
    for item in items:
        try:
            cursor.execute('''
                INSERT INTO training_corpus (
                    text, category, source, word_count,
                    has_example, has_dice_notation, has_rule_reference,
                    metadata, created_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s
                )
            ''', (
                item.get('text'),
                category,
                item.get('source'),
                item.get('wordCount', 0),
                item.get('hasExample', False),
                item.get('hasDiceNotation', False),
                item.get('hasRuleReference', False),
                json.dumps({
                    'type': item.get('type'),
                    'original_category': category
                }),
                datetime.now()
            ))
            imported += 1
            
        except Exception as e:
            print(f"  ⚠️  Error importing item: {e}")
            continue
    
    conn.commit()
    return imported

def main():
    """Main import process"""
    print("📚 Training Corpus Import Tool")
    print("="*60)
    print(f"Database: PostgreSQL at {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print("="*60)
    
    # Load training data
    print(f"\n📂 Loading training data from {TRAINING_FILE}...")
    try:
        with open(TRAINING_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ Loaded {len(data)} categories")
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return
    
    # Connect to database
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("\n✅ Connected to PostgreSQL")
    except Exception as e:
        print(f"\n❌ Database connection failed: {e}")
        return
    
    # Create table
    print("\n📋 Setting up training corpus table...")
    create_training_corpus_table(conn)
    
    # Import each category
    print(f"\n📥 Importing training corpus...")
    total_imported = 0
    
    for category, items in data.items():
        if isinstance(items, list):
            print(f"\n  {category}:")
            print(f"    Items to import: {len(items)}")
            
            imported = import_training_items(conn, category, items)
            total_imported += imported
            
            print(f"    ✅ Imported: {imported}")
    
    # Show statistics
    cursor = conn.cursor()
    
    print(f"\n📊 Import Statistics:")
    print("-"*60)
    
    cursor.execute('''
        SELECT category, COUNT(*) as count
        FROM training_corpus
        GROUP BY category
        ORDER BY count DESC
    ''')
    
    for row in cursor.fetchall():
        category, count = row
        print(f"  {category:20} {count:5} items")
    
    print()
    cursor.execute('''
        SELECT 
            COUNT(*) FILTER (WHERE has_example) as with_examples,
            COUNT(*) FILTER (WHERE has_dice_notation) as with_dice,
            COUNT(*) FILTER (WHERE has_rule_reference) as with_refs,
            COUNT(*) as total
        FROM training_corpus
    ''')
    
    stats = cursor.fetchone()
    print(f"  With examples:        {stats[0]:5}")
    print(f"  With dice notation:   {stats[1]:5}")
    print(f"  With rule references: {stats[2]:5}")
    print(f"  Total:                {stats[3]:5}")
    
    conn.close()
    
    print("\n" + "="*60)
    print(f"✅ Import Complete! Imported {total_imported} training items")
    print("="*60)

if __name__ == '__main__':
    main()
