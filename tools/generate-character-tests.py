#!/usr/bin/env python3
"""
Generate comprehensive test suite from actual character data
Reads character markdown files and database to create complete test cases
"""
import os
import re
from pathlib import Path
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row

load_dotenv()

def get_all_character_data():
    """Get all character data from database"""
    conn = psycopg.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB'),
        row_factory=dict_row
    )
    cursor = conn.cursor()
    
    # Get all characters
    cursor.execute("SELECT * FROM characters ORDER BY name")
    characters = cursor.fetchall()
    
    test_data = []
    
    for char in characters:
        char_id = char['id']
        char_name = char['name']
        
        # Get skills
        cursor.execute("SELECT * FROM character_skills WHERE character_id = %s", (char_id,))
        skills = cursor.fetchall()
        
        # Get cyberware
        cursor.execute("SELECT * FROM character_modifiers WHERE character_id = %s AND source_type = 'cyberware'", (char_id,))
        cyberware = cursor.fetchall()
        
        # Get bioware
        cursor.execute("SELECT * FROM character_modifiers WHERE character_id = %s AND source_type = 'bioware'", (char_id,))
        bioware = cursor.fetchall()
        
        # Get weapons
        cursor.execute("SELECT * FROM character_gear WHERE character_id = %s AND gear_type = 'weapon'", (char_id,))
        weapons = cursor.fetchall()
        
        # Get armor
        cursor.execute("SELECT * FROM character_gear WHERE character_id = %s AND gear_type = 'armor'", (char_id,))
        armor = cursor.fetchall()
        
        # Get contacts
        cursor.execute("SELECT * FROM character_contacts WHERE character_id = %s", (char_id,))
        contacts = cursor.fetchall()
        
        # Get vehicles
        cursor.execute("SELECT * FROM character_vehicles WHERE character_id = %s", (char_id,))
        vehicles = cursor.fetchall()
        
        # Get edges
        cursor.execute("SELECT * FROM character_edges_flaws WHERE character_id = %s AND type = 'edge'", (char_id,))
        edges = cursor.fetchall()
        
        # Get flaws
        cursor.execute("SELECT * FROM character_edges_flaws WHERE character_id = %s AND type = 'flaw'", (char_id,))
        flaws = cursor.fetchall()
        
        test_data.append({
            'character': dict(char),
            'skills': [dict(s) for s in skills],
            'cyberware': [dict(c) for c in cyberware],
            'bioware': [dict(b) for b in bioware],
            'weapons': [dict(w) for w in weapons],
            'armor': [dict(a) for a in armor],
            'contacts': [dict(c) for c in contacts],
            'vehicles': [dict(v) for v in vehicles],
            'edges': [dict(e) for e in edges],
            'flaws': [dict(f) for f in flaws]
        })
    
    conn.close()
    return test_data

def main():
    """Generate test data report"""
    print("Generating character test data...")
    print("=" * 70)
    
    test_data = get_all_character_data()
    
    for data in test_data:
        char = data['character']
        print(f"\n## {char['name']} ({char.get('street_name', 'N/A')})")
        print(f"   Metatype: {char.get('metatype', 'N/A')}")
        print(f"   Archetype: {char.get('archetype', 'N/A')}")
        print(f"   Skills: {len(data['skills'])}")
        print(f"   Cyberware: {len(data['cyberware'])}")
        print(f"   Bioware: {len(data['bioware'])}")
        print(f"   Weapons: {len(data['weapons'])}")
        print(f"   Armor: {len(data['armor'])}")
        print(f"   Contacts: {len(data['contacts'])}")
        print(f"   Vehicles: {len(data['vehicles'])}")
        print(f"   Edges: {len(data['edges'])}")
        print(f"   Flaws: {len(data['flaws'])}")
        
        # Show details
        if data['skills']:
            print(f"\n   Skills:")
            for skill in data['skills']:
                print(f"     - {skill['skill_name']}: {skill['base_rating']} ({skill['skill_type']})")
        
        if data['cyberware']:
            print(f"\n   Cyberware:")
            for cyber in data['cyberware']:
                print(f"     - {cyber['source']}: {cyber.get('essence_cost', 0)} Essence")
        
        if data['bioware']:
            print(f"\n   Bioware:")
            for bio in data['bioware']:
                mod_data = bio.get('modifier_data', {})
                cost_info = []
                if mod_data and isinstance(mod_data, dict):
                    if 'essence_cost' in mod_data:
                        cost_info.append(f"{mod_data['essence_cost']} Essence")
                    if 'body_index_cost' in mod_data:
                        cost_info.append(f"{mod_data['body_index_cost']} BI")
                cost_str = ", ".join(cost_info) if cost_info else "N/A"
                print(f"     - {bio['source']}: {cost_str}")
        
        if data['weapons']:
            print(f"\n   Weapons:")
            for weapon in data['weapons']:
                print(f"     - {weapon['gear_name']}")
        
        if data['contacts']:
            print(f"\n   Contacts:")
            for contact in data['contacts']:
                print(f"     - {contact['name']}: {contact.get('archetype', 'N/A')}")

if __name__ == "__main__":
    main()
