#!/usr/bin/env python3
"""Check all magic fields for Oak character"""
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=os.getenv('POSTGRES_PORT'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    dbname=os.getenv('POSTGRES_DB')
)

cur = conn.cursor()

# Get Oak's magic fields
cur.execute("""
    SELECT 
        name, 
        current_magic as magic_rating,
        magic_pool,
        spell_pool,
        initiate_level,
        metamagics,
        magical_group,
        tradition,
        totem
    FROM characters 
    WHERE name = 'Simon Stalman' OR street_name = 'Oak'
""")

row = cur.fetchone()
if row:
    print("Oak (Simon Stalman) Magic Fields:")
    print("=" * 60)
    print(f"  Magic Rating: {row[1]}")
    print(f"  Magic Pool: {row[2]}")
    print(f"  Spell Pool: {row[3]}")
    print(f"  Initiate Level: {row[4]}")
    print(f"  Metamagics: {row[5]}")
    print(f"  Magical Group: {row[6]}")
    print(f"  Tradition: {row[7]}")
    print(f"  Totem: {row[8]}")
    print()
    
    # Check spells
    cur.execute("""
        SELECT spell_name, spell_category, spell_type
        FROM character_spells
        WHERE character_id = (SELECT id FROM characters WHERE name = 'Simon Stalman')
        ORDER BY spell_name
    """)
    
    spells = cur.fetchall()
    print(f"  Spells ({len(spells)}):")
    for spell in spells:
        print(f"    - {spell[0]} ({spell[1]}, {spell[2]})")
    print()
    
    # Check spirits
    cur.execute("""
        SELECT spirit_name, spirit_type, force, services
        FROM character_spirits
        WHERE character_id = (SELECT id FROM characters WHERE name = 'Simon Stalman')
    """)
    
    spirits = cur.fetchall()
    print(f"  Bound Spirits ({len(spirits)}):")
    for spirit in spirits:
        services = "Permanent" if spirit[3] == -1 else str(spirit[3])
        print(f"    - {spirit[0]} (Force {spirit[2]}, {services} services)")
else:
    print("Oak character not found!")

conn.close()
