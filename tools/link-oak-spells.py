#!/usr/bin/env python3
"""
Link Oak's spells to master_spells table and set learned forces
"""
import os
from dotenv import load_dotenv
import psycopg

load_dotenv()

def link_spells():
    """Link character spells to master spells"""
    conn = psycopg.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB')
    )
    
    cursor = conn.cursor()
    
    # Get Oak's ID
    cursor.execute("SELECT id FROM characters WHERE street_name = 'Oak'")
    oak_id = cursor.fetchone()[0]
    
    # Get Oak's spells
    cursor.execute("""
        SELECT id, spell_name 
        FROM character_spells 
        WHERE character_id = %s AND deleted_at IS NULL
    """, (oak_id,))
    
    oak_spells = cursor.fetchall()
    
    print(f"Linking {len(oak_spells)} spells for Oak...")
    
    linked = 0
    not_found = []
    
    for spell_id, spell_name in oak_spells:
        # Find matching master spell
        cursor.execute("""
            SELECT id, drain_formula 
            FROM master_spells 
            WHERE LOWER(spell_name) = LOWER(%s)
        """, (spell_name,))
        
        result = cursor.fetchone()
        
        if result:
            master_id, drain_formula = result
            
            # Update character spell with master_spell_id and learned force of 6
            cursor.execute("""
                UPDATE character_spells 
                SET master_spell_id = %s, force = 6, drain_code = %s
                WHERE id = %s
            """, (master_id, drain_formula, spell_id))
            
            linked += 1
            print(f"✓ Linked {spell_name} (Force 6, drain: {drain_formula})")
        else:
            not_found.append(spell_name)
            print(f"✗ {spell_name} not found in master_spells")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"\n✓ Linked {linked} spells")
    if not_found:
        print(f"✗ {len(not_found)} spells not found: {', '.join(not_found)}")

if __name__ == "__main__":
    link_spells()
