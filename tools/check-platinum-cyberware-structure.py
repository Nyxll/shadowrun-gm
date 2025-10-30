#!/usr/bin/env python3
"""
Check the actual structure of Platinum's cyberware/bioware from the API
"""
import os
from dotenv import load_dotenv
import psycopg2
import json

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
    
    # Get Platinum's id
    cur.execute("SELECT id FROM characters WHERE street_name = 'Platinum'")
    char_id = cur.fetchone()[0]
    
    print("="*80)
    print("PLATINUM'S CYBERWARE FROM DATABASE")
    print("="*80)
    
    # Get cyberware
    cur.execute("""
        SELECT source, modifier_type, modifier_data, effects
        FROM character_modifiers
        WHERE character_id = %s AND source_type = 'cyberware'
        ORDER BY source
    """, (char_id,))
    
    cyberware = cur.fetchall()
    for source, mod_type, mod_data, effects in cyberware:
        print(f"\nSource: {source}")
        print(f"Type: {mod_type}")
        print(f"Data: {json.dumps(mod_data, indent=2)}")
        print(f"Effects: {effects}")
    
    print("\n" + "="*80)
    print("PLATINUM'S BIOWARE FROM DATABASE")
    print("="*80)
    
    # Get bioware
    cur.execute("""
        SELECT source, modifier_type, modifier_data, effects
        FROM character_modifiers
        WHERE character_id = %s AND source_type = 'bioware'
        ORDER BY source
    """, (char_id,))
    
    bioware = cur.fetchall()
    for source, mod_type, mod_data, effects in bioware:
        print(f"\nSource: {source}")
        print(f"Type: {mod_type}")
        print(f"Data: {json.dumps(mod_data, indent=2)}")
        print(f"Effects: {effects}")
    
    conn.close()

if __name__ == "__main__":
    main()
