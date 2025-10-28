#!/usr/bin/env python3
"""Check what data was imported for Platinum"""
import os
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row

load_dotenv()

conn = psycopg.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=os.getenv('POSTGRES_PORT'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    dbname=os.getenv('POSTGRES_DB'),
    row_factory=dict_row
)

cur = conn.cursor()

print("Checking Platinum character data...")
print("=" * 80)

# Check basic character info
cur.execute("""
    SELECT metatype, sex, age, height, weight, hair, eyes, 
           lifestyle, karma_available, combat_pool, body_index_current,
           background
    FROM characters 
    WHERE name='Kent Jefferies'
""")
char = cur.fetchone()

print("\nBasic Info:")
print(f"  Metatype: {char['metatype']}")
print(f"  Sex: {char['sex']}")
print(f"  Age: {char['age']}")
print(f"  Height: {char['height']}")
print(f"  Weight: {char['weight']}")
print(f"  Hair: {char['hair']}")
print(f"  Eyes: {char['eyes']}")
print(f"  Lifestyle: {char['lifestyle']}")
print(f"  Karma Available: {char['karma_available']}")
print(f"  Combat Pool: {char['combat_pool']}")
print(f"  Body Index: {char['body_index_current']}")
print(f"  Background: {char['background'][:50] if char['background'] else None}...")

# Check skills
cur.execute("""
    SELECT skill_name, skill_type, current_rating
    FROM character_skills
    WHERE character_id = (SELECT id FROM characters WHERE name='Kent Jefferies')
    ORDER BY skill_type, skill_name
""")
skills = cur.fetchall()
print(f"\nSkills: {len(skills)} total")
for skill in skills[:5]:
    print(f"  {skill['skill_name']} ({skill['skill_type']}): {skill['current_rating']}")
if len(skills) > 5:
    print(f"  ... and {len(skills) - 5} more")

# Check gear
cur.execute("""
    SELECT gear_name, gear_type, damage, conceal
    FROM character_gear
    WHERE character_id = (SELECT id FROM characters WHERE name='Kent Jefferies')
    ORDER BY gear_type, gear_name
    LIMIT 5
""")
gear = cur.fetchall()
print(f"\nGear: (showing first 5)")
for item in gear:
    print(f"  {item['gear_name']} ({item['gear_type']}): dmg={item['damage']}, conceal={item['conceal']}")

# Check modifiers (cyberware/bioware)
cur.execute("""
    SELECT source, source_type, essence_cost, body_index_cost
    FROM character_modifiers
    WHERE character_id = (SELECT id FROM characters WHERE name='Kent Jefferies')
""")
mods = cur.fetchall()
print(f"\nModifiers (Cyberware/Bioware): {len(mods)} total")
for mod in mods:
    print(f"  {mod['source']} ({mod['source_type']}): essence={mod['essence_cost']}, BI={mod['body_index_cost']}")

# Check contacts
cur.execute("""
    SELECT name, archetype, connection
    FROM character_contacts
    WHERE character_id = (SELECT id FROM characters WHERE name='Kent Jefferies')
""")
contacts = cur.fetchall()
print(f"\nContacts: {len(contacts)} total")
for contact in contacts:
    print(f"  {contact['name']} ({contact['archetype']}): Connection {contact['connection']}")

# Check vehicles
cur.execute("""
    SELECT vehicle_name, vehicle_type
    FROM character_vehicles
    WHERE character_id = (SELECT id FROM characters WHERE name='Kent Jefferies')
""")
vehicles = cur.fetchall()
print(f"\nVehicles: {len(vehicles)} total")
for vehicle in vehicles:
    print(f"  {vehicle['vehicle_name']} ({vehicle['vehicle_type']})")

# Check edges/flaws
cur.execute("""
    SELECT name, type
    FROM character_edges_flaws
    WHERE character_id = (SELECT id FROM characters WHERE name='Kent Jefferies')
""")
edges_flaws = cur.fetchall()
print(f"\nEdges/Flaws: {len(edges_flaws)} total")
for ef in edges_flaws:
    print(f"  {ef['name']} ({ef['type']})")

cur.close()
conn.close()

print("\n" + "=" * 80)
