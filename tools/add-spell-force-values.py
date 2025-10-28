#!/usr/bin/env python3
"""
Add reasonable learned_force values to all spells
Based on typical Shadowrun 2E spell force levels
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

# Typical force levels for different spell types
SPELL_FORCE_DEFAULTS = {
    # Combat spells - typically learned at Force 6
    'Stunball': 6,
    'Stunbolt': 6,
    'Lightning Bolt': 6,
    'Manabolt': 6,
    
    # Detection spells - typically Force 4-6
    'Mind Probe': 5,
    
    # Health spells - typically Force 4-6
    'Increase Reflex +3': 3,  # Force equals the bonus
    'Treat': 5,
    'Stabilize': 4,
    
    # Illusion spells - typically Force 4-6
    'Improved Invisibility': 6,
    'Physical Mask': 5,
    'Invisibility': 6,
    
    # Manipulation spells - typically Force 4-6
    'Levitate': 5,
    'Levitate Person': 5,
    'Silence': 4,
    'Control Thoughts': 6,
    'Mana Barrier': 5,
    'Physical Barrier': 5,
    
    # Special/Unknown - conservative Force 4
    'Recharge': 4,
    'Stop Regeneration': 4,
}

def main():
    conn = psycopg.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Get all spells
        cursor.execute("""
            SELECT 
                cs.id,
                c.name as character_name,
                cs.spell_name,
                cs.spell_category,
                cs.learned_force
            FROM character_spells cs
            JOIN characters c ON cs.character_id = c.id
            ORDER BY c.name, cs.spell_name
        """)
        
        spells = cursor.fetchall()
        
        print(f"Adding force values to {len(spells)} spells...")
        print("=" * 80)
        
        updated = 0
        skipped = 0
        
        for spell in spells:
            spell_id, char_name, spell_name, category, current_force = spell
            
            # Skip if already has force
            if current_force:
                print(f"  ⊘ {char_name}: {spell_name} - already has Force {current_force}")
                skipped += 1
                continue
            
            # Get default force for this spell
            force = SPELL_FORCE_DEFAULTS.get(spell_name, 5)  # Default to 5 if not in list
            
            # Update the spell
            cursor.execute("""
                UPDATE character_spells
                SET learned_force = %s
                WHERE id = %s
            """, (force, spell_id))
            
            print(f"  ✓ {char_name}: {spell_name:30} -> Force {force}")
            updated += 1
        
        conn.commit()
        
        print("\n" + "=" * 80)
        print(f"Summary:")
        print(f"  Updated: {updated}")
        print(f"  Skipped (already had force): {skipped}")
        print(f"  Total: {len(spells)}")
        
    except Exception as e:
        conn.rollback()
        print(f"\n✗ Error: {e}")
        raise
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
