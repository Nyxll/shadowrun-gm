#!/usr/bin/env python3
"""
Fix foreign key constraints to point to correct table
The constraints currently point to sr_characters.id (doesn't exist)
They should point to characters.id
"""
import os
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row

load_dotenv()

def get_connection():
    """Get database connection"""
    return psycopg.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB'),
        row_factory=dict_row
    )

def main():
    """Fix foreign key constraints"""
    print("=" * 60)
    print("FIX FOREIGN KEY CONSTRAINTS")
    print("=" * 60)
    print()
    print("This will:")
    print("1. Drop incorrect FK constraints (pointing to sr_characters)")
    print("2. Keep existing data intact")
    print("3. Note: Data won't match until you populate properly")
    print()
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Check current constraints
        print("=== CURRENT CONSTRAINTS ===\n")
        cursor.execute("""
            SELECT
                tc.table_name,
                tc.constraint_name,
                ccu.table_name AS foreign_table_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
                AND tc.table_name IN ('character_skills', 'character_gear')
        """)
        
        constraints = cursor.fetchall()
        for c in constraints:
            print(f"{c['table_name']}.{c['constraint_name']} -> {c['foreign_table_name']}")
        
        if not constraints:
            print("No foreign key constraints found")
            return
        
        print("\n" + "=" * 60)
        response = input("\nDrop these incorrect constraints? (yes/no): ")
        
        if response.lower() != 'yes':
            print("\nCancelled.")
            return
        
        # Drop constraints
        print("\n=== DROPPING CONSTRAINTS ===\n")
        for c in constraints:
            table = c['table_name']
            constraint = c['constraint_name']
            print(f"Dropping {table}.{constraint}...")
            cursor.execute(f"ALTER TABLE {table} DROP CONSTRAINT {constraint}")
        
        conn.commit()
        print("\n✓ Constraints dropped successfully!")
        print("\nNote: character_skills and character_gear now have no FK constraints")
        print("The INTEGER character_id values won't match UUID characters.id")
        print("You'll need to either:")
        print("  1. Clear and repopulate these tables with correct UUIDs")
        print("  2. Keep them as-is (data won't load in character sheets)")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
