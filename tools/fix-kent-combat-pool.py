#!/usr/bin/env python3
"""
Fix Kent Jefferies (Platinum) combat pool in database
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
    
    try:
        cur = conn.cursor()
        
        # Get current stats
        cur.execute("""
            SELECT name, street_name, combat_pool, current_quickness, 
                   current_intelligence, current_willpower
            FROM characters 
            WHERE name='Kent Jefferies'
        """)
        
        result = cur.fetchone()
        
        if result:
            name, street_name, old_combat_pool, quickness, intelligence, willpower = result
            
            # Calculate correct combat pool
            new_combat_pool = (quickness + intelligence + willpower) // 2
            
            print(f"Character: {name} ({street_name})")
            print(f"Attributes: Q={quickness}, I={intelligence}, W={willpower}")
            print(f"Old Combat Pool: {old_combat_pool}")
            print(f"New Combat Pool: {new_combat_pool}")
            
            # Update the database
            cur.execute("""
                UPDATE characters 
                SET combat_pool = %s
                WHERE name = 'Kent Jefferies'
            """, (new_combat_pool,))
            
            conn.commit()
            print(f"\n✓ Updated combat pool to {new_combat_pool}")
            
        else:
            print("Kent Jefferies character not found!")
        
        cur.close()
    finally:
        conn.close()

if __name__ == "__main__":
    main()
