#!/usr/bin/env python3
"""
Fix Platinum's cyberware essence costs
"""
import os
import json
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST'),
    'port': int(os.getenv('POSTGRES_PORT', '5434')),
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'dbname': os.getenv('POSTGRES_DB')
}

def main():
    conn = psycopg.connect(**DB_CONFIG, row_factory=dict_row)
    cursor = conn.cursor()
    
    try:
        # Get Platinum's character ID
        cursor.execute("SELECT id FROM characters WHERE name = 'Kent Jefferies'")
        char = cursor.fetchone()
        if not char:
            print("Platinum not found!")
            return
        
        char_id = char['id']
        print(f"Found Platinum: {char_id}")
        
        # Update cyberware with essence costs
        print("\nUpdating cyberware essence costs...")
        cyberware_costs = {
            'Wired Reflexes 3 (Beta-Grade)': 2.4,
            'Reaction Enhancers 6 (Delta-Grade)': 1.2,
            'Cybereyes': 0.2,
            'Smartlink 2': 0.5,
            'Datajack (Delta-Grade)': 0.1
        }
        
        for name, essence_cost in cyberware_costs.items():
            cursor.execute("""
                UPDATE character_modifiers
                SET modifier_data = %s::jsonb
                WHERE character_id = %s 
                  AND source = %s 
                  AND source_type = 'cyberware'
            """, (
                json.dumps({'essence_cost': essence_cost}),
                char_id,
                name
            ))
            print(f"  ✓ Updated {name}: {essence_cost} essence")
        
        conn.commit()
        print("\n✅ Cyberware essence costs updated!")
        
        # Verify
        print("\nVerifying...")
        cursor.execute("""
            SELECT source, modifier_data
            FROM character_modifiers
            WHERE character_id = %s AND source_type = 'cyberware'
            ORDER BY source
        """, (char_id,))
        
        for row in cursor.fetchall():
            ess = row['modifier_data'].get('essence_cost', 0) if row['modifier_data'] else 0
            print(f"  {row['source']:40} Essence: {ess}")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
