#!/usr/bin/env python3
"""
Fix Platinum's combat pool directly in the database
"""
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

def main():
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB')
    )
    
    cur = conn.cursor()
    
    # Find Platinum by name or street_name
    cur.execute("""
        SELECT id, name, street_name, 
               base_quickness, base_intelligence, base_willpower,
               current_quickness, current_intelligence, current_willpower,
               combat_pool, base_magic, current_magic
        FROM characters 
        WHERE LOWER(name) LIKE '%platinum%' OR LOWER(street_name) LIKE '%platinum%'
    """)
    
    results = cur.fetchall()
    
    if not results:
        print("No Platinum character found!")
        print("\nSearching for all characters...")
        cur.execute("SELECT id, name, street_name FROM characters ORDER BY name")
        all_chars = cur.fetchall()
        print(f"\nFound {len(all_chars)} characters:")
        for char in all_chars[:10]:
            print(f"  - {char[1]} (street: {char[2]})")
        conn.close()
        return
    
    for row in results:
        char_id, name, street_name, base_q, base_i, base_w, curr_q, curr_i, curr_w, combat_pool, base_magic, curr_magic = row
        
        print(f"\nFound: {name} (street: {street_name})")
        print(f"  ID: {char_id}")
        print(f"  Base Attributes: Q={base_q}, I={base_i}, W={base_w}")
        print(f"  Current Attributes: Q={curr_q}, I={curr_i}, W={curr_w}")
        print(f"  Current Combat Pool: {combat_pool}")
        print(f"  Magic: base={base_magic}, current={curr_magic}")
        
        # Calculate correct combat pool
        # Use current attributes (which include cyberware/bioware modifiers)
        q = curr_q or base_q or 1
        i = curr_i or base_i or 1
        w = curr_w or base_w or 1
        
        correct_combat_pool = (q + i + w) // 2
        magic_pool = curr_magic if curr_magic else 0
        
        print(f"\n  Calculated Combat Pool: ({q} + {i} + {w}) / 2 = {correct_combat_pool}")
        print(f"  Calculated Magic Pool: {magic_pool}")
        
        if combat_pool != correct_combat_pool:
            print(f"\n  FIXING: Updating combat pool from {combat_pool} to {correct_combat_pool}")
            cur.execute("""
                UPDATE characters 
                SET combat_pool = %s, magic_pool = %s
                WHERE id = %s
            """, (correct_combat_pool, magic_pool, char_id))
            conn.commit()
            print("  ✓ Updated!")
        else:
            print("\n  Combat pool is already correct!")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
