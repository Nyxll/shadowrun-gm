#!/usr/bin/env python3
"""
Migrate Platinum's cyberware to character_modifiers table
Adds vision enhancements and smartlink as modifiers
"""
import os
import sys
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row

load_dotenv()

def main():
    print("=" * 70)
    print("MIGRATING PLATINUM'S CYBERWARE TO MODIFIERS")
    print("=" * 70)
    
    conn = psycopg.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB'),
        row_factory=dict_row
    )
    
    cursor = conn.cursor()
    
    try:
        # Get Platinum's character ID
        cursor.execute("""
            SELECT id, name FROM characters
            WHERE LOWER(name) = 'kent jefferies' OR LOWER(street_name) = 'platinum'
        """)
        
        char = cursor.fetchone()
        if not char:
            print("ERROR: Platinum not found!")
            return
        
        char_id = char['id']
        print(f"\nFound character: {char['name']} (ID: {char_id})")
        
        # Check existing modifiers
        cursor.execute("""
            SELECT COUNT(*) as count FROM character_modifiers
            WHERE character_id = %s
        """, (char_id,))
        
        existing_count = cursor.fetchone()['count']
        print(f"Existing modifiers: {existing_count}")
        
        # Add vision modifiers
        print("\nAdding vision modifiers...")
        
        # Thermographic vision (cybernetic)
        cursor.execute("""
            INSERT INTO character_modifiers (
                character_id, modifier_type, target_name, modifier_value,
                source, source_type, modifier_data, is_permanent
            ) VALUES (
                %s, 'vision', 'thermographic', 1,
                'Cybereyes Alpha', 'cyberware',
                '{"vision_type": "cybernetic", "darkness_penalty": 2}'::jsonb,
                true
            )
            ON CONFLICT DO NOTHING
        """, (char_id,))
        print("  ✓ Thermographic vision (cybernetic)")
        
        # Low-light vision (cybernetic)
        cursor.execute("""
            INSERT INTO character_modifiers (
                character_id, modifier_type, target_name, modifier_value,
                source, source_type, modifier_data, is_permanent
            ) VALUES (
                %s, 'vision', 'lowLight', 1,
                'Cybereyes Alpha', 'cyberware',
                '{"vision_type": "cybernetic"}'::jsonb,
                true
            )
            ON CONFLICT DO NOTHING
        """, (char_id,))
        print("  ✓ Low-light vision (cybernetic)")
        
        # Optical magnification 3
        cursor.execute("""
            INSERT INTO character_modifiers (
                character_id, modifier_type, target_name, modifier_value,
                source, source_type, modifier_data, is_permanent
            ) VALUES (
                %s, 'vision', 'magnification', 3,
                'Cybereyes Alpha', 'cyberware',
                '{"max_range_shift": 3}'::jsonb,
                true
            )
            ON CONFLICT DO NOTHING
        """, (char_id,))
        print("  ✓ Optical magnification 3")
        
        # Add smartlink modifier
        print("\nAdding combat modifiers...")
        
        # Smartlink 3 (base -2, +1 for rating 3 = -3 total)
        cursor.execute("""
            INSERT INTO character_modifiers (
                character_id, modifier_type, target_name, modifier_value,
                source, source_type, modifier_data, is_permanent
            ) VALUES (
                %s, 'combat', 'ranged_tn', -3,
                'Smartlink 3', 'cyberware',
                '{"rating": 3, "requires_weapon_smartlink": true, "description": "Smartlink 3: -2 base, +1 for rating 3"}'::jsonb,
                true
            )
            ON CONFLICT DO NOTHING
        """, (char_id,))
        print("  ✓ Smartlink 3 (-3 TN)")
        
        # Commit changes
        conn.commit()
        
        # Verify
        cursor.execute("""
            SELECT 
                modifier_type,
                target_name,
                modifier_value,
                source,
                source_type
            FROM character_modifiers
            WHERE character_id = %s
            ORDER BY modifier_type, target_name
        """, (char_id,))
        
        modifiers = cursor.fetchall()
        
        print(f"\n{'='*70}")
        print(f"FINAL MODIFIERS FOR {char['name'].upper()}")
        print(f"{'='*70}")
        
        for mod in modifiers:
            sign = '+' if mod['modifier_value'] > 0 else ''
            print(f"{mod['modifier_type']:.<15} {mod['target_name']:.<20} {sign}{mod['modifier_value']:>3}  ({mod['source']})")
        
        print(f"\n{'='*70}")
        print("MIGRATION COMPLETE!")
        print(f"{'='*70}")
        
    except Exception as e:
        conn.rollback()
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
