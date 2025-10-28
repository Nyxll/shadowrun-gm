#!/usr/bin/env python3
"""
Check if spells have learned_force values
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
    conn = psycopg.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Check if learned_force column exists
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'character_spells' 
            AND column_name = 'learned_force'
        """)
        
        col_info = cursor.fetchone()
        if col_info:
            print(f"✓ Column 'learned_force' exists: {col_info[1]}")
        else:
            print("✗ Column 'learned_force' does not exist!")
            return
        
        # Get all spells with their force values
        cursor.execute("""
            SELECT 
                c.name as character_name,
                cs.spell_name,
                cs.spell_category,
                cs.learned_force
            FROM character_spells cs
            JOIN characters c ON cs.character_id = c.id
            ORDER BY c.name, cs.spell_category, cs.spell_name
        """)
        
        spells = cursor.fetchall()
        
        if not spells:
            print("\nNo spells found in database!")
            return
        
        print(f"\nFound {len(spells)} spells:")
        print("=" * 80)
        
        current_char = None
        spells_with_force = 0
        spells_without_force = 0
        
        for spell in spells:
            char_name, spell_name, category, force = spell
            
            if char_name != current_char:
                if current_char:
                    print()
                current_char = char_name
                print(f"\n{char_name}:")
                print("-" * 80)
            
            force_display = f"Force {force}" if force else "NO FORCE"
            status = "✓" if force else "✗"
            
            if force:
                spells_with_force += 1
            else:
                spells_without_force += 1
            
            print(f"  {status} {spell_name:30} ({category:15}) {force_display}")
        
        print("\n" + "=" * 80)
        print(f"Summary:")
        print(f"  Spells with force: {spells_with_force}")
        print(f"  Spells without force: {spells_without_force}")
        
        if spells_without_force > 0:
            print(f"\n⚠ {spells_without_force} spells need force values!")
            print("  You can add them with:")
            print("  UPDATE character_spells SET learned_force = 6 WHERE spell_name = 'Spell Name';")
        
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
