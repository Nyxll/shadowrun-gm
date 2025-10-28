#!/usr/bin/env python3
"""
Complete import of Platinum character with all bioware, vehicles, and detailed stats
"""
import os
import json
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv
from decimal import Decimal

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
            print("Platinum not found!")
            return
        
        char_id = char['id']
        print(f"Found Platinum: {char_id}")
        
        # Update base attributes (from character file)
        print("\nUpdating base attributes...")
        cursor.execute("""
            UPDATE characters SET
                base_body = 9,
                base_quickness = 10,
                base_strength = 9,
                base_charisma = 4,
                base_intelligence = 9,
                base_willpower = 9,
                base_essence = 6.0,
                base_reaction = 1,
                current_body = 10,
                current_quickness = 15,
                current_strength = 14,
                current_charisma = 4,
                current_intelligence = 12,
                current_willpower = 9,
                current_essence = 2.55,
                current_reaction = 27,
                age = NULL,
                skin = NULL
            WHERE id = %s
        """, (char_id,))
        print("✓ Base attributes updated")
        
        # Add missing bioware
        print("\nAdding bioware...")
        bioware_items = [
            {
                'name': 'Enhanced Articulation',
                'essence': 0,
                'body_index': 0.3,
                'effects': '+1 die to physical skills, +1 Reaction'
            },
            {
                'name': 'Cerebral Booster 3',
                'essence': 0,
                'body_index': 0.4,
                'effects': '+3 Intelligence'
            },
            {
                'name': 'Supra-Thyroid Gland',
                'essence': 0,
                'body_index': 1.4,
                'effects': '+1 Body, Quickness, Strength, Reaction'
            },
            {
                'name': 'Muscle Augmentation 4',
                'essence': 0,
                'body_index': 4.0,
                'effects': '+4 Quickness/Strength'
            },
            {
                'name': 'Damage Compensator 3',
                'essence': 0,
                'body_index': 0.75,
                'effects': 'Negates TN penalties for Physical or Mental monitor if boxes ≤ 3'
            },
            {
                'name': 'Reflex Recorder (Firearms)',
                'essence': 0,
                'body_index': 0.3,
                'effects': '+1 Firearms'
            },
            {
                'name': 'Mnemonic Enhancer 4',
                'essence': 0,
                'body_index': 1.2,
                'effects': '+2 dice to Knowledge/Language skills'
            }
        ]
        
        for item in bioware_items:
            # Check if already exists
            cursor.execute("""
                SELECT id FROM character_modifiers
                WHERE character_id = %s AND source = %s AND source_type = 'bioware'
            """, (char_id, item['name']))
            
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO character_modifiers 
                    (character_id, modifier_type, target_name, modifier_value, source, source_type, is_permanent, modifier_data)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb)
                """, (
                    char_id,
                    'bioware',
                    'body_index',
                    0,  # modifier_value not used for bioware display
                    item['name'],
                    'bioware',
                    True,
                    json.dumps({
                        'essence_cost': float(item['essence']),
                        'body_index_cost': float(item['body_index']),
                        'effects': item['effects']
                    })
                ))
                print(f"  ✓ Added {item['name']}")
        
        # Update skill base ratings
        print("\nUpdating skill base ratings...")
        skills_base = {
            'Gunnery': 5,
            'Athletics': 6,
            'Stealth': 6,
            'Firearms': 7,
            'Whips': 2,
            'Monowhip': 6,
            'Cars': 2,
            'Negotiation': 3,
            'Computers': 7,
            'Demolitions': 3,
            'Physical Sciences': 2,
            'Magical Theory': 2,
            'Military Theory': 2,
            'English': 6,
            'French': 2,
            'Cooking': 1
        }
        
        for skill_name, base_rating in skills_base.items():
            cursor.execute("""
                UPDATE character_skills
                SET base_rating = %s
                WHERE character_id = %s AND skill_name = %s
            """, (base_rating, char_id, skill_name))
        print("✓ Skill base ratings updated")
        
        # Add vehicles
        print("\nAdding vehicles...")
        vehicles = [
            {
                'name': 'GMC Bulldog Stepvan',
                'vehicle_type': 'Stepvan',
                'handling': '4/8',
                'speed': 90,
                'body': 8,
                'armor': 4
            },
            {
                'name': 'Eurocar Westwind',
                'vehicle_type': 'Car',
                'handling': '3/8',
                'speed': 210,
                'body': 8,
                'armor': 2
            }
        ]
        
        for vehicle in vehicles:
            cursor.execute("""
                SELECT id FROM character_vehicles
                WHERE character_id = %s AND vehicle_name = %s
            """, (char_id, vehicle['name']))
            
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO character_vehicles
                    (character_id, vehicle_name, vehicle_type, handling, speed, body, armor)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    char_id,
                    vehicle['name'],
                    vehicle['vehicle_type'],
                    vehicle['handling'],
                    vehicle['speed'],
                    vehicle['body'],
                    vehicle['armor']
                ))
                print(f"  ✓ Added {vehicle['name']}")
        
        # Update weapon stats in character_gear
        print("\nUpdating weapon stats...")
        weapon_stats = {
            'Morrissey Alta': {
                'damage': '12(c)',
                'type': 'Heavy Pistol',
                'conceal': 6,
                'ammo': '12(c)',
                'mode': 'SA',
                'modifications': {'smartgun': True, 'integrated': True}
            },
            'Monowhip': {
                'damage': '10S',
                'type': 'Melee (Whip)',
                'conceal': 10,
                'reach': 2
            },
            'Ares Alpha': {
                'damage': '7M',
                'type': 'Assault Rifle',
                'conceal': 2,
                'ammo': '42(c)',
                'mode': 'SA/BF/FA',
                'modifications': {'sound_suppressor': True, 'grenade_launcher': True}
            },
            'Armtech MGL-12': {
                'damage': 'By grenade type',
                'type': 'Grenade Launcher',
                'conceal': 'N/A'
            },
            'Panther Assault Cannon': {
                'damage': '18D',
                'type': 'Assault Cannon',
                'conceal': 'N/A',
                'modifications': {'smartlink': True}
            },
            'MP Laser 3': {
                'damage': '15M',
                'type': 'Laser Weapon',
                'conceal': 'N/A',
                'ammo': 20
            },
            'Walther MA-2100': {
                'damage': '14S',
                'type': 'Sniper Rifle',
                'conceal': 'N/A',
                'ammo': 20
            }
        }
        
        for weapon_name, stats in weapon_stats.items():
            cursor.execute("""
                UPDATE character_gear
                SET weapon_stats = %s::jsonb
                WHERE character_id = %s AND gear_name LIKE %s
            """, (json.dumps(stats), char_id, f'%{weapon_name}%'))
            print(f"  ✓ Updated {weapon_name}")
        
        conn.commit()
        print("\n✅ Platinum character data updated successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
