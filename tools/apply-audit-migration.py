#!/usr/bin/env python3
"""
Apply migration 019: Add audit system and enhanced spell fields
"""
import os
from dotenv import load_dotenv
import psycopg

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', '127.0.0.1'),
    'port': int(os.getenv('POSTGRES_PORT', '5434')),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'dbname': os.getenv('POSTGRES_DB', 'postgres')
}

def main():
    print("Applying migration 019: Audit system and enhanced spell fields...")
    print("=" * 80)
    
    conn = psycopg.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Read migration file
        with open('migrations/019_add_audit_and_enhanced_spells.sql', 'r') as f:
            migration_sql = f.read()
        
        # Execute migration
        cursor.execute(migration_sql)
        conn.commit()
        
        print("\n✓ Migration applied successfully!")
        
        # Verify tables were created
        print("\nVerifying new tables...")
        
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('users', 'audit_log')
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        for table in tables:
            print(f"  ✓ Table '{table[0]}' exists")
        
        # Verify user was created
        cursor.execute("SELECT email, display_name FROM users WHERE email = 'rickstjean@gmail.com'")
        user = cursor.fetchone()
        if user:
            print(f"\n✓ Default user created: {user[1]} ({user[0]})")
        
        # Verify new columns on character_spells
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'character_spells' 
            AND column_name IN ('drain_code', 'target_type', 'totem_modifier', 'spell_notes',
                               'created_by', 'modified_by', 'deleted_at')
            ORDER BY column_name
        """)
        
        columns = cursor.fetchall()
        print(f"\n✓ Added {len(columns)} new columns to character_spells:")
        for col in columns:
            print(f"  - {col[0]}")
        
        # Verify triggers
        cursor.execute("""
            SELECT trigger_name 
            FROM information_schema.triggers 
            WHERE trigger_name LIKE 'audit_%'
            ORDER BY trigger_name
        """)
        
        triggers = cursor.fetchall()
        print(f"\n✓ Created {len(triggers)} audit triggers:")
        for trigger in triggers:
            print(f"  - {trigger[0]}")
        
        # Verify views
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.views 
            WHERE table_schema = 'public' 
            AND table_name LIKE 'active_%'
            ORDER BY table_name
        """)
        
        views = cursor.fetchall()
        print(f"\n✓ Created {len(views)} active views:")
        for view in views:
            print(f"  - {view[0]}")
        
        print("\n" + "=" * 80)
        print("Migration 019 completed successfully!")
        print("\nNext steps:")
        print("1. Update schema.sql with new tables/columns")
        print("2. Create Python hybrid search module")
        print("3. Enhance import script with RAG supplementation")
        
    except Exception as e:
        conn.rollback()
        print(f"\n✗ Error applying migration: {e}")
        raise
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
