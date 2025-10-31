#!/usr/bin/env python3
"""
Check Kent Jefferies (Platinum) pools in database
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
        
        # Get Kent Jefferies stats
        cur.execute("""
            SELECT name, street_name, combat_pool, current_quickness, 
                   current_intelligence, current_willpower, karma_pool, magic_pool
            FROM characters 
            WHERE name='Kent Jefferies'
        """)
        
        result = cur.fetchone()
        
        if result:
            name, street_name, combat_pool, quickness, intelligence, willpower, karma_pool, magic_pool = result
            
            # SR2 Combat Pool = (Quickness + Intelligence + Willpower) / 2 (round down)
            calculated_combat_pool = (quickness + intelligence + willpower) // 2
            
            print(f"Character: {name} ({street_name})")
            print(f"\nAttributes:")
            print(f"  Quickness: {quickness}")
            print(f"  Intelligence: {intelligence}")
            print(f"  Willpower: {willpower}")
            print(f"\nPools:")
            print(f"  Combat Pool (stored in DB): {combat_pool}")
            print(f"  Combat Pool (calculated): {calculated_combat_pool}")
            print(f"  Karma Pool: {karma_pool}")
            print(f"  Magic Pool: {magic_pool}")
            print(f"\nCalculation: ({quickness} + {intelligence} + {willpower}) / 2 = {calculated_combat_pool}")
            
            if combat_pool != calculated_combat_pool:
                print(f"\n⚠️  MISMATCH! Stored value ({combat_pool}) != Calculated value ({calculated_combat_pool})")
                print(f"   Need to update database to {calculated_combat_pool}")
            else:
                print(f"\n✓ Combat pool is correct!")
        else:
            print("Kent Jefferies character not found!")
        
        cur.close()
    finally:
        conn.close()

if __name__ == "__main__":
    main()
