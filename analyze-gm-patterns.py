#!/usr/bin/env python3
"""
Analyze GM Style Patterns from Training Corpus
Extracts teaching methodology, common phrases, and rule interpretation patterns
"""

import os
import psycopg2
from dotenv import load_dotenv
from collections import Counter
import re

# Load environment variables
load_dotenv()

DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', '127.0.0.1'),
    'port': os.getenv('POSTGRES_PORT', '5434'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'database': os.getenv('POSTGRES_DB', 'postgres')
}

def analyze_teaching_style(conn):
    """Analyze teaching methodology from allTeachings category"""
    cursor = conn.cursor()
    
    print("\n📚 Teaching Style Analysis")
    print("="*60)
    
    # Get teaching examples
    cursor.execute('''
        SELECT text, word_count
        FROM training_corpus
        WHERE category = 'allTeachings'
        ORDER BY word_count DESC
        LIMIT 20
    ''')
    
    teachings = cursor.fetchall()
    
    # Common teaching phrases
    teaching_phrases = []
    for text, _ in teachings:
        # Extract key phrases
        if 'I' in text or 'you' in text:
            teaching_phrases.append(text[:200])
    
    print(f"\nTop Teaching Approaches ({len(teaching_phrases)} examples):")
    for i, phrase in enumerate(teaching_phrases[:5], 1):
        print(f"\n{i}. {phrase}...")
    
    return teachings

def analyze_rule_interpretations(conn):
    """Analyze how rules are interpreted and explained"""
    cursor = conn.cursor()
    
    print("\n\n⚖️  Rule Interpretation Patterns")
    print("="*60)
    
    # Get items with rule references
    cursor.execute('''
        SELECT category, COUNT(*) as count
        FROM training_corpus
        WHERE has_rule_reference = TRUE
        GROUP BY category
        ORDER BY count DESC
    ''')
    
    print("\nRule References by Category:")
    for category, count in cursor.fetchall():
        print(f"  {category:20} {count:4} references")
    
    # Get example rule explanations
    cursor.execute('''
        SELECT text, category
        FROM training_corpus
        WHERE has_rule_reference = TRUE
          AND has_example = TRUE
        LIMIT 10
    ''')
    
    print("\n\nSample Rule Explanations with Examples:")
    for i, (text, category) in enumerate(cursor.fetchall()[:3], 1):
        print(f"\n{i}. [{category}] {text[:150]}...")

def analyze_mechanical_examples(conn):
    """Analyze mechanical examples and dice notation usage"""
    cursor = conn.cursor()
    
    print("\n\n🎲 Mechanical Examples Analysis")
    print("="*60)
    
    # Get dice notation examples
    cursor.execute('''
        SELECT category, COUNT(*) as count
        FROM training_corpus
        WHERE has_dice_notation = TRUE
        GROUP BY category
        ORDER BY count DESC
    ''')
    
    print("\nDice Notation by Category:")
    for category, count in cursor.fetchall():
        print(f"  {category:20} {count:4} examples")
    
    # Sample mechanical examples
    cursor.execute('''
        SELECT text, category
        FROM training_corpus
        WHERE has_dice_notation = TRUE
        ORDER BY word_count DESC
        LIMIT 5
    ''')
    
    print("\n\nSample Mechanical Examples:")
    for i, (text, category) in enumerate(cursor.fetchall()[:3], 1):
        print(f"\n{i}. [{category}] {text[:200]}...")

def analyze_common_topics(conn):
    """Analyze most commonly discussed topics"""
    cursor = conn.cursor()
    
    print("\n\n📊 Common Topics Analysis")
    print("="*60)
    
    # Keywords to search for
    keywords = [
        'initiative', 'combat', 'damage', 'armor',
        'spell', 'magic', 'drain', 'force',
        'matrix', 'decker', 'IC', 'program',
        'skill', 'attribute', 'test', 'target number',
        'karma', 'character', 'creation', 'advancement'
    ]
    
    topic_counts = {}
    
    for keyword in keywords:
        cursor.execute('''
            SELECT COUNT(*)
            FROM training_corpus
            WHERE text ILIKE %s
        ''', (f'%{keyword}%',))
        
        count = cursor.fetchone()[0]
        if count > 0:
            topic_counts[keyword] = count
    
    print("\nMost Discussed Topics:")
    for topic, count in sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:15]:
        print(f"  {topic:20} {count:4} mentions")

