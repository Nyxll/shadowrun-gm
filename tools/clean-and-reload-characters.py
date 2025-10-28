#!/usr/bin/env python3
"""
Clean character tables and reload all characters from markdown files
"""
import os
import sys
import subprocess
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row

load_dotenv()

def clean_character_tables():
    """Delete all data from character-related tables"""
    print("Connecting to database...")
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
        print("\nCleaning character tables...")
        print("=" * 70)
        
        # Delete in order to respect foreign key constraints
        tables = [
            'character_spells',
            'character_edges_flaws',
            'character_contacts',
            'character_vehicles',
            'character_modifiers',
            'character_gear',
            'character_skills',
            'characters'
        ]
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
            count = cursor.fetchone()['count']
            
            cursor.execute(f"DELETE FROM {table}")
            print(f"  ✓ Deleted {count} rows from {table}")
        
        conn.commit()
        print("\n✓ All character tables cleaned successfully!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ Error cleaning tables: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def main():
    """Clean tables and reload characters"""
    try:
        # Step 1: Clean tables
        clean_character_tables()
        
        # Step 2: Import characters using the existing script
        print("\nStarting character import...")
        print("=" * 70)
        
        # Run the complete import script
        import_script = os.path.join(os.path.dirname(__file__), 'import-characters-complete.py')
        result = subprocess.run([sys.executable, import_script], 
                              capture_output=False, 
                              text=True)
        
        if result.returncode != 0:
            print(f"\n✗ Import script failed with return code {result.returncode}")
            sys.exit(1)
        
        print("\n" + "=" * 70)
        print("✓ Character reload complete!")
        
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
