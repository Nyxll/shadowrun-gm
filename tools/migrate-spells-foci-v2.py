#!/usr/bin/env python3
"""
Migrate spells and foci tables - handles existing old schema
"""
import os
from dotenv import load_dotenv
import psycopg

load_dotenv()

def main():
    """Migrate spells and foci tables"""
    try:
        conn = psycopg.connect(
            host=os.getenv('POSTGRES_HOST'),
            port=os.getenv('POSTGRES_PORT'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            dbname=os.getenv('POSTGRES_DB')
        )
        
        cursor = conn.cursor()
        
        print("Checking existing tables...")
        
        # Check if old character_spells exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'character_spells'
            )
        """)
        
        old_spells_exists = cursor.fetchone()[0]
        
        if old_spells_exists:
            print("Found old character_spells table - dropping it...")
            cursor.execute("DROP TABLE IF EXISTS character_spells CASCADE")
            conn.commit()
            print("✓ Dropped old character_spells table")
        
        # Drop any orphaned indexes
        print("Cleaning up orphaned indexes...")
        cursor.execute("DROP INDEX IF EXISTS idx_spells_character CASCADE")
        cursor.execute("DROP INDEX IF EXISTS idx_spells_category CASCADE")
        cursor.execute("DROP INDEX IF EXISTS idx_foci_character CASCADE")
        cursor.execute("DROP INDEX IF EXISTS idx_foci_type CASCADE")
        cursor.execute("DROP INDEX IF EXISTS idx_foci_category CASCADE")
        conn.commit()
        print("✓ Cleaned up orphaned indexes")
        
        # Check if character_foci exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'character_foci'
            )
        """)
        
        foci_exists = cursor.fetchone()[0]
        
        if foci_exists:
            print("Found existing character_foci table - dropping it...")
            cursor.execute("DROP TABLE IF EXISTS character_foci CASCADE")
            conn.commit()
            print("✓ Dropped old character_foci table")
        
        # Now create new tables
        print("\nCreating new tables...")
        
        # Create character_spells
        cursor.execute("""
            CREATE TABLE character_spells (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                character_id UUID REFERENCES characters(id) ON DELETE CASCADE,
                
                spell_name TEXT NOT NULL,
                spell_category TEXT NOT NULL,
                spell_type TEXT NOT NULL,
                target_type TEXT,
                duration TEXT,
                drain_modifier INTEGER DEFAULT 0,
                
                description TEXT,
                notes TEXT,
                
                created_at TIMESTAMP DEFAULT NOW(),
                UNIQUE(character_id, spell_name)
            )
        """)
        
        cursor.execute("CREATE INDEX idx_spells_character ON character_spells(character_id)")
        cursor.execute("CREATE INDEX idx_spells_category ON character_spells(spell_category)")
        
        print("✓ Created character_spells table")
        
        # Create character_foci
        cursor.execute("""
            CREATE TABLE character_foci (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                character_id UUID REFERENCES characters(id) ON DELETE CASCADE,
                
                focus_name TEXT NOT NULL,
                focus_type TEXT NOT NULL,
                force INTEGER NOT NULL,
                
                spell_category TEXT,
                specific_spell TEXT,
                
                bonus_dice INTEGER DEFAULT 0,
                tn_modifier INTEGER DEFAULT 0,
                
                bonded BOOLEAN DEFAULT TRUE,
                karma_cost INTEGER,
                description TEXT,
                notes TEXT,
                
                created_at TIMESTAMP DEFAULT NOW(),
                UNIQUE(character_id, focus_name)
            )
        """)
        
        cursor.execute("CREATE INDEX idx_foci_character ON character_foci(character_id)")
        cursor.execute("CREATE INDEX idx_foci_type ON character_foci(focus_type)")
        cursor.execute("CREATE INDEX idx_foci_category ON character_foci(spell_category)")
        
        print("✓ Created character_foci table")
        
        conn.commit()
        
        print("\n✓ Migration completed successfully!")
        print("\nNew table structure:")
        print("  - character_spells: Tracks spells known by each character")
        print("  - character_foci: Tracks magical foci (fetishes, power foci, etc.)")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error during migration: {e}")
        raise

if __name__ == "__main__":
    main()
