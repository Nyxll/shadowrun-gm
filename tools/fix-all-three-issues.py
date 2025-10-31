#!/usr/bin/env python3
"""
Fix three issues:
1. Set base_essence to 6.0 for all characters (standard human)
2. Link Oak's spells to master_spells table
3. Import notes from character .md files
"""
import os
import re
from dotenv import load_dotenv
import psycopg2

load_dotenv()

def fix_all_issues():
    """Fix all three issues"""
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB')
    )
    
    try:
        cur = conn.cursor()
        
        # ===== ISSUE 1: Fix All Characters' Essence =====
        print("=" * 60)
        print("ISSUE 1: Fixing Base Essence for All Characters")
        print("=" * 60)
        
        # Set base_essence to 6.0 for all characters (standard for humans)
        cur.execute("""
            UPDATE characters
            SET base_essence = 6.0
            WHERE base_essence = 0.0 OR base_essence IS NULL
        """)
        
        updated_count = cur.rowcount
        print(f"✅ Updated {updated_count} characters to base_essence = 6.0")
        
        # Verify
        cur.execute("""
            SELECT street_name, base_essence, essence_hole
            FROM characters
            ORDER BY street_name
        """)
        
        print("\nCurrent essence values:")
        for street_name, base, hole in cur.fetchall():
            current = (base or 0) - (hole or 0)
            print(f"  {street_name}: base={base}, hole={hole}, current={current}")
        
        # ===== ISSUE 2: Link Oak's Spells to Master Spells =====
        print("\n" + "=" * 60)
        print("ISSUE 2: Linking Oak's Spells to Master Spells")
        print("=" * 60)
        
        # Get Oak's ID using street_name
        cur.execute("SELECT id FROM characters WHERE street_name = 'Oak'")
        result = cur.fetchone()
        
        if result:
            oak_id = result[0]
            
            # Get Oak's spells
            cur.execute("""
                SELECT id, name
                FROM character_spells
                WHERE character_id = %s
                ORDER BY name
            """, (oak_id,))
            
            oak_spells = cur.fetchall()
            print(f"Found {len(oak_spells)} spells for Oak")
            
            linked_count = 0
            for spell_id, spell_name in oak_spells:
                # Try to find matching master spell
                cur.execute("""
                    SELECT id FROM master_spells
                    WHERE LOWER(name) = LOWER(%s)
                    LIMIT 1
                """, (spell_name,))
                
                master_result = cur.fetchone()
                if master_result:
                    master_id = master_result[0]
                    
                    # Link the spell
                    cur.execute("""
                        UPDATE character_spells
                        SET master_spell_id = %s
                        WHERE id = %s
                    """, (master_id, spell_id))
                    
                    linked_count += 1
                    print(f"   ✅ Linked '{spell_name}' to master_spells")
                else:
                    print(f"   ⚠️  No master spell found for '{spell_name}'")
            
            print(f"\n✅ Linked {linked_count}/{len(oak_spells)} spells")
        else:
            print("❌ Oak character not found")
        
        # ===== ISSUE 3: Import Notes from .md Files =====
        print("\n" + "=" * 60)
        print("ISSUE 3: Importing Notes from Character .md Files")
        print("=" * 60)
        
        # Check if characters directory exists
        char_dir = "characters"
        if not os.path.exists(char_dir):
            print(f"❌ Characters directory '{char_dir}' not found")
        else:
            # Get all .md files
            md_files = [f for f in os.listdir(char_dir) if f.endswith('.md')]
            print(f"Found {len(md_files)} .md files")
            
            notes_imported = 0
            for md_file in md_files:
                filepath = os.path.join(char_dir, md_file)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Extract street name from filename (e.g., "Platinum.md" -> "Platinum")
                    street_name = os.path.splitext(md_file)[0]
                    
                    # Use the entire markdown content as notes
                    if content.strip():
                        # Update character notes using street_name
                        cur.execute("""
                            UPDATE characters
                            SET notes = %s
                            WHERE street_name = %s
                        """, (content, street_name))
                        
                        if cur.rowcount > 0:
                            notes_imported += 1
                            preview = content[:50].replace('\n', ' ') + "..." if len(content) > 50 else content
                            print(f"   ✅ {street_name}: {preview}")
                        else:
                            print(f"   ⚠️  {street_name}: Character not found in DB")
                    
                except Exception as e:
                    print(f"   ❌ Error reading {md_file}: {e}")
            
            print(f"\n✅ Imported notes for {notes_imported} characters")
        
        # Commit all changes
        conn.commit()
        print("\n" + "=" * 60)
        print("ALL FIXES APPLIED SUCCESSFULLY")
        print("=" * 60)
        
        cur.close()
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
