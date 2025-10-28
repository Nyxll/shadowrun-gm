#!/usr/bin/env python3
"""
Apply campaign management migration (016)
Creates campaigns, campaign_npcs, and campaign_characters tables
"""
import os
import sys
from dotenv import load_dotenv
import psycopg2

load_dotenv()

def apply_migration():
    """Apply the campaign management migration"""
    
    # Database connection
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB')
    )
    
    cursor = conn.cursor()
    
    try:
        print("Applying migration 016: Campaign Management System...")
        
        # Read migration file
        with open('migrations/016_add_campaign_management.sql', 'r') as f:
            migration_sql = f.read()
        
        # Execute migration
        cursor.execute(migration_sql)
        conn.commit()
        
        print("✓ Migration applied successfully")
        
        # Verify tables were created
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
              AND table_name IN ('campaigns', 'campaign_npcs', 'campaign_characters')
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        print(f"\n✓ Created {len(tables)} tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Check indexes
        cursor.execute("""
            SELECT indexname 
            FROM pg_indexes 
            WHERE schemaname = 'public' 
              AND tablename IN ('campaigns', 'campaign_npcs', 'campaign_characters')
            ORDER BY indexname
        """)
        
        indexes = cursor.fetchall()
        print(f"\n✓ Created {len(indexes)} indexes:")
        for idx in indexes:
            print(f"  - {idx[0]}")
        
        print("\n✓ Campaign management system ready!")
        
    except Exception as e:
        conn.rollback()
        print(f"\n✗ Error applying migration: {e}")
        sys.exit(1)
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    apply_migration()
