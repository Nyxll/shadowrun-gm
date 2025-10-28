#!/usr/bin/env python3
"""
Apply totem support migration
"""
import os
from dotenv import load_dotenv
import psycopg

load_dotenv()

def main():
    """Apply migration 015"""
    try:
        conn = psycopg.connect(
            host=os.getenv('POSTGRES_HOST'),
            port=os.getenv('POSTGRES_PORT'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            dbname=os.getenv('POSTGRES_DB')
        )
        
        cursor = conn.cursor()
        
        print("Applying migration 015: Add Totem Support...")
        
        # Read migration file
        with open('migrations/015_add_totem_support.sql', 'r') as f:
            migration_sql = f.read()
        
        # Execute migration
        cursor.execute(migration_sql)
        conn.commit()
        
        print("✓ Migration applied successfully")
        
        # Verify tables created
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name = 'totems'
        """)
        
        if cursor.fetchone():
            print("✓ Totems table created")
        
        # Check totem column added
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'characters' 
              AND column_name = 'totem'
        """)
        
        if cursor.fetchone():
            print("✓ Totem column added to characters table")
        
        # Count totems
        cursor.execute("SELECT COUNT(*) FROM totems")
        count = cursor.fetchone()[0]
        print(f"✓ {count} totems loaded")
        
        # Show totems
        cursor.execute("""
            SELECT totem_name, favored_categories, spirit_type
            FROM totems
            ORDER BY totem_name
        """)
        
        print("\nAvailable totems:")
        for row in cursor.fetchall():
            print(f"  - {row[0]}: {', '.join(row[1])} ({row[2]} spirit)")
        
        cursor.close()
        conn.close()
        
        print("\n✓ Migration complete!")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
