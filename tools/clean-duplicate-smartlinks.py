#!/usr/bin/env python3
"""
Remove duplicate smartlink modifiers for Platinum
Keep only the Smartlink 3 entry
"""
import os
import sys
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row

load_dotenv()

def main():
    print("=" * 70)
    print("CLEANING DUPLICATE SMARTLINK MODIFIERS")
    print("=" * 70)
    
    conn = psycopg.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB'),
        row_factory=dict_row
    )
    
    cursor = conn.cursor()
    
    try:
        # Get Platinum's character ID
        cursor.execute("""
            SELECT id, name FROM characters
            WHERE LOWER(name) = 'kent jefferies' OR LOWER(street_name) = 'platinum'
        """)
        
        char = cursor.fetchone()
        if not char:
            print("ERROR: Platinum not found!")
            return
        
        char_id = char['id']
        print(f"\nFound character: {char['name']} (ID: {char_id})")
        
        # Find all smartlink modifiers
        cursor.execute("""
            SELECT id, source, modifier_value, modifier_data
            FROM character_modifiers
            WHERE character_id = %s
              AND modifier_type = 'combat'
              AND target_name = 'ranged_tn'
              AND LOWER(source) LIKE LOWER(%s)
            ORDER BY created_at
        """, (char_id, '%smartlink%'))
        
        smartlinks = cursor.fetchall()
        
        print(f"\nFound {len(smartlinks)} smartlink modifiers:")
        for sl in smartlinks:
            print(f"  - {sl['source']}: {sl['modifier_value']} (ID: {sl['id']})")
        
        if len(smartlinks) <= 1:
            print("\nNo duplicates to clean up!")
            return
        
        # Keep the last one (Smartlink 3), delete the rest
        to_delete = smartlinks[:-1]
        to_keep = smartlinks[-1]
        
        print(f"\nKeeping: {to_keep['source']} ({to_keep['modifier_value']})")
        print(f"Deleting {len(to_delete)} duplicate(s):")
        
        for sl in to_delete:
            print(f"  - {sl['source']}")
            cursor.execute("""
                DELETE FROM character_modifiers
                WHERE id = %s
            """, (sl['id'],))
        
        conn.commit()
        
        print(f"\n{'='*70}")
        print("CLEANUP COMPLETE!")
        print(f"{'='*70}")
        
    except Exception as e:
        conn.rollback()
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
