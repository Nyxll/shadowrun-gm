#!/usr/bin/env python3
"""
Check for duplicate gear items in the database
"""

import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
db_config = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', 5432)),
    'database': os.getenv('POSTGRES_DB', 'postgres'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', '')
}

def check_duplicates():
    """Check for duplicate gear items"""
    conn = psycopg2.connect(**db_config)
    
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            # Find duplicates by name and category
            cur.execute("""
                SELECT 
                    name,
                    category,
                    COUNT(*) as count,
                    ARRAY_AGG(id ORDER BY id) as ids,
                    ARRAY_AGG(source_file ORDER BY id) as sources,
                    ARRAY_AGG(data_quality ORDER BY id) as qualities
                FROM gear
                GROUP BY name, category
                HAVING COUNT(*) > 1
                ORDER BY COUNT(*) DESC, name
            """)
            
            duplicates = cur.fetchall()
            
            if duplicates:
                print("=" * 70)
                print(f"Found {len(duplicates)} duplicate gear items:")
                print("=" * 70)
                
                for dup in duplicates:
                    print(f"\n{dup['name']} ({dup['category']})")
                    print(f"  Copies: {dup['count']}")
                    for i, (id, source, quality) in enumerate(zip(dup['ids'], dup['sources'], dup['qualities'])):
                        print(f"  [{i+1}] ID: {id} | Source: {source} | Quality: {quality}")
                
                print("\n" + "=" * 70)
                print(f"Total duplicate items: {len(duplicates)}")
                print(f"Total duplicate records: {sum(d['count'] - 1 for d in duplicates)}")
                print("=" * 70)
            else:
                print("=" * 70)
                print("✓ No duplicate gear items found!")
                print("=" * 70)
            
            # Show total gear count
            cur.execute("SELECT COUNT(*) as total FROM gear")
            total = cur.fetchone()['total']
            print(f"\nTotal gear items in database: {total}")
            
            # Show breakdown by category
            cur.execute("""
                SELECT category, COUNT(*) as count
                FROM gear
                GROUP BY category
                ORDER BY count DESC
            """)
            
            categories = cur.fetchall()
            print("\nGear by category:")
            for cat in categories:
                print(f"  {cat['category']}: {cat['count']}")
            
    finally:
        conn.close()

def remove_duplicates():
    """Remove duplicate gear items, keeping the highest quality version"""
    conn = psycopg2.connect(**db_config)
    
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            # Find duplicates
            cur.execute("""
                SELECT 
                    name,
                    category,
                    ARRAY_AGG(id ORDER BY data_quality DESC, id ASC) as ids
                FROM gear
                GROUP BY name, category
                HAVING COUNT(*) > 1
            """)
            
            duplicates = cur.fetchall()
            
            if not duplicates:
                print("No duplicates to remove.")
                return
            
            removed = 0
            for dup in duplicates:
                # Keep first ID (highest quality), remove rest
                keep_id = dup['ids'][0]
                remove_ids = dup['ids'][1:]
                
                for remove_id in remove_ids:
                    cur.execute("DELETE FROM gear WHERE id = %s", (remove_id,))
                    removed += 1
                    print(f"Removed duplicate: {dup['name']} (ID: {remove_id})")
            
            conn.commit()
            
            print("\n" + "=" * 70)
            print(f"Removed {removed} duplicate records")
            print("=" * 70)
            
    finally:
        conn.close()

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--remove':
        print("Removing duplicates...")
        remove_duplicates()
    else:
        check_duplicates()
        print("\nTo remove duplicates, run: python check-gear-duplicates.py --remove")
