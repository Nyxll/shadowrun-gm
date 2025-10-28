#!/usr/bin/env python3
"""
Check completeness of character data to understand what needs enrichment
"""
import os
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row

load_dotenv()

def main():
    conn = psycopg.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB'),
        row_factory=dict_row
    )
    
    cur = conn.cursor()
    
    print("="*70)
    print("CHARACTER DATA COMPLETENESS CHECK")
    print("="*70)
    
    # Check Platinum's weapons
    print("\n" + "="*70)
    print("PLATINUM'S WEAPONS")
    print("="*70)
    
    cur.execute("""
        SELECT gear_name, damage, conceal, ammo_capacity, notes
        FROM character_gear
        WHERE character_id = (SELECT id FROM characters WHERE street_name = 'Platinum')
        AND gear_type = 'weapon'
    """)
    
    weapons = cur.fetchall()
    for w in weapons:
        print(f"\n{w['gear_name']}:")
        print(f"  Damage: {w['damage'] or 'MISSING'}")
        print(f"  Conceal: {w['conceal'] or 'MISSING'}")
        print(f"  Ammo: {w['ammo_capacity'] or 'MISSING'}")
        print(f"  Notes: {w['notes'] or 'None'}")
    
    # Check Platinum's cyberware
    print("\n" + "="*70)
    print("PLATINUM'S CYBERWARE")
    print("="*70)
    
    cur.execute("""
        SELECT source, essence_cost, modifier_data
        FROM character_modifiers
        WHERE character_id = (SELECT id FROM characters WHERE street_name = 'Platinum')
        AND source_type = 'cyberware'
    """)
    
    cyberware = cur.fetchall()
    for c in cyberware:
        print(f"\n{c['source']}:")
        print(f"  Essence: {c['essence_cost']}")
        print(f"  Data: {c['modifier_data']}")
    
    # Check what's in gear table for Monowhip
    print("\n" + "="*70)
    print("MONOWHIP IN GEAR TABLE")
    print("="*70)
    
    cur.execute("""
        SELECT name, category, base_stats, description
        FROM gear
        WHERE LOWER(name) LIKE '%monowhip%'
    """)
    
    monowhips = cur.fetchall()
    for m in monowhips:
        print(f"\n{m['name']}:")
        print(f"  Category: {m['category']}")
        print(f"  Stats: {m['base_stats']}")
        print(f"  Description: {m['description'][:100] if m['description'] else 'None'}...")
    
    conn.close()

if __name__ == "__main__":
    main()
