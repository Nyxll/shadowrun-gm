#!/usr/bin/env python3
"""
Migrate character_skills and character_gear foreign keys from INTEGER to UUID
This fixes the schema mismatch where characters.id is UUID but child tables use INTEGER
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

def check_current_state(conn):
    """Check current schema state"""
    cursor = conn.cursor()
    
    print("=== CURRENT SCHEMA STATE ===\n")
    
    # Check characters table
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name='characters' AND column_name='id'
    """)
    char_id = cursor.fetchone()
    print(f"characters.id: {char_id['data_type']}")
    
    # Check character_skills
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name='character_skills' AND column_name='character_id'
    """)
    skills_fk = cursor.fetchone()
    if skills_fk:
        print(f"character_skills.character_id: {skills_fk['data_type']}")
    else:
        print("character_skills table does not exist")
    
    # Check character_gear
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name='character_gear' AND column_name='character_id'
    """)
    gear_fk = cursor.fetchone()
    if gear_fk:
        print(f"character_gear.character_id: {gear_fk['data_type']}")
    else:
        print("character_gear table does not exist")
    
    # Check for existing data
    print("\n=== DATA CHECK ===\n")
    
    cursor.execute("SELECT COUNT(*) as count FROM characters")
    char_count = cursor.fetchone()['count']
    print(f"Characters: {char_count} records")
    
    if skills_fk:
        cursor.execute("SELECT COUNT(*) as count FROM character_skills")
        skills_count = cursor.fetchone()['count']
        print(f"Character Skills: {skills_count} records")
    
    if gear_fk:
        cursor.execute("SELECT COUNT(*) as count FROM character_gear")
        gear_count = cursor.fetchone()['count']
        print(f"Character Gear: {gear_count} records")
    
    cursor.close()
    
    return {
        'has_skills_table': skills_fk is not None,
        'has_gear_table': gear_fk is not None,
        'char_id_type': char_id['data_type'],
        'skills_fk_type': skills_fk['data_type'] if skills_fk else None,
        'gear_fk_type': gear_fk['data_type'] if gear_fk else None
    }

def check_foreign_key_constraints(conn):
    """Check for existing foreign key constraints"""
    cursor = conn.cursor()
    
    print("\n=== FOREIGN KEY CONSTRAINTS ===\n")
    
    cursor.execute("""
        SELECT
            tc.table_name,
            tc.constraint_name,
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_name IN ('character_skills', 'character_gear')
    """)
    
    constraints = cursor.fetchall()
    
    if constraints:
        for c in constraints:
            print(f"{c['table_name']}.{c['column_name']} -> {c['foreign_table_name']}.{c['foreign_column_name']}")
            print(f"  Constraint: {c['constraint_name']}")
    else:
        print("No foreign key constraints found")
    
    cursor.close()
    return constraints

