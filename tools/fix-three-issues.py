#!/usr/bin/env python3
"""
Fix three issues:
1. Platinum's essence (set to 6.0)
2. Link Oak's spells to master_spells table
3. Import notes from character JSON files
"""
import os
import json
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
        
        # ===== ISSUE 1: Fix Platinum's Essence =====
        print("=" * 60)
        print("ISSUE 1: Fixing Platinum's Essence")
        print("=" * 60)
        
        # Get Platinum's ID
        cur.execute("SELECT id FROM characters WHERE name = 'Platinum'")
        result = cur.fetchone()
        
        if result:
            platinum_id = result[0]
            
            # Set base_essence to 6.0 (standard for humans)
            cur.execute("""
                UPDATE characters
                SET base_essence = 6.0
                WHERE id = %s
            """, (platinum_id,))
            
            print(f"✅ Set Platinum's base_essence to 6.0")
            
            # Verify
            cur.execute("""
                SELECT base_essence, essence_loss
                FROM characters
                WHERE id = %s
            """, (platinum_id,))
            
            base, loss = cur.fetchone()
            current = base - loss
            print(f"   Base: {base}, Loss: {loss}, Current: {current}")
        else:
            print("❌ Platinum character not found")
        
        # ===== ISSUE 2: Link Oak's Spells to Master Spells =====
        print("\n" + "=" * 60)
        print("ISSUE 2: Linking Oak's Spells to Master Spells")
        print("=" * 60)
        
        # Get Oak's ID
        cur.execute("SELECT id FROM characters WHERE name = 'Oak'")
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
        
        # ===== ISSUE 3: Import Notes from JSON Files =====
        print("\n" + "=" * 60)
        print("ISSUE 3: Importing Notes from Character JSON Files")
        print("=" * 60)
        
        # Check if characters directory exists
        char_dir = "characters"
        if not os.path.exists(char_dir):
            print(f"❌ Characters directory '{char_dir}' not found")
        else:
            # Get all JSON files
            json_files = [f for f in os.listdir(char_dir) if f.endswith('.json')]
            print(f"Found {len(json_files)} JSON files")
            
            notes_imported = 0
            for json_file in json_files:
                filepath = os.path.join(char_dir, json_file)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    char_name = data.get('name')
                    notes = data.get('notes') or data.get('description')
                    
                    if char_name and notes:
                        # Update character notes
                        cur.execute("""
                            UPDATE characters
                            SET notes = %s
                            WHERE name = %s
                        """, (notes, char_name))
                        
                        if cur.rowcount > 0:
                            notes_imported += 1
                            preview = notes[:50] + "..." if len(notes) > 50 else notes
                            print(f"   ✅ {char_name}: {preview}")
                        else:
                            print(f"   ⚠️  {char_name}: Character not found in DB")
                    
                except Exception as e:
                    print(f"   ❌ Error reading {json_file}: {e}")
            
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
    fix_all_issues()