def extract_house_rules(conn):
    """Extract potential house rules from session logs"""
    cursor = conn.cursor()
    
    print("\n\n🏠 Potential House Rules")
    print("="*60)
    
    # Look for teaching items that mention variations or house rules
    cursor.execute('''
        SELECT text, category
        FROM training_corpus
        WHERE text ILIKE '%house rule%'
           OR text ILIKE '%we use%'
           OR text ILIKE '%I rule%'
           OR text ILIKE '%variant%'
        LIMIT 10
    ''')
    
    results = cursor.fetchall()
    
    if results:
        print("\nFound potential house rules:")
        for i, (text, category) in enumerate(results[:5], 1):
            print(f"\n{i}. [{category}] {text[:200]}...")
    else:
        print("\nNo explicit house rules found in training corpus.")
        print("(House rules may be in session logs or campaign notes)")

def generate_gm_style_summary(conn):
    """Generate overall GM style summary"""
    cursor = conn.cursor()
    
    print("\n\n✨ GM Style Summary")
    print("="*60)
    
    # Get statistics
    cursor.execute('''
        SELECT 
            COUNT(*) as total,
            COUNT(*) FILTER (WHERE has_example) as with_examples,
            COUNT(*) FILTER (WHERE has_dice_notation) as with_dice,
            COUNT(*) FILTER (WHERE has_rule_reference) as with_refs,
            AVG(word_count) as avg_words
        FROM training_corpus
    ''')
    
    stats = cursor.fetchone()
    total, examples, dice, refs, avg_words = stats
    
    print(f"\nTeaching Characteristics:")
    print(f"  Total training items:     {total:5}")
    print(f"  Uses examples:            {examples:5} ({examples/total*100:.1f}%)")
    print(f"  Shows mechanics:          {dice:5} ({dice/total*100:.1f}%)")
    print(f"  Cites rules:              {refs:5} ({refs/total*100:.1f}%)")
    print(f"  Average explanation:      {avg_words:.0f} words")
    
    print("\n\nGM Style Profile:")
    
    if refs/total > 0.7:
        print("  ✅ Rule-focused: Frequently cites official rules")
    if examples/total > 0.05:
        print("  ✅ Example-driven: Uses practical demonstrations")
    if dice/total > 0.3:
        print("  ✅ Mechanics-oriented: Shows dice rolls and calculations")
    if avg_words > 50:
        print("  ✅ Detailed explanations: Thorough and comprehensive")
    
    # Category focus
    cursor.execute('''
        SELECT category, COUNT(*) as count
        FROM training_corpus
        GROUP BY category
        ORDER BY count DESC
        LIMIT 3
    ''')
    
    print("\n  Primary focus areas:")
    for category, count in cursor.fetchall():
        print(f"    • {category} ({count} items)")

def main():
    """Main analysis process"""
    print("🔍 GM Style Pattern Analysis")
    print("="*60)
    print(f"Database: PostgreSQL at {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print("="*60)
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("\n✅ Connected to PostgreSQL")
    except Exception as e:
        print(f"\n❌ Database connection failed: {e}")
        return
    
    # Run analyses
    analyze_teaching_style(conn)
    analyze_rule_interpretations(conn)
    analyze_mechanical_examples(conn)
    analyze_common_topics(conn)
    extract_house_rules(conn)
    generate_gm_style_summary(conn)
    
    conn.close()
    
    print("\n" + "="*60)
    print("✅ Analysis Complete!")
    print("="*60)

if __name__ == '__main__':
    main()
