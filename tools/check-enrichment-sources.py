#!/usr/bin/env python3
"""
Check what data is available in database for enrichment
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
    print("DATABASE ENRICHMENT SOURCES")
    print("="*70)
    
    # Check gear table
    cur.execute("SELECT COUNT(*) as count FROM gear")
    gear_count = cur.fetchone()['count']
    print(f"\nGear table: {gear_count} items")
    
    # Sample gear items
    cur.execute("SELECT name, category FROM gear WHERE category = 'Weapons' LIMIT 10")
    weapons = cur.fetchall()
    print("\nSample weapons in gear table:")
    for w in weapons:
        print(f"  - {w['name']}")
    
    # Check qualities table
    cur.execute("SELECT COUNT(*) as count FROM qualities")
    qual_count = cur.fetchone()['count']
    print(f"\nQualities table: {qual_count} items")
    
    # Sample qualities
    cur.execute("SELECT name FROM qualities LIMIT 10")
    qualities = cur.fetchall()
    print("\nSample qualities:")
    for q in qualities:
        print(f"  - {q['name']}")
    
    # Check for specific items we're trying to enrich
    print("\n" + "="*70)
    print("CHECKING SPECIFIC ITEMS")
    print("="*70)
    
    items_to_check = [
        ("Combat Axe", "gear", "name"),
        ("Monowhip", "gear", "name"),
        ("Aptitude", "qualities", "name"),
        ("Technical School", "qualities", "name"),
        ("Cybereyes", "gear", "name"),
    ]
    
    for item_name, table, column in items_to_check:
        cur.execute(f"SELECT COUNT(*) as count FROM {table} WHERE LOWER({column}) LIKE LOWER(%s)", (f"%{item_name}%",))
        count = cur.fetchone()['count']
        print(f"\n'{item_name}' in {table}: {count} matches")
        
        if count > 0:
            cur.execute(f"SELECT {column} FROM {table} WHERE LOWER({column}) LIKE LOWER(%s) LIMIT 3", (f"%{item_name}%",))
            matches = cur.fetchall()
            for match in matches:
                print(f"  - {match[column]}")
    
    conn.close()

if __name__ == "__main__":
    main()
