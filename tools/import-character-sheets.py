#!/usr/bin/env python3
"""
Import character sheets from markdown files into the database
Parses markdown format and updates existing records
"""
import os
import re
import json
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row

load_dotenv()

# Database connection
def get_connection():
    return psycopg.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB'),
        row_factory=dict_row
    )

def parse_character_markdown(filepath):
    """Parse markdown character sheet into structured data"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    character = {
        'name': None,
        'street_name': None,
        'archetype': None,
        'character_type': None,
        'description': None,
        'nuyen': 0,
        'karma_pool': 0,
        'karma_total': 0,
        'essence': 6.0,
        'magic': 0,
        'reaction': 0,
        'initiative': None,
        'initiate_level': 0,
        'tradition': None,
        'attributes': {},
        'skills': [],
        'gear': [],
        'contacts': [],
        'edges': [],
        'flaws': [],
        'cyberware': [],
        'bioware': [],
        'spells': [],
        'spell_formulas': [],
        'adept_powers': [],
        'summoned_spirits': [],
        'magical_items': [],
        'weapons': [],
        'armor': [],
        'vehicles': [],
        'drones': [],
        'deck': None,
        'notes': []
    }
    
    # Extract title/name
    title_match = re.search(r'^#\s+(.+?)(?:\s+Character Sheet)?$', content, re.MULTILINE)
    if title_match:
        title = title_match.group(1).strip()
        # Handle "Name (Street Name)" format
        if '(' in title and ')' in title:
            parts = re.match(r'(.+?)\s*\((.+?)\)', title)
            if parts:
                character['name'] = parts.group(1).strip()
                character['street_name'] = parts.group(2).strip()
        else:
            character['name'] = title
    
    # Extract basic information section
    basic_info = re.search(r'##\s+Basic Information\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
    if basic_info:
        info_text = basic_info.group(1)
        
        # Extract fields
        for line in info_text.split('\n'):
            line = line.strip()
            if not line or not line.startswith('-'):
                continue
            
            # Parse "- **Field**: Value" format
            match = re.match(r'-\s+\*\*(.+?)\*\*:\s*(.+)', line)
            if match:
                field = match.group(1).strip()
                value = match.group(2).strip()
                
                if field == 'Name' and not character['name']:
                    character['name'] = value
                elif field == 'Street Name':
                    character['street_name'] = value
                elif field == 'Archetype':
                    character['archetype'] = value
                elif field == 'Race':
                    character['character_type'] = value
                elif field == 'Description':
                    character['description'] = value
                elif field == 'Nuyen':
                    # Extract number from "498,148¥" format
                    num_match = re.search(r'([\d,]+)', value)
                    if num_match:
                        character['nuyen'] = int(num_match.group(1).replace(',', ''))
                elif field == 'Karma Pool':
                    num_match = re.search(r'(\d+)', value)
                    if num_match:
                        character['karma_pool'] = int(num_match.group(1))
                elif field == 'Essence':
                    num_match = re.search(r'([\d.]+)', value)
                    if num_match:
                        character['essence'] = float(num_match.group(1))
                elif field == 'Magic':
                    num_match = re.search(r'(\d+)', value)
                    if num_match:
                        character['magic'] = int(num_match.group(1))
                elif field == 'Reaction':
                    # Handle "27" or "3 / 2 (Human / Rhino)" formats
                    num_match = re.search(r'(\d+)', value)
                    if num_match:
                        character['reaction'] = int(num_match.group(1))
                elif field == 'Initiative':
                    character['initiative'] = value
    
    # Extract attributes
    attr_section = re.search(r'##\s+Attributes(?:\s+\([^)]+\))?\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
    if attr_section:
        attr_text = attr_section.group(1)
        for line in attr_text.split('\n'):
            line = line.strip()
            if not line or not line.startswith('-'):
                continue
            
            match = re.match(r'-\s+\*\*(.+?)\*\*:\s*(.+)', line)
            if match:
                attr_name = match.group(1).strip().lower()
                value_text = match.group(2).strip()
                
                # Check for dual values (e.g., "6 / 9" for shapeshifters)
                dual_match = re.match(r'(\d+)\s*/\s*(\d+)', value_text)
                if dual_match:
                    # Store both base and augmented
                    character['attributes'][attr_name] = int(dual_match.group(1))
                    character['attributes'][f'{attr_name}_augmented'] = int(dual_match.group(2))
                else:
                    # Extract single number (base value)
                    num_match = re.search(r'(\d+)', value_text)
                    if num_match:
                        character['attributes'][attr_name] = int(num_match.group(1))
    
    # Extract skills
    skills_section = re.search(r'##\s+Skills\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
    if skills_section:
        skills_text = skills_section.group(1)
        for line in skills_text.split('\n'):
            line = line.strip()
            if not line or not line.startswith('-'):
                continue
            
            match = re.match(r'-\s+\*\*(.+?)\*\*:\s*(.+)', line)
            if match:
                skill_name = match.group(1).strip()
                value_text = match.group(2).strip()
                
                # Extract rating (first number)
                num_match = re.search(r'(\d+)', value_text)
                if num_match:
                    rating = int(num_match.group(1))
                    
                    # Check for specialization
                    spec_match = re.search(r'specialization\s+(\d+)', value_text, re.IGNORECASE)
                    specialization = None
                    if spec_match:
                        # Extract the specialization name
                        spec_name_match = re.search(r'(\w+)\s+specialization', value_text, re.IGNORECASE)
                        if spec_name_match:
                            specialization = spec_name_match.group(1)
                    
                    character['skills'].append({
                        'skill_name': skill_name,
                        'rating': rating,
                        'specialization': specialization
                    })
    
    # Extract gear from multiple sections
    gear_sections = [
        r'##\s+Gear\s*\n(.*?)(?=\n##|\Z)',
        r'##\s+Cyberware\s*\n(.*?)(?=\n##|\Z)',
        r'##\s+Bioware\s*\n(.*?)(?=\n##|\Z)',
        r'##\s+Weapons\s*\n(.*?)(?=\n##|\Z)'
    ]
    
    for pattern in gear_sections:
        section = re.search(pattern, content, re.DOTALL)
        if section:
            gear_text = section.group(1)
            for line in gear_text.split('\n'):
                line = line.strip()
                if not line or not line.startswith('-'):
                    continue
                
                # Remove markdown formatting
                gear_item = re.sub(r'\*\*(.+?)\*\*', r'\1', line)
                gear_item = gear_item.lstrip('- ').strip()
                
                # Skip section headers (items ending with ':')
                if gear_item and len(gear_item) > 2 and not gear_item.endswith(':'):
                    character['gear'].append({
                        'gear_name': gear_item[:200],  # Limit length
                        'quantity': 1,
                        'notes': None
                    })
    
    # Extract contacts
    contacts_section = re.search(r'##\s+Contacts\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
    if contacts_section:
        contacts_text = contacts_section.group(1)
        for line in contacts_text.split('\n'):
            line = line.strip()
            if not line or not line.startswith('-'):
                continue
            
            # Remove markdown and extract contact info
            contact_text = re.sub(r'\*\*(.+?)\*\*', r'\1', line)
            contact_text = contact_text.lstrip('- ').strip()
            
            if contact_text:
                character['contacts'].append(contact_text)
    
    # Extract edges and flaws
    edges_section = re.search(r'##\s+Edges and Flaws\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
    if edges_section:
        ef_text = edges_section.group(1)
        
        # Extract edges - handle both inline and list formats
        edges_match = re.search(r'-\s+\*\*Edges\*\*:\s*\n(.*?)(?=-\s+\*\*Flaws\*\*:|\n##|\Z)', ef_text, re.DOTALL)
        if edges_match:
            edges_text = edges_match.group(1).strip()
            # Parse list items
            for line in edges_text.split('\n'):
                line = line.strip()
                if line.startswith('-'):
                    edge = line.lstrip('- ').strip()
                    if edge:
                        character['edges'].append(edge)
        
        # Extract flaws - handle both inline and list formats
        flaws_match = re.search(r'-\s+\*\*Flaws\*\*:\s*\n(.*?)(?=\n-\s+\*\*[A-Z]|\n##|\Z)', ef_text, re.DOTALL)
        if flaws_match:
            flaws_text = flaws_match.group(1).strip()
            # Parse list items
            for line in flaws_text.split('\n'):
                line = line.strip()
                if line.startswith('-'):
                    flaw = line.lstrip('- ').strip()
                    if flaw:
                        character['flaws'].append(flaw)
    
    # Extract spells
    spells_section = re.search(r'##\s+Spells\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
    if spells_section:
        spells_text = spells_section.group(1)
        for line in spells_text.split('\n'):
            line = line.strip()
            if not line or not line.startswith('-'):
                continue
            
            # Parse "- **Spell Name**: Force X" format
            match = re.match(r'-\s+\*\*(.+?)\*\*:\s*(.+)', line)
            if match:
                spell_name = match.group(1).strip()
                details = match.group(2).strip()
                
                # Extract force
                force_match = re.search(r'Force\s+(\d+)', details, re.IGNORECASE)
                force = int(force_match.group(1)) if force_match else 0
                
                character['spells'].append({
                    'name': spell_name,
                    'force': force,
                    'details': details
                })
    
    # Extract spell formulas
    formulas_section = re.search(r'##\s+Spell Formulas\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
    if formulas_section:
        formulas_text = formulas_section.group(1)
        for line in formulas_text.split('\n'):
            line = line.strip()
            if not line or not line.startswith('-'):
                continue
            
            # Parse formulas list
            formulas_match = re.search(r'-\s+\*\*Formulas\*\*:\s*(.+)', line)
            if formulas_match:
                formulas_list = formulas_match.group(1).strip()
                # Split by comma and parse each formula
                for formula in formulas_list.split(','):
                    formula = formula.strip()
                    if formula:
                        # Extract name and force
                        parts = formula.rsplit(' ', 1)
                        if len(parts) == 2 and parts[1].isdigit():
                            character['spell_formulas'].append({
                                'name': parts[0].strip(),
                                'force': int(parts[1])
                            })
                        else:
                            character['spell_formulas'].append({
                                'name': formula,
                                'force': 0
                            })
    
    # Extract adept powers
    adept_section = re.search(r'##\s+Adept Powers\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
    if adept_section:
        adept_text = adept_section.group(1)
        for line in adept_text.split('\n'):
            line = line.strip()
            if not line or not line.startswith('-'):
                continue
            
            # Parse "- **Power Name**: X points (details)" format
            match = re.match(r'-\s+\*\*(.+?)\*\*:\s*(.+)', line)
            if match:
                power_name = match.group(1).strip()
                details = match.group(2).strip()
                
                # Extract points
                points_match = re.search(r'([\d.]+)\s+points?', details, re.IGNORECASE)
                points = float(points_match.group(1)) if points_match else 0
                
                character['adept_powers'].append({
                    'name': power_name,
                    'points': points,
                    'details': details
                })
    
    # Extract summoned spirits
    spirits_section = re.search(r'##\s+Summoned Spirits\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
    if spirits_section:
        spirits_text = spirits_section.group(1)
        for line in spirits_text.split('\n'):
            line = line.strip()
            if not line or not line.startswith('-'):
                continue
            
            # Parse spirit entries
            match = re.match(r'-\s+\*\*(.+?)\*\*:\s*(.+)', line)
            if match:
                spirit_type = match.group(1).strip()
                details = match.group(2).strip()
                
                # Extract force and services
                force_match = re.search(r'Force\s+(\d+)', details, re.IGNORECASE)
                services_match = re.search(r'services?\s+(\d+)', details, re.IGNORECASE)
                
                character['summoned_spirits'].append({
                    'type': spirit_type,
                    'force': int(force_match.group(1)) if force_match else 0,
                    'services': int(services_match.group(1)) if services_match else 0,
                    'details': details
                })
    
    # Extract additional data from basic info for initiate level, tradition, karma total
    if basic_info:
        info_text = basic_info.group(1)
        for line in info_text.split('\n'):
            line = line.strip()
            if not line or not line.startswith('-'):
                continue
            
            match = re.match(r'-\s+\*\*(.+?)\*\*:\s*(.+)', line)
            if match:
                field = match.group(1).strip()
                value = match.group(2).strip()
                
                if field == 'Initiate Level':
                    num_match = re.search(r'(\d+)', value)
                    if num_match:
                        character['initiate_level'] = int(num_match.group(1))
                elif field == 'Tradition':
                    character['tradition'] = value
                elif field == 'Total Karma Earned':
                    num_match = re.search(r'(\d+)', value)
                    if num_match:
                        character['karma_total'] = int(num_match.group(1))
    
    # Extract cyberware with essence costs
    cyber_section = re.search(r'##\s+Cyberware\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
    if cyber_section:
        cyber_text = cyber_section.group(1)
        for line in cyber_text.split('\n'):
            line = line.strip()
            if not line or not line.startswith('-'):
                continue
            
            # Parse "- **Item Name** (Essence X.X, details)" format
            match = re.match(r'-\s+\*\*(.+?)\*\*\s*\((.+?)\)', line)
            if match:
                item_name = match.group(1).strip()
                details = match.group(2).strip()
                
                # Extract essence cost
                essence_match = re.search(r'Essence\s+([\d.]+)', details, re.IGNORECASE)
                essence = float(essence_match.group(1)) if essence_match else 0
                
                character['cyberware'].append({
                    'name': item_name,
                    'essence': essence,
                    'details': details
                })
    
    # Extract bioware with body index costs
    bio_section = re.search(r'##\s+Bioware\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
    if bio_section:
        bio_text = bio_section.group(1)
        for line in bio_text.split('\n'):
            line = line.strip()
            if not line or not line.startswith('-'):
                continue
            
            # Parse "- **Item Name** (B.I. X.X, details)" format
            match = re.match(r'-\s+\*\*(.+?)\*\*\s*\((.+?)\)', line)
            if match:
                item_name = match.group(1).strip()
                details = match.group(2).strip()
                
                # Extract body index cost
                bi_match = re.search(r'B\.I\.\s+([\d.]+)', details, re.IGNORECASE)
                body_index = float(bi_match.group(1)) if bi_match else 0
                
                character['bioware'].append({
                    'name': item_name,
                    'body_index': body_index,
                    'details': details
                })
    
    # Extract weapons from gear section with FULL details
    weapons_section = re.search(r'##\s+Gear\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
    if weapons_section:
        gear_text = weapons_section.group(1)
        
        # Check for nested weapons list under "**Weapons**:" header
        weapons_nested = re.search(r'-\s+\*\*Weapons\*\*:\s*\n(.*?)(?=\n-\s+\*\*[A-Z]|\n##|\Z)', gear_text, re.DOTALL)
        if weapons_nested:
            weapons_text = weapons_nested.group(1)
            current_weapon = None
            
            for line in weapons_text.split('\n'):
                line_stripped = line.strip()
                
                # Count leading spaces to determine indentation level
                leading_spaces = len(line) - len(line.lstrip(' '))
                
                # Main weapons have 2 spaces, sub-items have 4+ spaces
                is_main_weapon = leading_spaces == 2 and line_stripped.startswith('- **')
                is_sub_item = leading_spaces >= 4 and line_stripped.startswith('-')
                
                # Check if this is a main weapon entry
                if is_main_weapon:
                    # Save previous weapon if exists
                    if current_weapon:
                        character['weapons'].append(current_weapon)
                    
                    # Parse new weapon - match to the LAST closing paren
                    match = re.match(r'-\s+\*\*(.+?)\*\*\s*\((.+)\)', line_stripped)
                    if match:
                        weapon_name = match.group(1).strip()
                        main_details = match.group(2).strip()
                        
                        # Extract all stats
                        conceal_match = re.search(r'Conceal\s+(\d+)', main_details, re.IGNORECASE)
                        capacity_match = re.search(r'(\d+)\(c\)', main_details)
                        mode_match = re.search(r'(SA|BF|FA|SA/BF|SA/BF/FA|SS)', main_details)
                        damage_match = re.search(r'(\d+[MLSD](?:\s+(?:Physical|Stun))?)', main_details, re.IGNORECASE)
                        tn_mod_match = re.search(r'(-\d+)\s+TN', main_details)
                        reach_match = re.search(r'Reach\s+(\d+)', main_details, re.IGNORECASE)
                        
                        current_weapon = {
                            'name': weapon_name,
                            'conceal': int(conceal_match.group(1)) if conceal_match else None,
                            'capacity': capacity_match.group(1) if capacity_match else None,
                            'mode': mode_match.group(1) if mode_match else None,
                            'damage': damage_match.group(1) if damage_match else '',
                            'tn_modifier': tn_mod_match.group(1) if tn_mod_match else None,
                            'reach': int(reach_match.group(1)) if reach_match else None,
                            'ammo': [],
                            'modifications': [],
                            'notes': main_details
                        }
                    else:
                        # Simple weapon without parentheses
                        weapon_name = line_stripped.lstrip('- **').rstrip('**').strip()
                        current_weapon = {
                            'name': weapon_name,
                            'conceal': None,
                            'capacity': None,
                            'mode': None,
                            'damage': '',
                            'tn_modifier': None,
                            'reach': None,
                            'ammo': [],
                            'modifications': [],
                            'notes': ''
                        }
                
                # Check for sub-items (ammo, mods) - indented lines starting with -
                elif current_weapon and is_sub_item:
                    sub_item = line_stripped.lstrip('- ').strip()
                    
                    # Remove any ** markdown
                    sub_item = re.sub(r'\*\*(.+?)\*\*', r'\1', sub_item)
                    
                    # Categorize as ammo or modification
                    if any(keyword in sub_item.lower() for keyword in ['ammo', 'rounds', 'clips', 'magazine', 'apds', 'gel', 'ex-explosive', 'explosive', 'grenade']):
                        current_weapon['ammo'].append(sub_item)
                    else:
                        current_weapon['modifications'].append(sub_item)
            
            # Don't forget the last weapon
            if current_weapon:
                character['weapons'].append(current_weapon)
    
    # Extract vehicles from gear section
    gear_section = re.search(r'##\s+Gear\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
    if gear_section:
        gear_text = gear_section.group(1)
        
        # Look for vehicles section
        vehicles_nested = re.search(r'-\s+\*\*Vehicles\*\*:\s*\n(.*?)(?=\n-\s+\*\*[A-Z]|\n##|\Z)', gear_text, re.DOTALL)
        if vehicles_nested:
            vehicles_text = vehicles_nested.group(1)
            
            for line in vehicles_text.split('\n'):
                line_stripped = line.strip()
                if not line_stripped.startswith('- **'):
                    continue
                
                # Parse vehicle entry
                match = re.match(r'-\s+\*\*(.+?)\*\*\s*\((.+?)\)', line_stripped)
                if match:
                    vehicle_name = match.group(1).strip()
                    details = match.group(2).strip()
                    
                    # Extract stats
                    handling_match = re.search(r'Handling\s+([\d/]+)', details)
                    speed_match = re.search(r'Speed\s+(\d+)', details)
                    body_match = re.search(r'Body\s+(\d+)', details)
                    armor_match = re.search(r'Armor\s+(\d+)', details)
                    
                    character['vehicles'].append({
                        'name': vehicle_name,
                        'handling': handling_match.group(1) if handling_match else '',
                        'speed': int(speed_match.group(1)) if speed_match else 0,
                        'body': int(body_match.group(1)) if body_match else 0,
                        'armor': int(armor_match.group(1)) if armor_match else 0,
                        'details': details
                    })
    
    # Extract cyberdeck information
    deck_section = re.search(r'##\s+Matrix Stats\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
    if not deck_section:
        deck_section = re.search(r'###\s+Cyberdeck[:\s]+(.+?)\n(.*?)(?=\n###|\n##|\Z)', content, re.DOTALL)
    
    if deck_section:
        deck_text = deck_section.group(0) if deck_section else ''
        
        # Extract MPCP
        mpcp_match = re.search(r'MPCP\s+(?:Rating\s*:?\s*)?(\d+)', deck_text, re.IGNORECASE)
        memory_match = re.search(r'Memory\s*:?\s*(\d+)', deck_text, re.IGNORECASE)
        hardening_match = re.search(r'Hardening\s*:?\s*(\d+)', deck_text, re.IGNORECASE)
        
        if mpcp_match:
            character['deck'] = {
                'mpcp': int(mpcp_match.group(1)),
                'memory': int(memory_match.group(1)) if memory_match else 0,
                'hardening': int(hardening_match.group(1)) if hardening_match else 0,
                'details': deck_text[:500]  # First 500 chars
            }
    
    return character

def import_character(conn, character_data):
    """Import or update character in database"""
    cursor = conn.cursor()
    
    try:
        # Check if character exists
        cursor.execute("""
            SELECT id FROM characters 
            WHERE LOWER(name) = LOWER(%s) OR LOWER(COALESCE(street_name, '')) = LOWER(%s)
        """, (character_data['name'], character_data['street_name'] or ''))
        
        existing = cursor.fetchone()
        
        if existing:
            char_id = existing['id']
            print(f"Updating existing character: {character_data['name']}")
            
            # Build comprehensive attributes JSON
            attrs = character_data['attributes'].copy()
            attrs['essence'] = character_data['essence']
            attrs['magic'] = character_data['magic']
            attrs['reaction'] = character_data['reaction']
            attrs['initiate_level'] = character_data['initiate_level']
            attrs['tradition'] = character_data['tradition']
            attrs['karma_total'] = character_data['karma_total']
            
            # Build relationships JSON with all character data
            relationships = {
                'contacts': character_data['contacts'],
                'edges': character_data['edges'],
                'flaws': character_data['flaws'],
                'spells': character_data['spells'],
                'spell_formulas': character_data['spell_formulas'],
                'adept_powers': character_data['adept_powers'],
                'summoned_spirits': character_data['summoned_spirits'],
                'magical_items': character_data['magical_items'],
                'weapons': character_data['weapons'],
                'armor': character_data['armor'],
                'vehicles': character_data['vehicles'],
                'drones': character_data['drones'],
                'deck': character_data['deck']
            }
            
            # Update character
            cursor.execute("""
                UPDATE characters SET
                    street_name = %s,
                    character_type = %s,
                    archetype = %s,
                    nuyen = %s,
                    karma_pool = %s,
                    karma_total = %s,
                    initiative = %s,
                    attributes = %s,
                    relationships = %s,
                    notes = %s
                WHERE id = %s
            """, (
                character_data['street_name'],
                character_data['character_type'],
                character_data['archetype'],
                character_data['nuyen'],
                character_data['karma_pool'],
                character_data['karma_total'],
                character_data['initiative'],
                json.dumps(attrs),
                json.dumps(relationships),
                character_data['description'],
                char_id
            ))
            
            # Delete existing skills and gear
            cursor.execute("DELETE FROM character_skills WHERE character_id = %s", (char_id,))
            cursor.execute("DELETE FROM character_gear WHERE character_id = %s", (char_id,))
        else:
            print(f"Creating new character: {character_data['name']}")
            
            # Build comprehensive attributes JSON
            attrs = character_data['attributes'].copy()
            attrs['essence'] = character_data['essence']
            attrs['magic'] = character_data['magic']
            attrs['reaction'] = character_data['reaction']
            attrs['initiate_level'] = character_data['initiate_level']
            attrs['tradition'] = character_data['tradition']
            attrs['karma_total'] = character_data['karma_total']
            
            # Build relationships JSON with all character data
            relationships = {
                'contacts': character_data['contacts'],
                'edges': character_data['edges'],
                'flaws': character_data['flaws'],
                'spells': character_data['spells'],
                'spell_formulas': character_data['spell_formulas'],
                'adept_powers': character_data['adept_powers'],
                'summoned_spirits': character_data['summoned_spirits'],
                'magical_items': character_data['magical_items'],
                'weapons': character_data['weapons'],
                'armor': character_data['armor'],
                'vehicles': character_data['drones'],
                'drones': character_data['drones'],
                'deck': character_data['deck']
            }
            
            # Insert new character
            cursor.execute("""
                INSERT INTO characters (
                    name, street_name, character_type, archetype,
                    nuyen, karma_pool, karma_total, initiative, attributes, relationships, notes
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                character_data['name'],
                character_data['street_name'],
                character_data['character_type'],
                character_data['archetype'],
                character_data['nuyen'],
                character_data['karma_pool'],
                character_data['karma_total'],
                character_data['initiative'],
                json.dumps(attrs),
                json.dumps(relationships),
                character_data['description']
            ))
            
            char_id = cursor.fetchone()['id']
        
        # Insert skills
        for skill in character_data['skills']:
            cursor.execute("""
                INSERT INTO character_skills (character_id, skill_name, rating, specialization)
                VALUES (%s, %s, %s, %s)
            """, (char_id, skill['skill_name'], skill['rating'], skill.get('specialization')))
        
        # Insert gear
        for item in character_data['gear']:
            cursor.execute("""
                INSERT INTO character_gear (character_id, gear_name, quantity, notes)
                VALUES (%s, %s, %s, %s)
            """, (char_id, item['gear_name'], item.get('quantity', 1), item.get('notes')))
        
        conn.commit()
        
        # Print summary
        summary_parts = [f"{len(character_data['skills'])} skills", f"{len(character_data['gear'])} gear items"]
        if character_data['spells']:
            summary_parts.append(f"{len(character_data['spells'])} spells")
        if character_data['adept_powers']:
            summary_parts.append(f"{len(character_data['adept_powers'])} adept powers")
        if character_data['summoned_spirits']:
            summary_parts.append(f"{len(character_data['summoned_spirits'])} spirits")
        if character_data['cyberware']:
            summary_parts.append(f"{len(character_data['cyberware'])} cyberware")
        if character_data['bioware']:
            summary_parts.append(f"{len(character_data['bioware'])} bioware")
        if character_data['weapons']:
            summary_parts.append(f"{len(character_data['weapons'])} weapons")
        if character_data['vehicles']:
            summary_parts.append(f"{len(character_data['vehicles'])} vehicles/drones")
        if character_data['deck']:
            summary_parts.append(f"cyberdeck (MPCP {character_data['deck']['mpcp']})")
        
        print(f"✓ Successfully imported {character_data['name']} ({', '.join(summary_parts)})")
        
    except Exception as e:
        conn.rollback()
        print(f"✗ Error importing {character_data['name']}: {e}")
        raise
    finally:
        cursor.close()

def main():
    """Main import function"""
    # Character files to import from local characters/ folder
    character_files = {
        'Platinum': 'characters/Platinum.md',
        'Oak': 'characters/Oak.md',
        'Manticore': 'characters/Manticore.md',
        'Block': 'characters/Block.md',
        'Axel': 'characters/Axel.md',
        'Raven': 'characters/Raven.md',
    }
    
    conn = get_connection()
    
    try:
        for char_name, filepath in character_files.items():
            if not os.path.exists(filepath):
                print(f"⚠ File not found: {filepath}")
                continue
            
            print(f"\nProcessing {char_name}...")
            character_data = parse_character_markdown(filepath)
            import_character(conn, character_data)
        
        print("\n✓ All characters imported successfully!")
        
    except Exception as e:
        print(f"\n✗ Import failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    main()
