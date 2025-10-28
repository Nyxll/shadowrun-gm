#!/usr/bin/env python3
"""
Apply migration 017: Add missing magic fields to characters table
"""
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

def apply_migration():
    """Apply the magic fields migration"""
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB')
    )
    
    cur = conn.cursor()
    
    print("Applying migration 017: Add missing magic fields...")
    print("=" * 70)
    
    # Read migration file
    with open('migrations/017_add_magic_fields.sql', 'r') as f:
        migration_sql = f.read()
    
    try:
        cur.execute(migration_sql)
        conn.commit()
        print("✓ Migration applied successfully!")
        
        # Verify columns were added
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'characters' 
            AND column_name IN ('magic_pool', 'spell_pool', 'initiate_level', 'metamagics', 'magical_group', 'tradition')
            ORDER BY column_name
        """)
        
        added_columns = [row[0] for row in cur.fetchall()]
        print(f"\n✓ Added columns: {', '.join(added_columns)}")
        
    except Exception as e:
        print(f"✗ Error applying migration: {e}")
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    apply_migration()
