#!/usr/bin/env python3
"""
Complete character import from markdown files
Imports ALL character data including physical description, cyberware, contacts, vehicles, etc.
"""
import os
import re
from pathlib import Path
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row

load_dotenv()

def parse_markdown_section(content, section_name):
    """Extract a section from markdown content"""
    # Use greedy match to capture all content including subsections (###)
    # Allow optional text in parentheses after section name (e.g., "(if using Shadowrun Companion)")
    pattern = rf'##\s+{re.escape(section_name)}(?:\s*\([^)]*\))?\s*\n(.*)(?=\n##|\Z)'
    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else ""

def parse_basic_info(content):
    """Parse Basic Information section"""
    section = parse_markdown_section(content, "Basic Information")
    info = {}
    
    patterns = {
        'name': r'-\s+\*\*Name\*\*:\s*(.+)',
        'street_name': r'-\s+\*\*Street Name\*\*:\s*(.+)',
        'metatype': r'-\s+\*\*Metatype\*\*:\s*(.+)',
        'archetype': r'-\s+\*\*Archetype\*\*:\s*(.+)',
        'sex': r'-\s+\*\*Sex\*\*:\s*(.+)',
        'age': r'-\s+\*\*Age\*\*:\s*(.+)',
        'height': r'-\s+\*\*Height\*\*:\s*(.+)',
        'weight': r'-\s+\*\*Weight\*\*:\s*(.+)',
        'hair': r'-\s+\*\*Hair\*\*:\s*(.+)',
        'eyes': r'-\s+\*\*Eyes\*\*:\s*(.+)',
        'skin': r'-\s+\*\*Skin\*\*:\s*(.+)',
        'race': r'-\s+\*\*Race\*\*:\s*(.+)',  # Alternative to metatype
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, section, re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            info[key] = None if value.lower() in ['n/a', 'none', ''] else value
    
    # If race was found but not metatype, use race as metatype
    if 'race' in info and info['race'] and not info.get('metatype'):
        info['metatype'] = info['race']
    if 'race' in info:
        del info['race']
    
    return info

def parse_attributes(content):
    """Parse Attributes section - Base Form only, also check Basic Information for attributes"""
    section = parse_markdown_section(content, "Attributes")
    
    # Try to extract Base Form subsection first
    base_match = re.search(r'###\s+Base Form(.*?)(?=###|\Z)', section, re.DOTALL | re.IGNORECASE)
    if base_match:
        base_section = base_match.group(1)
    else:
        # If no Base Form subsection, use the whole Attributes section
        base_section = section
    
    attrs = {}
    patterns = {
        'body': r'-\s+\*\*Body\*\*:\s*(\d+)',
        'quickness': r'-\s+\*\*Quickness\*\*:\s*(\d+)',
        'strength': r'-\s+\*\*Strength\*\*:\s*(\d+)',
        'charisma': r'-\s+\*\*Charisma\*\*:\s*(\d+)',
        'intelligence': r'-\s+\*\*Intelligence\*\*:\s*(\d+)',
        'willpower': r'-\s+\*\*Willpower\*\*:\s*(\d+)',
        'essence': r'-\s+\*\*Essence\*\*:\s*([\d.]+)',
        'magic': r'-\s+\*\*Magic\*\*:\s*(\d+)',
        'reaction': r'-\s+\*\*Reaction\*\*:\s*(\d+)',
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, base_section, re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            if value.lower() not in ['n/a', 'none']:
                attrs[key] = float(value) if '.' in value else int(value)
    
    # Also check Basic Information section for attributes (some files have them there)
    basic_section = parse_markdown_section(content, "Basic Information")
    for key, pattern in patterns.items():
        if key not in attrs:  # Only if not already found
            match = re.search(pattern, basic_section, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                if value.lower() not in ['n/a', 'none']:
                    attrs[key] = float(value) if '.' in value else int(value)
    
    return attrs

def parse_derived_stats(content):
    """Parse Derived Stats section"""
    section = parse_markdown_section(content, "Derived Stats")
    stats = {}
    
    patterns = {
        'initiative': r'-\s+\*\*Initiative\*\*:\s*(.+)',
        'combat_pool': r'-\s+\*\*Combat Pool\*\*:\s*(\d+)',
        'karma_pool': r'-\s+\*\*Karma Pool\*\*:\s*(\d+)',
        'karma_total': r'-\s+\*\*Total Karma Earned\*\*:\s*(\d+)',
        'karma_available': r'-\s+\*\*Total Karma Available\*\*:\s*(\d+)',
        'nuyen': r'-\s+\*\*Nuyen\*\*:\s*([\d,]+)',
        'lifestyle': r'-\s+\*\*Lifestyle\*\*:\s*(.+)',
        'essence_hole': r'-\s+\*\*Essence Hole\*\*:\s*([\d.]+)',
        'body_index': r'-\s+\*\*Body Index\*\*:\s*([\d.]+)/([\d.]+)',
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, section, re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            if value.lower() not in ['n/a', 'none']:
                if key == 'nuyen':
                    stats[key] = int(value.replace(',', '').replace('¥', ''))
                elif key == 'body_index':
                    stats['body_index_current'] = float(match.group(1))
                    stats['body_index_max'] = float(match.group(2))
                elif key in ['combat_pool', 'karma_pool', 'karma_total', 'karma_available']:
                    stats[key] = int(value)
                elif key == 'essence_hole':
                    stats[key] = float(value)
                elif key == 'lifestyle':
                    # Parse "High (5,000¥/month, 1 month prepaid)"
                    lifestyle_match = re.match(r'(\w+)\s*\(([\d,]+)¥/month,\s*(\d+)\s*month', value)
                    if lifestyle_match:
                        stats['lifestyle'] = lifestyle_match.group(1)
                        stats['lifestyle_cost'] = int(lifestyle_match.group(2).replace(',', ''))
                        stats['lifestyle_months_prepaid'] = int(lifestyle_match.group(3))
                    else:
                        stats['lifestyle'] = value
                else:
                    stats[key] = value
    
    return stats

def parse_skills(content):
    """Parse Skills section"""
    section = parse_markdown_section(content, "Skills")
    skills = []
    
    # Parse Active Skills
    active_match = re.search(r'###\s+Active Skills(.*?)(?=###|\Z)', section, re.DOTALL | re.IGNORECASE)
    if active_match:
        for line in active_match.group(1).split('\n'):
            match = re.match(r'-\s+\*\*(.+?)\*\*:\s*(\d+)', line)
            if match:
                skills.append({
                    'name': match.group(1).strip(),
                    'rating': int(match.group(2)),
                    'type': 'active'
                })
    
    # Parse Knowledge Skills
    knowledge_match = re.search(r'###\s+Knowledge Skills(.*?)(?=###|\Z)', section, re.DOTALL | re.IGNORECASE)
    if knowledge_match:
        for line in knowledge_match.group(1).split('\n'):
            match = re.match(r'-\s+\*\*(.+?)\*\*:\s*(\d+)', line)
            if match:
                skills.append({
                    'name': match.group(1).strip(),
                    'rating': int(match.group(2)),
                    'type': 'knowledge'
                })
    
    # Parse Language Skills
    language_match = re.search(r'###\s+Language Skills(.*?)(?=###|\Z)', section, re.DOTALL | re.IGNORECASE)
    if language_match:
        for line in language_match.group(1).split('\n'):
            match = re.match(r'-\s+\*\*(.+?)\*\*:\s*(\d+)', line)
            if match:
                skills.append({
                    'name': match.group(1).strip(),
                    'rating': int(match.group(2)),
                    'type': 'language'
                })
    
    return skills

def parse_cyberware(content):
    """Parse Cyberware from Cyberware/Bioware section"""
    section = parse_markdown_section(content, "Cyberware/Bioware")
    cyberware = []
    
    cyber_match = re.search(r'###\s+Cyberware(.*?)(?=###|\Z)', section, re.DOTALL | re.IGNORECASE)
    if not cyber_match:
        return cyberware
    
    cyber_section = cyber_match.group(1)
    
    # Parse each cyberware item
    items = re.split(r'\n-\s+\*\*', cyber_section)
    for item in items[1:]:  # Skip first empty split
        lines = item.split('\n')
        if not lines:
            continue
        
        # First line has name and essence cost
        first_line = lines[0]
        name_match = re.match(r'(.+?)\*\*\s*\(([\d.]+)\s+Essence\)', first_line)
        if name_match:
            name = name_match.group(1).strip()
            essence = float(name_match.group(2))
            
            # Parse modifiers from subsequent lines
            modifiers = []
            for line in lines[1:]:
                line = line.strip()
                if line.startswith('-'):
                    modifiers.append(line[1:].strip())
            
            cyberware.append({
                'name': name,
                'essence_cost': essence,
                'modifiers': modifiers
            })
    
    return cyberware

def parse_bioware(content):
    """Parse Bioware from Cyberware/Bioware section"""
    section = parse_markdown_section(content, "Cyberware/Bioware")
    bioware = []
    
    # Look for Bioware subsection, stopping at next ### subsection, --- separator, or end
    bio_match = re.search(r'###\s+Bioware(.*?)(?=\n###|\n---|\Z)', section, re.DOTALL | re.IGNORECASE)
    if not bio_match:
        return bioware
    
    bio_section = bio_match.group(1)
    
    # Parse each bioware item
    items = re.split(r'\n-\s+\*\*', bio_section)
    for item in items[1:]:  # Skip first empty split
        lines = item.split('\n')
        if not lines:
            continue
        
        # First line has name and cost (either Body Index or Essence)
        first_line = lines[0]
        
        # Try Body Index format first
        name_match = re.match(r'(.+?)\*\*\s*\(([\d.]+)\s+Body Index\)', first_line)
        if name_match:
            name = name_match.group(1).strip()
            cost = float(name_match.group(2))
            cost_type = 'body_index'
        else:
            # Try Essence format (some bioware uses Essence cost)
            name_match = re.match(r'(.+?)\*\*\s*\(([\d.]+)\s+Essence\)', first_line)
            if name_match:
                name = name_match.group(1).strip()
                cost = float(name_match.group(2))
                cost_type = 'essence'
            else:
                continue
        
        # Parse modifiers from subsequent lines
        modifiers = []
        for line in lines[1:]:
            line = line.strip()
            if line.startswith('-'):
                modifiers.append(line[1:].strip())
        
        bioware.append({
            'name': name,
            'body_index_cost': cost if cost_type == 'body_index' else 0,
            'essence_cost': cost if cost_type == 'essence' else 0,
            'modifiers': modifiers
        })
    
    return bioware

def parse_weapons(content):
    """Parse Weapons from Gear section"""
    section = parse_markdown_section(content, "Gear")
    weapons = []
    
    weapons_match = re.search(r'###\s+Weapons(.*?)(?=###|\Z)', section, re.DOTALL | re.IGNORECASE)
    if not weapons_match:
        return weapons
    
    weapons_section = weapons_match.group(1)
    
    # Parse each weapon
    items = re.split(r'\n-\s+\*\*', weapons_section)
    for item in items[1:]:  # Skip first empty split
        lines = item.split('\n')
        if not lines:
            continue
        
        # First line has weapon name
        name = lines[0].split('**')[0].strip()
        
        weapon_data = {'name': name}
        
        # Parse weapon properties
        for line in lines[1:]:
            line = line.strip()
            if line.startswith('- Type:'):
                weapon_data['type'] = line.split(':', 1)[1].strip()
            elif line.startswith('- Damage:'):
                weapon_data['damage'] = line.split(':', 1)[1].strip()
            elif line.startswith('- Concealability:') or line.startswith('- Conceal:'):
                weapon_data['conceal'] = line.split(':', 1)[1].strip()
            elif line.startswith('- Ammo:'):
                weapon_data['ammo'] = line.split(':', 1)[1].strip()
            elif line.startswith('- Modifications:'):
                weapon_data['modifications'] = line.split(':', 1)[1].strip()
        
        weapons.append(weapon_data)
    
    return weapons

def parse_armor(content):
    """Parse Armor from Gear section"""
    section = parse_markdown_section(content, "Gear")
    armor = []
    
    armor_match = re.search(r'###\s+Armor(.*?)(?=###|\Z)', section, re.DOTALL | re.IGNORECASE)
    if not armor_match:
        return armor
    
    armor_section = armor_match.group(1)
    
    # Parse each armor item
    items = re.split(r'\n-\s+\*\*', armor_section)
    for item in items[1:]:  # Skip first empty split
        lines = item.split('\n')
        if not lines:
            continue
        
        # First line has armor name
        name = lines[0].split('**')[0].strip()
        
        armor_data = {'name': name}
        
        # Parse armor properties
        for line in lines[1:]:
            line = line.strip()
            if line.startswith('- Rating:'):
                rating = line.split(':', 1)[1].strip()
                # Parse "5/3 (Ballistic/Impact)"
                rating_match = re.match(r'(\d+)/(\d+)', rating)
                if rating_match:
                    armor_data['ballistic'] = int(rating_match.group(1))
                    armor_data['impact'] = int(rating_match.group(2))
            elif line.startswith('- Concealability:') or line.startswith('- Conceal:'):
                armor_data['conceal'] = line.split(':', 1)[1].strip()
        
        armor.append(armor_data)
    
    return armor

def parse_contacts(content):
    """Parse Contacts section"""
    section = parse_markdown_section(content, "Contacts")
    contacts = []
    
    # Parse each contact line: "- **Name** - Role"
    for line in section.split('\n'):
        match = re.match(r'-\s+\*\*(.+?)\*\*\s+-\s+(.+)', line)
        if match:
            name = match.group(1).strip()
            role = match.group(2).strip()
            
            # Extract level if present
            level_match = re.search(r'Level:\s*(\d+)', role)
            level = int(level_match.group(1)) if level_match else 1
            
            contacts.append({
                'name': name,
                'role': role,
                'level': level
            })
    
    return contacts

def parse_vehicles(content):
    """Parse Vehicles section"""
    section = parse_markdown_section(content, "Gear")
    vehicles = []
    
    vehicles_match = re.search(r'###\s+Vehicles(.*?)(?=###|\Z)', section, re.DOTALL | re.IGNORECASE)
    if not vehicles_match:
        return vehicles
    
    vehicles_section = vehicles_match.group(1)
    
    # Parse each vehicle
    items = re.split(r'\n-\s+\*\*', vehicles_section)
    for item in items[1:]:  # Skip first empty split
        lines = item.split('\n')
        if not lines:
            continue
        
        # First line has vehicle name
        name = lines[0].split('**')[0].strip()
        
        vehicle_data = {'name': name}
        
        # Parse vehicle properties
        for line in lines[1:]:
            line = line.strip()
            if line.startswith('- Type:'):
                vehicle_data['type'] = line.split(':', 1)[1].strip()
            elif line.startswith('- Handling:'):
                vehicle_data['handling'] = line.split(':', 1)[1].strip()
            elif line.startswith('- Speed:'):
                speed = line.split(':', 1)[1].strip()
                if speed and speed != 'N/A':
                    vehicle_data['speed'] = int(speed)
            elif line.startswith('- Body:'):
                body = line.split(':', 1)[1].strip()
                if body and body != 'N/A':
                    vehicle_data['body'] = int(body)
            elif line.startswith('- Armor:'):
                armor = line.split(':', 1)[1].strip()
                if armor and armor != 'N/A':
                    vehicle_data['armor'] = int(armor)
        
        vehicles.append(vehicle_data)
    
    return vehicles

def parse_edges_flaws(content):
    """Parse Edges and Flaws section"""
    edges = []
    flaws = []
    
    section = parse_markdown_section(content, "Edges and Flaws")
    
    # Parse Edges - stop at next ### subsection, --- separator, or end
    edges_match = re.search(r'###\s+Edges(.*?)(?=\n###|\n---|\Z)', section, re.DOTALL | re.IGNORECASE)
    if edges_match:
        for line in edges_match.group(1).split('\n'):
            # Match pattern: - **Name** (optional points): Description
            match = re.match(r'-\s+\*\*(.+?)\*\*.*?:\s*(.+)', line)
            if match:
                name = match.group(1).strip()
                desc = match.group(2).strip()
                # Include N/A items (they're still valid edges/flaws, just without special mechanics)
                edges.append({'name': name, 'description': desc})
    
    # Parse Flaws - stop at next ### subsection, --- separator, or end
    flaws_match = re.search(r'###\s+Flaws(.*?)(?=\n###|\n---|\Z)', section, re.DOTALL | re.IGNORECASE)
    if flaws_match:
        for line in flaws_match.group(1).split('\n'):
            # Match pattern: - **Name** (optional points): Description
            match = re.match(r'-\s+\*\*(.+?)\*\*.*?:\s*(.+)', line)
            if match:
                name = match.group(1).strip()
                desc = match.group(2).strip()
                # Include N/A items (they're still valid edges/flaws, just without special mechanics)
                flaws.append({'name': name, 'description': desc})
    
    return edges, flaws

def parse_background(content):
    """Parse Background section"""
    section = parse_markdown_section(content, "Background")
    return section if section else None

def import_character(filepath, conn):
    """Import a single character from markdown file"""
    print(f"\nImporting {filepath.name}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse all sections
    basic_info = parse_basic_info(content)
    attributes = parse_attributes(content)
    derived_stats = parse_derived_stats(content)
    skills = parse_skills(content)
    cyberware = parse_cyberware(content)
    bioware = parse_bioware(content)
    weapons = parse_weapons(content)
    armor = parse_armor(content)
    contacts = parse_contacts(content)
    vehicles = parse_vehicles(content)
    edges, flaws = parse_edges_flaws(content)
    background = parse_background(content)
    
    cursor = conn.cursor()
    
    try:
        # Insert character
        char_data = {**basic_info, **attributes, **derived_stats}
        char_data['background'] = background
        
        # Set current attributes same as base for now
        for attr in ['body', 'quickness', 'strength', 'charisma', 'intelligence', 'willpower', 'essence', 'magic', 'reaction']:
            if attr in char_data:
                char_data[f'base_{attr}'] = char_data[attr]
                char_data[f'current_{attr}'] = char_data[attr]
                del char_data[attr]
        
        # Build INSERT statement
        columns = list(char_data.keys())
        placeholders = ', '.join(['%s'] * len(columns))
        column_names = ', '.join(columns)
        
        cursor.execute(f"""
            INSERT INTO characters ({column_names})
            VALUES ({placeholders})
            RETURNING id
        """, list(char_data.values()))
        
        result = cursor.fetchone()
        char_id = result['id'] if isinstance(result, dict) else result[0]
        print(f"  ✓ Created character: {basic_info.get('name', 'Unknown')} (ID: {char_id})")
        
        # Insert skills
        for skill in skills:
            cursor.execute("""
                INSERT INTO character_skills 
                (character_id, skill_name, skill_type, base_rating, current_rating)
                VALUES (%s, %s, %s, %s, %s)
            """, (char_id, skill['name'], skill['type'], skill['rating'], skill['rating']))
        print(f"  ✓ Added {len(skills)} skills")
        
        # Insert cyberware
        for cyber in cyberware:
            cursor.execute("""
                INSERT INTO character_modifiers
                (character_id, modifier_type, target_name, modifier_value, source, source_type,
                 is_permanent, essence_cost)
                VALUES (%s, 'augmentation', 'cyberware', 0, %s, 'cyberware', true, %s)
            """, (char_id, cyber['name'], cyber['essence_cost']))
        print(f"  ✓ Added {len(cyberware)} cyberware items")
        
        # Insert bioware
        for bio in bioware:
            # Build modifier_data JSONB with costs
            modifier_data = {}
            if bio.get('essence_cost', 0) > 0:
                modifier_data['essence_cost'] = bio['essence_cost']
            if bio.get('body_index_cost', 0) > 0:
                modifier_data['body_index_cost'] = bio['body_index_cost']
            
            cursor.execute("""
                INSERT INTO character_modifiers
                (character_id, modifier_type, target_name, modifier_value, source, source_type,
                 is_permanent, modifier_data)
                VALUES (%s, 'augmentation', 'bioware', 0, %s, 'bioware', true, %s)
            """, (char_id, bio['name'], psycopg.types.json.Jsonb(modifier_data)))
        print(f"  ✓ Added {len(bioware)} bioware items")
        
        # Insert weapons
        for weapon in weapons:
            cursor.execute("""
                INSERT INTO character_gear
                (character_id, gear_name, gear_type, damage, conceal, ammo_capacity)
                VALUES (%s, %s, 'weapon', %s, %s, %s)
            """, (char_id, weapon['name'], weapon.get('damage'), weapon.get('conceal'), weapon.get('ammo')))
        print(f"  ✓ Added {len(weapons)} weapons")
        
        # Insert armor
        for armor_item in armor:
            cursor.execute("""
                INSERT INTO character_gear
                (character_id, gear_name, gear_type, ballistic_rating, impact_rating, conceal)
                VALUES (%s, %s, 'armor', %s, %s, %s)
            """, (char_id, armor_item['name'], armor_item.get('ballistic'), armor_item.get('impact'), armor_item.get('conceal')))
        print(f"  ✓ Added {len(armor)} armor items")
        
        # Insert contacts
        for contact in contacts:
            cursor.execute("""
                INSERT INTO character_contacts
                (character_id, name, archetype, connection)
                VALUES (%s, %s, %s, %s)
            """, (char_id, contact['name'], contact['role'], contact['level']))
        print(f"  ✓ Added {len(contacts)} contacts")
        
        # Insert vehicles
        for vehicle in vehicles:
            cursor.execute("""
                INSERT INTO character_vehicles
                (character_id, vehicle_name, vehicle_type, handling, speed, body, armor)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (char_id, vehicle['name'], vehicle.get('type'), vehicle.get('handling'),
                  vehicle.get('speed'), vehicle.get('body'), vehicle.get('armor')))
        print(f"  ✓ Added {len(vehicles)} vehicles")
        
        # Insert edges
        for edge in edges:
            cursor.execute("""
                INSERT INTO character_edges_flaws
                (character_id, name, type, description)
                VALUES (%s, %s, 'edge', %s)
            """, (char_id, edge['name'], edge.get('description')))
        print(f"  ✓ Added {len(edges)} edges")
        
        # Insert flaws
        for flaw in flaws:
            cursor.execute("""
                INSERT INTO character_edges_flaws
                (character_id, name, type, description)
                VALUES (%s, %s, 'flaw', %s)
            """, (char_id, flaw['name'], flaw.get('description')))
        print(f"  ✓ Added {len(flaws)} flaws")
        
        conn.commit()
        print(f"  ✓ Import complete!")
        
    except Exception as e:
        conn.rollback()
        print(f"  ✗ Error importing character: {e}")
        raise

def main():
    """Import all characters from characters/ directory"""
    characters_dir = Path('characters')
    
    if not characters_dir.exists():
        print("Error: characters/ directory not found")
        return
    
    # Get all markdown files
    char_files = list(characters_dir.glob('*.md'))
    char_files = [f for f in char_files if f.name != 'README.md']
    
    if not char_files:
        print("No character files found in characters/")
        return
    
    print(f"Found {len(char_files)} character files")
    print("=" * 70)
    
    # Connect to database
    conn = psycopg.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB'),
        row_factory=dict_row
    )
    
    try:
        for char_file in sorted(char_files):
            import_character(char_file, conn)
        
        print("\n" + "=" * 70)
        print("Import complete!")
        
    finally:
        conn.close()

if __name__ == "__main__":
    main()
