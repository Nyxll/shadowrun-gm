#!/usr/bin/env python3
"""
Export all characters from database to standardized markdown format
Creates character sheets in characters/ folder
"""
import os
import json
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row

load_dotenv()

def get_connection():
    return psycopg.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB'),
        row_factory=dict_row
    )

def format_character_sheet(char_data, skills, gear):
    """Format character data as standardized markdown"""
    
    # Get data from character record
    name = char_data['name']
    street_name = char_data.get('street_name') or name
    char_type = char_data.get('character_type', 'Unknown')
    archetype = char_data.get('archetype', 'Unknown')
    nuyen = char_data.get('nuyen', 0)
    karma_pool = char_data.get('karma_pool', 0)
    karma_total = char_data.get('karma_total', 0)
    initiative = char_data.get('initiative', 'Unknown')
    notes = char_data.get('notes', '')
    
    # Get attributes from JSONB
    attrs = char_data.get('attributes') or {}
    essence = attrs.get('essence', 6.0)
    magic = attrs.get('magic', 0)
    reaction = attrs.get('reaction', 0)
    
    # Get relationships data
    rels = char_data.get('relationships') or {}
    contacts = rels.get('contacts', [])
    edges = rels.get('edges', [])
    flaws = rels.get('flaws', [])
    spells = rels.get('spells', [])
    spell_formulas = rels.get('spell_formulas', [])
    adept_powers = rels.get('adept_powers', [])
    summoned_spirits = rels.get('summoned_spirits', [])
    weapons = rels.get('weapons', [])
    vehicles = rels.get('vehicles', [])
    deck = rels.get('deck')
    
    # Build markdown
    md = f"""# {name} ({street_name}) Character Sheet

## Basic Information

- **Name**: {name}
- **Street Name**: {street_name}
- **Race**: {char_type}
- **Archetype**: {archetype}
- **Description**: {notes or 'No description available'}
- **Nuyen**: {nuyen:,}¥
- **Karma Pool**: {karma_pool}
- **Total Karma Earned**: {karma_total}
- **Essence**: {essence}
- **Magic**: {magic}
- **Reaction**: {reaction}
- **Initiative**: {initiative}

## Attributes

"""
    
    # Add attributes
    attr_order = ['body', 'quickness', 'strength', 'charisma', 'intelligence', 'willpower']
    for attr in attr_order:
        if attr in attrs:
            value = attrs[attr]
            # Check for augmented value
            aug_key = f'{attr}_augmented'
            if aug_key in attrs:
                md += f"- **{attr.title()}**: {value} / {attrs[aug_key]}\n"
            else:
                md += f"- **{attr.title()}**: {value}\n"
    
    md += "\n## Skills\n\n"
    
    # Add skills
    if skills:
        for skill in sorted(skills, key=lambda s: s['skill_name']):
            spec = f" ({skill['specialization']} specialization)" if skill.get('specialization') else ""
            md += f"- **{skill['skill_name']}**: {skill['rating']}{spec}\n"
    else:
        md += "- No skills recorded\n"
    
    # Add edges and flaws
    if edges or flaws:
        md += "\n## Edges and Flaws\n\n"
        
        if edges:
            md += "- **Edges**:\n"
            for edge in edges:
                md += f"  - {edge}\n"
        
        if flaws:
            md += "- **Flaws**:\n"
            for flaw in flaws:
                md += f"  - {flaw}\n"
    
    # Add contacts
    if contacts:
        md += "\n## Contacts\n\n"
        for contact in contacts:
            md += f"- {contact}\n"
    
    # Add gear section
    md += "\n## Gear\n\n"
    
    # Weapons
    if weapons:
        md += "- **Weapons**:\n"
        for weapon in weapons:
            # Build weapon line with ALL details
            parts = []
            if weapon.get('conceal') is not None:
                parts.append(f"Conceal {weapon['conceal']}")
            if weapon.get('capacity'):
                parts.append(f"{weapon['capacity']}(c)")
            if weapon.get('mode'):
                parts.append(weapon['mode'])
            if weapon.get('damage'):
                parts.append(weapon['damage'])
            if weapon.get('tn_modifier'):
                parts.append(f"{weapon['tn_modifier']} TN")
            if weapon.get('reach') is not None:
                parts.append(f"Reach {weapon['reach']}")
            
            details = ", ".join(parts) if parts else "No stats"
            md += f"  - **{weapon['name']}** ({details})\n"
            
            # Add ammo
            if weapon.get('ammo'):
                for ammo in weapon['ammo']:
                    md += f"    - {ammo}\n"
            
            # Add modifications
            if weapon.get('modifications'):
                for mod in weapon['modifications']:
                    md += f"    - {mod}\n"
    
    # Vehicles
    if vehicles:
        md += "- **Vehicles**:\n"
        for vehicle in vehicles:
            parts = []
            if vehicle.get('handling'):
                parts.append(f"Handling {vehicle['handling']}")
            if vehicle.get('speed'):
                parts.append(f"Speed {vehicle['speed']}")
            if vehicle.get('body'):
                parts.append(f"Body {vehicle['body']}")
            if vehicle.get('armor'):
                parts.append(f"Armor {vehicle['armor']}")
            
            details = ", ".join(parts) if parts else "No stats"
            md += f"  - **{vehicle['name']}** ({details})\n"
    
    # Other gear (filter out weapons and vehicles that are already listed)
    if gear:
        # Get weapon and vehicle names for filtering
        weapon_names = {w['name'].lower() for w in weapons} if weapons else set()
        vehicle_names = {v['name'].lower() for v in vehicles} if vehicles else set()
        
        # Filter gear
        filtered_gear = []
        magical_items = []
        
        for item in gear:
            item_name = item['gear_name'].lower()
            
            # Skip if it's a weapon or vehicle already listed
            if any(wn in item_name for wn in weapon_names):
                continue
            if any(vn in item_name for vn in vehicle_names):
                continue
            
            # Check if it's a magical item
            magical_keywords = ['focus', 'foci', 'spell lock', 'fetish', 'talisman', 'power focus', 
                              'weapon focus', 'sustaining focus', 'elemental', 'spirit']
            if any(keyword in item_name for keyword in magical_keywords):
                magical_items.append(item)
            else:
                filtered_gear.append(item)
        
        # Magical Items section
        if magical_items:
            md += "- **Magical Items**:\n"
            for item in sorted(magical_items, key=lambda g: g['gear_name']):
                qty = f" x{item['quantity']}" if item.get('quantity', 1) > 1 else ""
                note = f" - {item['notes']}" if item.get('notes') else ""
                md += f"  - {item['gear_name']}{qty}{note}\n"
        
        # Regular equipment
        if filtered_gear:
            md += "- **Equipment**:\n"
            for item in sorted(filtered_gear, key=lambda g: g['gear_name']):
                qty = f" x{item['quantity']}" if item.get('quantity', 1) > 1 else ""
                note = f" - {item['notes']}" if item.get('notes') else ""
                md += f"  - {item['gear_name']}{qty}{note}\n"
    
    # Cyberware (from relationships)
    cyberware = rels.get('cyberware', [])
    if cyberware:
        md += "\n## Cyberware\n\n"
        for cyber in cyberware:
            essence_cost = cyber.get('essence', 0)
            details = cyber.get('details', '')
            md += f"- **{cyber['name']}** (Essence {essence_cost}, {details})\n"
    
    # Bioware
    bioware = rels.get('bioware', [])
    if bioware:
        md += "\n## Bioware\n\n"
        for bio in bioware:
            bi_cost = bio.get('body_index', 0)
            details = bio.get('details', '')
            md += f"- **{bio['name']}** (B.I. {bi_cost}, {details})\n"
    
    # Spells
    if spells:
        md += "\n## Spells\n\n"
        for spell in spells:
            md += f"- **{spell['name']}**: Force {spell.get('force', 0)}\n"
    
    # Spell Formulas
    if spell_formulas:
        md += "\n## Spell Formulas\n\n"
        formula_list = [f"{f['name']} {f.get('force', 0)}" for f in spell_formulas]
        md += f"- **Formulas**: {', '.join(formula_list)}\n"
    
    # Adept Powers
    if adept_powers:
        md += "\n## Adept Powers\n\n"
        for power in adept_powers:
            points = power.get('points', 0)
            details = power.get('details', '')
            md += f"- **{power['name']}**: {points} points ({details})\n"
    
    # Summoned Spirits
    if summoned_spirits:
        md += "\n## Summoned Spirits\n\n"
        for spirit in summoned_spirits:
            force = spirit.get('force', 0)
            services = spirit.get('services', 0)
            md += f"- **{spirit['type']}**: Force {force}, {services} services remaining\n"
    
    # Cyberdeck
    if deck:
        md += "\n## Matrix Stats\n\n"
        md += f"- **MPCP Rating**: {deck.get('mpcp', 0)}\n"
        md += f"- **Memory**: {deck.get('memory', 0)}\n"
        md += f"- **Hardening**: {deck.get('hardening', 0)}\n"
    
    return md

