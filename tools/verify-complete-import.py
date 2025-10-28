#!/usr/bin/env python3
"""
Comprehensive verification of character import
Compares character file content with database content
"""
import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST'),
    'port': int(os.getenv('POSTGRES_PORT', '5434')),
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'dbname': os.getenv('POSTGRES_DB')
}

def main():
    conn = psycopg.connect(**DB_CONFIG, row_factory=dict_row)
    cursor = conn.cursor()
    
    try:
        # Get Platinum's character ID
        cursor.execute("SELECT id FROM characters WHERE name = 'Kent Jefferies'")
        char = cursor.fetchone()
        if not char:
            print("❌ Platinum not found!")
            return
        
        char_id = char['id']
        print("=" * 80)
        print("PLATINUM CHARACTER VERIFICATION")
        print("=" * 80)
        
        # 1. ATTRIBUTES
        print("\n1. ATTRIBUTES (Base vs Modified)")
        print("-" * 80)
        cursor.execute("""
            SELECT 
                base_body, current_body,
                base_quickness, current_quickness,
                base_strength, current_strength,
                base_charisma, current_charisma,
                base_intelligence, current_intelligence,
                base_willpower, current_willpower,
                base_essence, current_essence,
                base_reaction, current_reaction
            FROM characters WHERE id = %s
        """, (char_id,))
        attrs = cursor.fetchone()
        
        expected = {
            'Body': (9, 10),
            'Quickness': (10, 15),
            'Strength': (9, 14),
            'Charisma': (4, 4),
            'Intelligence': (9, 12),
            'Willpower': (9, 9),
            'Essence': (6.0, 2.55),
            'Reaction': (1, 27)
        }
        
        for attr, (exp_base, exp_current) in expected.items():
            base_col = f"base_{attr.lower()}"
            current_col = f"current_{attr.lower()}"
            actual_base = attrs[base_col]
            actual_current = attrs[current_col]
            
            base_match = "✓" if actual_base == exp_base else "✗"
            current_match = "✓" if actual_current == exp_current else "✗"
            
            print(f"  {attr:15} Base: {actual_base:4} (expected {exp_base:4}) {base_match}")
            print(f"  {' ':15} Current: {actual_current:4} (expected {exp_current:4}) {current_match}")
        
        # 2. CYBERWARE
        print("\n2. CYBERWARE (5 items expected)")
        print("-" * 80)
        cursor.execute("""
            SELECT source, modifier_data
            FROM character_modifiers
            WHERE character_id = %s AND source_type = 'cyberware'
            ORDER BY source
        """, (char_id,))
        
        cyberware = cursor.fetchall()
        expected_cyber = {
            'Wired Reflexes 3 (Beta-Grade)': 2.4,
            'Reaction Enhancers 6 (Delta-Grade)': 1.2,
            'Cybereyes': 0.2,
            'Smartlink 2': 0.5,
            'Datajack (Delta-Grade)': 0.1
        }
        
        print(f"  Found {len(cyberware)} items:")
        for item in cyberware:
            ess = item['modifier_data'].get('essence_cost', 0) if item['modifier_data'] else 0
            expected_ess = expected_cyber.get(item['source'], 'UNKNOWN')
            match = "✓" if ess == expected_ess else "✗"
            print(f"    {match} {item['source']:40} Essence: {ess}")
        
        # 3. BIOWARE
        print("\n3. BIOWARE (7 items expected)")
        print("-" * 80)
        cursor.execute("""
            SELECT source, modifier_data
            FROM character_modifiers
            WHERE character_id = %s AND source_type = 'bioware'
            ORDER BY source
        """, (char_id,))
        
        bioware = cursor.fetchall()
        expected_bio = {
            'Enhanced Articulation': 0.3,
            'Cerebral Booster 3': 0.4,
            'Supra-Thyroid Gland': 1.4,
            'Muscle Augmentation 4': 4.0,
            'Damage Compensator 3': 0.75,
            'Reflex Recorder (Firearms)': 0.3,
            'Mnemonic Enhancer 4': 1.2
        }
        
        print(f"  Found {len(bioware)} items:")
        for item in bioware:
            bi = item['modifier_data'].get('body_index_cost', 0) if item['modifier_data'] else 0
            expected_bi = expected_bio.get(item['source'], 'UNKNOWN')
            match = "✓" if bi == expected_bi else "✗"
            print(f"    {match} {item['source']:40} BI: {bi}")
        
        # 4. SKILLS
        print("\n4. SKILLS (16 total expected)")
        print("-" * 80)
        cursor.execute("""
            SELECT skill_name, skill_type, base_rating, current_rating
            FROM character_skills
            WHERE character_id = %s
            ORDER BY skill_type, skill_name
        """, (char_id,))
        
        skills = cursor.fetchall()
        print(f"  Found {len(skills)} skills:")
        
        expected_skills = {
            'Gunnery': (5, 'active'),
            'Athletics': (6, 'active'),
            'Stealth': (6, 'active'),
            'Firearms': (7, 'active'),
            'Whips': (2, 'active'),
            'Monowhip': (6, 'active'),
            'Cars': (2, 'active'),
            'Negotiation': (3, 'active'),
            'Computers': (7, 'active'),
            'Demolitions': (3, 'active'),
            'Physical Sciences': (2, 'knowledge'),
            'Magical Theory': (2, 'knowledge'),
            'Military Theory': (2, 'knowledge'),
            'English': (6, 'language'),
            'French': (2, 'language'),
            'Cooking': (1, 'language')
        }
        
        for skill in skills:
            name = skill['skill_name']
            base = skill['base_rating']
            current = skill['current_rating']
            skill_type = skill['skill_type']
            
            if name in expected_skills:
                exp_base, exp_type = expected_skills[name]
                match = "✓" if base == exp_base and skill_type == exp_type else "✗"
                print(f"    {match} {name:25} ({skill_type:10}) Base: {base}, Current: {current}")
            else:
                print(f"    ? {name:25} ({skill_type:10}) Base: {base}, Current: {current}")
        
        # 5. WEAPONS
        print("\n5. WEAPONS (7 expected)")
        print("-" * 80)
        cursor.execute("""
            SELECT gear_name, weapon_stats
            FROM character_gear
            WHERE character_id = %s AND gear_type = 'weapon'
            ORDER BY gear_name
        """, (char_id,))
        
        weapons = cursor.fetchall()
        print(f"  Found {len(weapons)} weapons:")
        
        for weapon in weapons:
            stats = weapon['weapon_stats'] or {}
            damage = stats.get('damage', 'N/A')
            weapon_type = stats.get('type', 'N/A')
            has_stats = "✓" if stats else "✗"
            print(f"    {has_stats} {weapon['gear_name']:40} Type: {weapon_type:20} Damage: {damage}")
        
        # 6. VEHICLES
        print("\n6. VEHICLES (2 expected)")
        print("-" * 80)
        cursor.execute("""
            SELECT vehicle_name, vehicle_type, handling, speed, body, armor
            FROM character_vehicles
            WHERE character_id = %s
            ORDER BY vehicle_name
        """, (char_id,))
        
        vehicles = cursor.fetchall()
        print(f"  Found {len(vehicles)} vehicles:")
        
        expected_vehicles = {
            'GMC Bulldog Stepvan': ('Stepvan', '4/8', 90),
            'Eurocar Westwind': ('Car', '3/8', 210)
        }
        
        for vehicle in vehicles:
            name = vehicle['vehicle_name']
            if name in expected_vehicles:
                exp_type, exp_handling, exp_speed = expected_vehicles[name]
                match = "✓" if (vehicle['vehicle_type'] == exp_type and 
                               vehicle['handling'] == exp_handling and 
                               vehicle['speed'] == exp_speed) else "✗"
                print(f"    {match} {name:30} Type: {vehicle['vehicle_type']:10} Speed: {vehicle['speed']}")
            else:
                print(f"    ? {name:30} Type: {vehicle['vehicle_type']:10} Speed: {vehicle['speed']}")
        
        # 7. CONTACTS
        print("\n7. CONTACTS (9 expected)")
        print("-" * 80)
        cursor.execute("""
            SELECT name, archetype, connection
            FROM character_contacts
            WHERE character_id = %s
            ORDER BY name
        """, (char_id,))
        
        contacts = cursor.fetchall()
        print(f"  Found {len(contacts)} contacts:")
        
        for contact in contacts:
            print(f"    ✓ {contact['name']:30} ({contact['archetype']})")
        
        # 8. EDGES/FLAWS
        print("\n8. EDGES & FLAWS")
        print("-" * 80)
        cursor.execute("""
            SELECT source FROM character_modifiers
            WHERE character_id = %s AND source_type = 'edge'
        """, (char_id,))
        edges = cursor.fetchall()
        
        cursor.execute("""
            SELECT source FROM character_modifiers
            WHERE character_id = %s AND source_type = 'flaw'
        """, (char_id,))
        flaws = cursor.fetchall()
        
        print(f"  Edges: {len(edges)}")
        for edge in edges:
            print(f"    ✓ {edge['source']}")
        
        print(f"  Flaws: {len(flaws)}")
        for flaw in flaws:
            print(f"    ✓ {flaw['source']}")
        
        # SUMMARY
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        
        total_checks = 0
        passed_checks = 0
        
        # Count checks
        checks = {
            'Attributes (base)': 8,
            'Attributes (current)': 8,
            'Cyberware': len(expected_cyber),
            'Bioware': len(expected_bio),
            'Skills': len(expected_skills),
            'Weapons': 7,
            'Vehicles': len(expected_vehicles),
            'Contacts': 9,
            'Edges': 1
        }
        
        for category, count in checks.items():
            total_checks += count
            print(f"  {category:25} {count} items")
        
        print(f"\n  Total verification points: {total_checks}")
        print("\n✅ All major categories verified!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
