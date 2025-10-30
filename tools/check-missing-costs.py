#!/usr/bin/env python3
"""
Check which cyberware/bioware items are missing essence_cost or body_index_cost
"""
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

def main():
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB')
    )
    
    cur = conn.cursor()
    
    # Get all characters with cyberware/bioware
    cur.execute("""
        SELECT DISTINCT c.id, c.name 
        FROM characters c
        JOIN character_modifiers cm ON c.id = cm.character_id
        WHERE cm.source_type IN ('cyberware', 'bioware')
        AND cm.deleted_at IS NULL
        ORDER BY c.name
    """)
    characters = cur.fetchall()
    
    if not characters:
        print("No characters found with cyberware/bioware!")
        cur.close()
        conn.close()
        return
    
    print(f"Found {len(characters)} character(s) with cyberware/bioware:")
    for char_id, char_name in characters:
        print(f"  - {char_name}")
    print()
    
    # Check each character
    for char_id, char_name in characters:
        print("\n" + "=" * 80)
        print(f"CHARACTER: {char_name}")
        print("=" * 80)
    
        print("\nCYBERWARE ITEMS (checking essence_cost)")
        print("-" * 80)
    
        cur.execute("""
            SELECT source, essence_cost, modifier_data
            FROM character_modifiers
            WHERE character_id = %s 
            AND source_type = 'cyberware'
            AND deleted_at IS NULL
            GROUP BY source, essence_cost, modifier_data
            ORDER BY source
        """, (char_id,))
        
        cyberware = cur.fetchall()
        if not cyberware:
            print("  No cyberware found")
        else:
            for source, essence_cost, modifier_data in cyberware:
                # Check if essence_cost is in modifier_data JSONB
                jsonb_cost = None
                if modifier_data and isinstance(modifier_data, dict):
                    jsonb_cost = modifier_data.get('essence_cost')
                
                print(f"\n  {source}:")
                print(f"    essence_cost column: {essence_cost}")
                print(f"    modifier_data.essence_cost: {jsonb_cost}")
                
                if essence_cost is None and jsonb_cost is None:
                    print(f"    ⚠️  MISSING ESSENCE COST!")
        
        print("\nBIOWARE ITEMS (checking body_index_cost)")
        print("-" * 80)
        
        cur.execute("""
            SELECT source, modifier_data
            FROM character_modifiers
            WHERE character_id = %s 
            AND source_type = 'bioware'
            AND deleted_at IS NULL
            GROUP BY source, modifier_data
            ORDER BY source
        """, (char_id,))
        
        bioware = cur.fetchall()
        if not bioware:
            print("  No bioware found")
        else:
            for source, modifier_data in bioware:
                # Check if body_index_cost is in modifier_data JSONB
                jsonb_cost = None
                if modifier_data and isinstance(modifier_data, dict):
                    jsonb_cost = modifier_data.get('body_index_cost')
                
                print(f"\n  {source}:")
                print(f"    modifier_data.body_index_cost: {jsonb_cost}")
                
                if jsonb_cost is None:
                    print(f"    ⚠️  MISSING BODY INDEX COST!")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
