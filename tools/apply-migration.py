#!/usr/bin/env python3
"""
Apply a specific migration file to the database
"""
import os
import sys
from dotenv import load_dotenv
import psycopg2

# Load environment variables
load_dotenv()

def apply_migration(migration_file):
    """Apply a migration file to the database"""
    if not os.path.exists(migration_file):
        print(f"ERROR: Migration file not found: {migration_file}")
        return False
    
    try:
        conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST'),
            port=os.getenv('POSTGRES_PORT'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            dbname=os.getenv('POSTGRES_DB')
        )
        
        cursor = conn.cursor()
        
        # Read and execute migration
        with open(migration_file, 'r', encoding='utf-8') as f:
            sql = f.read()
        
        print(f"Applying migration: {migration_file}")
        cursor.execute(sql)
        conn.commit()
        
        print(f"✓ Migration applied successfully")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python apply-migration.py <migration_file>")
        print("Example: python apply-migration.py migrations/021_add_master_spells_table.sql")
        sys.exit(1)
    
    migration_file = sys.argv[1]
    success = apply_migration(migration_file)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
