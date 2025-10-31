#!/usr/bin/env python3
"""
Add Platinum's custom cyberware to house rules
- Smartlink-3 AEGIS
- NeuroSync Processor
- SR2 Visibility Table
"""
import os
import sys
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import Json

# Load environment variables
load_dotenv()

def add_house_rules():
    """Add custom cyberware house rules"""
    try:
        conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST'),
            port=os.getenv('POSTGRES_PORT'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            dbname=os.getenv('POSTGRES_DB')
        )
        cur = conn.cursor()
        
        # 1. Smartlink-3 AEGIS
        print("Adding Smartlink-3 AEGIS house rule...")
        cur.execute("SELECT id FROM house_rules WHERE rule_name = 'Smartlink-3 AEGIS'")
        if cur.fetchone():
            print("  Already exists, updating...")
            cur.execute("""
                UPDATE house_rules SET
                    description = %s,
                    rule_config = %s,
                    is_active = true,
                    notes = %s
                WHERE rule_name = 'Smartlink-3 AEGIS'
            """, (
                'Enhanced smartlink system with Project Aegis software integration. Provides superior targeting assistance beyond standard smartlink-2 systems.',
                Json({
                    'essence_cost': 0.5,
                    'tn_modifier': -3,
                    'gunnery_bonus': 1,
                    'special_abilities': [
                        'Grenade launcher bonus (no scatter on direct hits)',
                        'No magazine size penalty',
                        'Enhanced target tracking',
                        'Integrated with Project Aegis software'
                    ]
                }),
                'Custom enhancement for Platinum. Standard smartlink is -2 TN, this is -3 TN. HOMEBREW.'
            ))
        else:
            print("  Creating new...")
            cur.execute("""
                INSERT INTO house_rules (rule_name, rule_type, description, rule_config, is_active, notes)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                'Smartlink-3 AEGIS',
                'custom',
                'Enhanced smartlink system with Project Aegis software integration. Provides superior targeting assistance beyond standard smartlink-2 systems.',
                Json({
                    'essence_cost': 0.5,
                    'tn_modifier': -3,
                    'gunnery_bonus': 1,
                    'special_abilities': [
                        'Grenade launcher bonus (no scatter on direct hits)',
                        'No magazine size penalty',
                        'Enhanced target tracking',
                        'Integrated with Project Aegis software'
                    ]
                }),
                True,
                'Custom enhancement for Platinum. Standard smartlink is -2 TN, this is -3 TN. HOMEBREW.'
            ))
        
        # 2. NeuroSync Processor
        print("Adding NeuroSync Processor house rule...")
        cur.execute("SELECT id FROM house_rules WHERE rule_name = 'NeuroSync Processor'")
        if cur.fetchone():
            print("  Already exists, updating...")
            cur.execute("""
                UPDATE house_rules SET
                    description = %s,
                    rule_config = %s,
                    is_active = true,
                    notes = %s
                WHERE rule_name = 'NeuroSync Processor'
            """, (
                'Advanced neural processor that enhances Matrix interface capabilities. Provides significant boost to Matrix initiative through optimized neural pathways.',
                Json({
                    'essence_cost': 0.5,
                    'body_index_cost': 0.5,
                    'matrix_initiative_bonus': '2D6'
                }),
                'Custom cyberware for deckers. Adds +2D6 to Matrix Initiative rolls. HOMEBREW.'
            ))
        else:
            print("  Creating new...")
            cur.execute("""
                INSERT INTO house_rules (rule_name, rule_type, description, rule_config, is_active, notes)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                'NeuroSync Processor',
                'custom',
                'Advanced neural processor that enhances Matrix interface capabilities. Provides significant boost to Matrix initiative through optimized neural pathways.',
                Json({
                    'essence_cost': 0.5,
                    'body_index_cost': 0.5,
                    'matrix_initiative_bonus': '2D6'
                }),
                True,
                'Custom cyberware for deckers. Adds +2D6 to Matrix Initiative rolls. HOMEBREW.'
            ))
        
        # 3. SR2 Visibility Table
        print("Adding SR2 Visibility Table house rule...")
        visibility_table = {
            'Full Darkness': {
                'Normal': 8,
                'Cybernetic Low-Light': 8,
                'Natural Low-Light': 8,
                'Cybernetic Thermographic': 4,
                'Natural Thermographic': 2
            },
            'Minimal Light': {
                'Normal': 5,
                'Cybernetic Low-Light': 4,
                'Natural Low-Light': 2,
                'Cybernetic Thermographic': 4,
                'Natural Thermographic': 2
            },
            'Partial Light': {
                'Normal': 2,
                'Cybernetic Low-Light': 2,
                'Natural Low-Light': 1,
                'Cybernetic Thermographic': 2,
                'Natural Thermographic': 1
            },
            'Glare': {
                'Normal': 2,
                'Cybernetic Low-Light': 2,
                'Natural Low-Light': 0,
                'Cybernetic Thermographic': 0,
                'Natural Thermographic': 0
            },
            'Mist': {
                'Normal': 4,
                'Cybernetic Low-Light': 4,
                'Natural Low-Light': 2,
                'Cybernetic Thermographic': 0,
                'Natural Thermographic': 0
            },
            'Light Smoke/Fog/Rain': {
                'Normal': 4,
                'Cybernetic Low-Light': 4,
                'Natural Low-Light': 2,
                'Cybernetic Thermographic': 0,
                'Natural Thermographic': 0
            },
            'Heavy Smoke/Fog/Rain': {
                'Normal': 6,
                'Cybernetic Low-Light': 6,
                'Natural Low-Light': 4,
                'Cybernetic Thermographic': 1,
                'Natural Thermographic': 0
            },
            'Thermal Smoke': {
                'Normal': 'As smoke',
                'Cybernetic Low-Light': 'As smoke',
                'Natural Low-Light': 'As smoke',
                'Cybernetic Thermographic': 'As smoke',
                'Natural Thermographic': 'As normal light'
            }
        }
        
        cur.execute("SELECT id FROM house_rules WHERE rule_name = 'SR2 Visibility Modifiers'")
        if cur.fetchone():
            print("  Already exists, updating...")
            cur.execute("""
                UPDATE house_rules SET
                    description = %s,
                    rule_config = %s,
                    is_active = true,
                    notes = %s
                WHERE rule_name = 'SR2 Visibility Modifiers'
            """, (
                'Official Shadowrun 2nd Edition visibility modifier table. Defines TN modifiers for various lighting and environmental conditions based on vision type.',
                Json({'table': visibility_table}),
                'Ultrasound vision ignores all visibility penalties. Natural vision types are superior to cybernetic equivalents. OFFICIAL SR2 RULES.'
            ))
        else:
            print("  Creating new...")
            cur.execute("""
                INSERT INTO house_rules (rule_name, rule_type, description, rule_config, is_active, notes)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                'SR2 Visibility Modifiers',
                'custom',
                'Official Shadowrun 2nd Edition visibility modifier table. Defines TN modifiers for various lighting and environmental conditions based on vision type.',
                Json({'table': visibility_table}),
                True,
                'Ultrasound vision ignores all visibility penalties. Natural vision types are superior to cybernetic equivalents. OFFICIAL SR2 RULES.'
            ))
        
        conn.commit()
        print("\n✓ Successfully added all house rules!")
        
        # Verify
        cur.execute("SELECT rule_name, rule_type, notes FROM house_rules WHERE rule_name IN ('Smartlink-3 AEGIS', 'NeuroSync Processor', 'SR2 Visibility Modifiers')")
        rules = cur.fetchall()
        print("\nAdded rules:")
        for rule in rules:
            homebrew = '[HOMEBREW]' if 'HOMEBREW' in (rule[2] or '') else '[OFFICIAL]'
            print(f"  - {rule[0]} ({rule[1]}) {homebrew}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")
        raise

if __name__ == "__main__":
    add_house_rules()
