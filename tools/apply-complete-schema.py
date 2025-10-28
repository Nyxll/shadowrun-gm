#!/usr/bin/env python3
"""
Apply complete character schema migration
Adds all missing columns and tables to support full character data
"""
import os
from dotenv import load_dotenv
import psycopg

load_dotenv()

def main():
    """Apply migration 008"""
    conn = psycopg.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB')
    )
    
    cur = conn.cursor()
    
    try:
        print("Applying migration 008: Complete Character Schema...")
        print("=" * 80)
        
        # Read migration file
        with open('migrations/008_add_complete_character_schema.sql', 'r') as f:
            migration_sql = f.read()
        
        # Execute migration
        cur.execute(migration_sql)
        conn.commit()
        
        print("✓ Migration applied successfully!")
        print()
        
        # Verify new columns exist
        print("Verifying new schema...")
        print("-" * 80)
        
        # Check characters table
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='characters' 
            ORDER BY ordinal_position
        """)
        char_columns = [row[0] for row in cur.fetchall()]
        print(f"✓ characters table has {len(char_columns)} columns")
        
        # Check character_skills table
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='character_skills' 
            ORDER BY ordinal_position
        """)
        skill_columns = [row[0] for row in cur.fetchall()]
        print(f"✓ character_skills table has {len(skill_columns)} columns")
        if 'skill_type' in skill_columns:
            print("  ✓ skill_type column added")
        
        # Check character_modifiers table
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='character_modifiers' 
            ORDER BY ordinal_position
        """)
        mod_columns = [row[0] for row in cur.fetchall()]
        print(f"✓ character_modifiers table has {len(mod_columns)} columns")
        if 'essence_cost' in mod_columns:
            print("  ✓ essence_cost column added")
        if 'body_index_cost' in mod_columns:
            print("  ✓ body_index_cost column added")
        
        # Check character_gear table
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='character_gear' 
            ORDER BY ordinal_position
        """)
        gear_columns = [row[0] for row in cur.fetchall()]
        print(f"✓ character_gear table has {len(gear_columns)} columns")
        if 'damage' in gear_columns:
            print("  ✓ damage column added")
        if 'conceal' in gear_columns:
            print("  ✓ conceal column added")
        
        # Check new tables
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema='public' 
              AND table_name IN ('character_vehicles', 'character_contacts', 
                                 'character_edges_flaws', 'character_spells')
            ORDER BY table_name
        """)
        new_tables = [row[0] for row in cur.fetchall()]
        print(f"\n✓ Created {len(new_tables)} new tables:")
        for table in new_tables:
            print(f"  ✓ {table}")
        
        print()
        print("=" * 80)
        print("Migration complete! Database is ready for full character data.")
        
    except Exception as e:
        conn.rollback()
        print(f"✗ Error applying migration: {e}")
        raise
    
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    main()
