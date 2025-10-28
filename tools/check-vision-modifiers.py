#!/usr/bin/env python3
"""
Check if vision modifiers are in the database
"""
import os
import psycopg2
from dotenv import load_dotenv

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
        
        # Check Axel's cybereyes modifiers
        print("="*70)
        print("AXEL - Cybereyes Modifiers")
        print("="*70)
        cur.execute("""
            SELECT cm.target_name, cm.modifier_value, cm.notes
            FROM character_modifiers cm
            JOIN characters c ON cm.character_id = c.id
            WHERE c.street_name = 'Axel'
            AND cm.source ILIKE '%cybereye%'
            ORDER BY cm.target_name
        """)
        
        for row in cur.fetchall():
            print(f"  {row[0]}: {row[1]}")
            if row[2]:
                print(f"    Notes: {row[2]}")
        
        # Check Platinum's cybereyes modifiers
        print("\n" + "="*70)
        print("PLATINUM - Cybereyes Modifiers")
        print("="*70)
        cur.execute("""
            SELECT cm.target_name, cm.modifier_value, cm.notes
            FROM character_modifiers cm
            JOIN characters c ON cm.character_id = c.id
            WHERE c.street_name = 'Platinum'
            AND cm.source ILIKE '%cybereye%'
            ORDER BY cm.target_name
        """)
        
        for row in cur.fetchall():
            print(f"  {row[0]}: {row[1]}")
            if row[2]:
                print(f"    Notes: {row[2]}")
        
        # Check what the API returns
        print("\n" + "="*70)
        print("API Data Check")
        print("="*70)
        
        for street_name in ['Axel', 'Platinum']:
            print(f"\n{street_name}:")
            cur.execute("""
                SELECT 
                    cm.source,
                    cm.target_name,
                    cm.modifier_value,
                    cm.modifier_data
                FROM character_modifiers cm
                JOIN characters c ON cm.character_id = c.id
                WHERE c.street_name = %s
                AND cm.source_type = 'cyberware'
                AND cm.source ILIKE '%eye%'
                ORDER BY cm.source, cm.target_name
            """, (street_name,))
            
            for row in cur.fetchall():
                print(f"  {row[0]}")
                print(f"    {row[1]}: {row[2]}")
                if row[3]:
                    print(f"    Data: {row[3]}")
        
    finally:
        conn.close()

if __name__ == "__main__":
    main()