def migrate_table(conn, table_name):
    """Migrate a single table's character_id column to UUID"""
    cursor = conn.cursor()
    
    print(f"\n=== MIGRATING {table_name.upper()} ===\n")
    
    try:
        # Step 1: Drop foreign key constraint if it exists
        print(f"1. Checking for foreign key constraints...")
        cursor.execute(f"""
            SELECT constraint_name
            FROM information_schema.table_constraints
            WHERE table_name = '{table_name}'
                AND constraint_type = 'FOREIGN KEY'
                AND constraint_name LIKE '%character_id%'
        """)
        
        fk_constraint = cursor.fetchone()
        if fk_constraint:
            constraint_name = fk_constraint['constraint_name']
            print(f"   Dropping constraint: {constraint_name}")
            cursor.execute(f"ALTER TABLE {table_name} DROP CONSTRAINT {constraint_name}")
        else:
            print(f"   No foreign key constraint found")
        
        # Step 2: Alter column type
        print(f"2. Converting character_id from INTEGER to UUID...")
        
        # First, check if there's any data that can't be converted
        cursor.execute(f"""
            SELECT character_id, COUNT(*) as count
            FROM {table_name}
            GROUP BY character_id
            LIMIT 5
        """)
        sample_data = cursor.fetchall()
        
        if sample_data:
            print(f"   Sample existing character_id values: {[row['character_id'] for row in sample_data]}")
            print(f"   WARNING: These INTEGER values cannot be directly converted to UUID!")
            print(f"   The table will need to be cleared or manually mapped.")
            
            # Ask for confirmation
            response = input(f"\n   Clear all data from {table_name}? (yes/no): ")
            if response.lower() == 'yes':
                cursor.execute(f"DELETE FROM {table_name}")
                deleted = cursor.rowcount
                print(f"   Deleted {deleted} rows from {table_name}")
            else:
                print(f"   Skipping {table_name} migration")
                return False
        
        # Now alter the column type
        cursor.execute(f"""
            ALTER TABLE {table_name} 
            ALTER COLUMN character_id TYPE UUID 
            USING NULL::UUID
        """)
        print(f"   ✓ Column type changed to UUID")
        
        # Step 3: Recreate foreign key constraint
        print(f"3. Creating foreign key constraint...")
        cursor.execute(f"""
            ALTER TABLE {table_name}
            ADD CONSTRAINT fk_{table_name}_character
            FOREIGN KEY (character_id)
            REFERENCES characters(id)
            ON DELETE CASCADE
        """)
        print(f"   ✓ Foreign key constraint created")
        
        # Commit the changes
        conn.commit()
        print(f"\n✓ {table_name} migration complete!")
        return True
        
    except Exception as e:
        print(f"\n✗ Error migrating {table_name}: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def verify_migration(conn):
    """Verify the migration was successful"""
    cursor = conn.cursor()
    
    print("\n=== VERIFICATION ===\n")
    
    # Check column types
    cursor.execute("""
        SELECT 
            table_name,
            column_name,
            data_type
        FROM information_schema.columns
        WHERE table_name IN ('characters', 'character_skills', 'character_gear')
            AND column_name IN ('id', 'character_id')
        ORDER BY table_name, column_name
    """)
    
    columns = cursor.fetchall()
    for col in columns:
        print(f"{col['table_name']}.{col['column_name']}: {col['data_type']}")
    
    # Check foreign keys
    cursor.execute("""
        SELECT
            tc.table_name,
            tc.constraint_name,
            tc.constraint_type
        FROM information_schema.table_constraints AS tc
        WHERE tc.table_name IN ('character_skills', 'character_gear')
            AND tc.constraint_type = 'FOREIGN KEY'
    """)
    
    fks = cursor.fetchall()
    print(f"\nForeign key constraints: {len(fks)}")
    for fk in fks:
        print(f"  {fk['table_name']}: {fk['constraint_name']}")
    
    cursor.close()

def main():
    """Main migration function"""
    print("=" * 60)
    print("CHARACTER FOREIGN KEY MIGRATION TO UUID")
    print("=" * 60)
    print()
    print("This script will migrate character_skills and character_gear")
    print("foreign keys from INTEGER to UUID to match characters.id")
    print()
    
    conn = get_connection()
    
    try:
        # Check current state
        state = check_current_state(conn)
        
        # Check constraints
        constraints = check_foreign_key_constraints(conn)
        
        # Verify we need to migrate
        if state['char_id_type'] != 'uuid':
            print("\n✗ ERROR: characters.id is not UUID type!")
            print("This migration expects characters.id to be UUID.")
            return
        
        needs_migration = False
        
        if state['has_skills_table'] and state['skills_fk_type'] != 'uuid':
            needs_migration = True
        
        if state['has_gear_table'] and state['gear_fk_type'] != 'uuid':
            needs_migration = True
        
        if not needs_migration:
            print("\n✓ No migration needed - all foreign keys are already UUID!")
            return
        
        # Confirm migration
        print("\n" + "=" * 60)
        print("READY TO MIGRATE")
        print("=" * 60)
        response = input("\nProceed with migration? (yes/no): ")
        
        if response.lower() != 'yes':
            print("\nMigration cancelled.")
            return
        
        # Migrate tables
        success = True
        
        if state['has_skills_table'] and state['skills_fk_type'] != 'uuid':
            if not migrate_table(conn, 'character_skills'):
                success = False
        
        if state['has_gear_table'] and state['gear_fk_type'] != 'uuid':
            if not migrate_table(conn, 'character_gear'):
                success = False
        
        # Verify
        if success:
            verify_migration(conn)
            print("\n" + "=" * 60)
            print("✓ MIGRATION COMPLETE!")
            print("=" * 60)
            print("\nNext steps:")
            print("1. Remove workaround code from game-server.py")
            print("2. Restart the game server")
            print("3. Test character sheets load with skills/gear")
        else:
            print("\n✗ Migration completed with errors")
            print("Please review the output above")
    
    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        conn.close()

if __name__ == "__main__":
    main()