def main():
    """Export all characters to markdown files"""
    
    # Create characters directory
    os.makedirs('characters', exist_ok=True)
    
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Get all characters
        cur.execute("""
            SELECT * FROM characters
            WHERE name != 'Manticore' OR street_name IS NOT NULL
            ORDER BY name
        """)
        
        characters = cur.fetchall()
        
        print(f"Exporting {len(characters)} characters...\n")
        
        for char in characters:
            char_id = char['id']
            name = char['name']
            street_name = char.get('street_name') or name
            
            # Get skills
            cur.execute("""
                SELECT skill_name, rating, specialization
                FROM character_skills
                WHERE character_id = %s
                ORDER BY skill_name
            """, (char_id,))
            skills = cur.fetchall()
            
            # Get gear
            cur.execute("""
                SELECT gear_name, quantity, notes
                FROM character_gear
                WHERE character_id = %s
                ORDER BY gear_name
            """, (char_id,))
            gear = cur.fetchall()
            
            # Generate markdown
            markdown = format_character_sheet(char, skills, gear)
            
            # Save to file
            filename = f"characters/{street_name.replace(' ', '_')}.md"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(markdown)
            
            print(f"✓ Exported {name} ({street_name}) to {filename}")
        
        print(f"\n✓ All characters exported to characters/ folder")
        
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    main()
