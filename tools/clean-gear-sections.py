#!/usr/bin/env python3
"""Remove section headers from character_gear table"""
import os
from dotenv import load_dotenv
import psycopg

load_dotenv()

conn = psycopg.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=os.getenv('POSTGRES_PORT'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    dbname=os.getenv('POSTGRES_DB')
)

cur = conn.cursor()

try:
    # Find all gear items that end with ':'
    cur.execute("""
        SELECT id, character_id, gear_name
        FROM character_gear
        WHERE gear_name LIKE '%:'
        ORDER BY gear_name
    """)
    
    section_headers = cur.fetchall()
    
    if not section_headers:
        print("No section headers found in gear table.")
    else:
        print(f"Found {len(section_headers)} section headers to remove:")
        print("=" * 60)
        
        for item_id, char_id, gear_name in section_headers:
            print(f"  - {gear_name}")
        
        print("\nRemoving section headers...")
        
        # Delete all gear items ending with ':'
        cur.execute("""
            DELETE FROM character_gear
            WHERE gear_name LIKE '%:'
        """)
        
        deleted_count = cur.rowcount
        conn.commit()
        
        print(f"\n✓ Removed {deleted_count} section headers from gear table")

except Exception as e:
    conn.rollback()
    print(f"✗ Error: {e}")
    raise

finally:
    cur.close()
    conn.close()
