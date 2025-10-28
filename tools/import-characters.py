#!/usr/bin/env python3
"""
Interactive Character Import Tool
Imports Shadowrun characters from markdown files into PostgreSQL
Prompts for missing critical data to ensure quality
"""

import psycopg2
import os
import re
import json
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# PostgreSQL connection from .env
DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', '127.0.0.1'),
    'port': os.getenv('POSTGRES_PORT', '5434'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'database': os.getenv('POSTGRES_DB', 'postgres')
}

CHARACTERS_DIR = r'G:\My Drive\SR-ai\teaching-ai\Characters'

# Critical fields that should prompt if missing
CRITICAL_FIELDS = ['name', 'street_name', 'race']

def parse_character_file(filepath):
    """Parse a character markdown file with comprehensive field extraction"""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    char = {}
    warnings = []
    
    # Extract basic info - try multiple patterns
    
    # Name - try header format first, then list format
    header_match = re.search(r'^#\s+([^(]+)\s*\(([^)]+)\)\s+Character Sheet', content, re.M | re.I)
    if header_match:
        char['name'] = header_match.group(1).strip()
        char['street_name'] = header_match.group(2).strip()
    else:
        name_match = re.search(r'[-*]\s*\*\*Name\*\*:\s*([^\n]+)', content, re.I)
        if name_match:
            char['name'] = name_match.group(1).strip()
        
        street_match = re.search(r'[-*]\s*\*\*(?:Street Name|Steet Name)\*\*:\s*([^\n]+)', content, re.I)
        if street_match:
            char['street_name'] = street_match.group(1).strip()
    
    # Race/Metatype
    race_match = re.search(r'[-*]\s*\*\*Race\*\*:\s*([^\n]+)', content, re.I)
    if race_match:
        char['race'] = race_match.group(1).strip()
    
    # Sex
    sex_match = re.search(r'[-*]\s*\*\*Sex\*\*:\s*([^\n]+)', content, re.I)
    if sex_match:
        char['sex'] = sex_match.group(1).strip()
    
    # Archetype/Concept
    archetype_match = re.search(r'[-*]\s*\*\*(?:Concept|Archetype)\*\*:\s*([^\n]+)', content, re.I)
    if archetype_match:
        char['archetype'] = archetype_match.group(1).strip()
    
    # Description
    desc_match = re.search(r'[-*]\s*\*\*Description\*\*:\s*([^\n]+)', content, re.I)
    if desc_match:
        char['description'] = desc_match.group(1).strip()
    
    # Attributes
    attributes = {}
    attr_section = re.search(r'##\s*Attributes(.*?)(?=##|$)', content, re.S | re.I)
    if attr_section:
        for line in attr_section.group(1).split('\n'):
            attr_match = re.search(r'[-*]\s*\*\*([^*]+)\*\*:\s*(\d+)', line)
            if attr_match:
                attr_name = attr_match.group(1).strip().lower()
                attributes[attr_name] = int(attr_match.group(2))
    
    char['attributes'] = attributes
    
    # Essence
    essence_match = re.search(r'[-*]\s*\*\*Essence\*\*:\s*([\d.]+)', content, re.I)
    if essence_match:
        char['essence'] = float(essence_match.group(1))
    
    # Body Index (for bioware)
    body_index_match = re.search(r'[-*]\s*\*\*Body Index\*\*:\s*([\d.]+)', content, re.I)
    if body_index_match:
        char['body_index'] = float(body_index_match.group(1))
    
    # Magic Rating - defaults to 0 if not present (mundane)
    magic_match = re.search(r'[-*]\s*\*\*Magic(?:\s+Rating)?\*\*:\s*(\d+)', content, re.I)
    if magic_match:
        char['magic'] = int(magic_match.group(1))
    else:
        char['magic'] = 0  # Default to mundane
    
    # Magic Pool (only for magical characters)
    magic_pool_match = re.search(r'[-*]\s*\*\*(?:Magic Pool|Spell Pool)\*\*:\s*(\d+)', content, re.I)
    if magic_pool_match:
        char['magic_pool'] = int(magic_pool_match.group(1))
    
    # Initiate Level
    initiate_match = re.search(r'[-*]\s*\*\*Initiate Level\*\*:\s*(\d+)', content, re.I)
    if initiate_match:
        char['initiate_level'] = int(initiate_match.group(1))
    
    # Metamagics (extract from initiate level line)
    metamagics_match = re.search(r'[-*]\s*\*\*Initiate Level\*\*:\s*\d+\s*\(([^)]+)\)', content, re.I)
    if metamagics_match:
        char['metamagics'] = [m.strip() for m in metamagics_match.group(1).split(',')]
    
    # Tradition
    tradition_match = re.search(r'[-*]\s*\*\*(?:Tradition|Magical Group)\*\*:\s*([^\n]+)', content, re.I)
    if tradition_match:
        char['tradition'] = tradition_match.group(1).strip()
    
    # Totem
    totem_match = re.search(r'##\s*Totem:\s*([^\n]+)', content, re.I)
    if totem_match:
        char['totem'] = totem_match.group(1).strip()
    
    # Karma
    karma_match = re.search(r'[-*]\s*\*\*Karma Pool\*\*:\s*(\d+)', content, re.I)
    if karma_match:
        char['karma_pool'] = int(karma_match.group(1))
    
    # Total Karma Earned
    total_karma_match = re.search(r'[-*]\s*\*\*Total Karma(?:\s+Earned)?\*\*:\s*(\d+)', content, re.I)
    if total_karma_match:
        char['total_karma'] = int(total_karma_match.group(1))
    
    # Karma Available
    karma_avail_match = re.search(r'[-*]\s*\*\*Total Karma Available\*\*:\s*(\d+)', content, re.I)
    if karma_avail_match:
        char['karma_available'] = int(karma_avail_match.group(1))
    
    # Nuyen
    nuyen_match = re.search(r'[-*]\s*\*\*Nuyen\*\*:\s*([\d,]+)', content, re.I)
    if nuyen_match:
        char['nuyen'] = int(nuyen_match.group(1).replace(',', '').replace('¥', ''))
    
    # Lifestyle
    lifestyle_match = re.search(r'[-*]\s*\*\*Lifestyle\*\*:\s*([^\n]+)', content, re.I)
    if lifestyle_match:
        char['lifestyle'] = lifestyle_match.group(1).strip()
    
    # Reaction
    reaction_match = re.search(r'[-*]\s*\*\*Reaction\*\*:\s*(\d+)', content, re.I)
    if reaction_match:
        char['reaction'] = int(reaction_match.group(1))
    
    # Initiative
    init_match = re.search(r'[-*]\s*\*\*Initiative\*\*:\s*([^\n]+)', content, re.I)
    if init_match:
        char['initiative'] = init_match.group(1).strip()
    
    # Combat Pool
    combat_pool_match = re.search(r'[-*]\s*\*\*Combat Pool\*\*:\s*(\d+)', content, re.I)
    if combat_pool_match:
        char['combat_pool'] = int(combat_pool_match.group(1))
    
    # Task Pool (for deckers)
    task_pool_match = re.search(r'[-*]\s*\*\*Task Pool\*\*:\s*(\d+)', content, re.I)
    if task_pool_match:
        char['task_pool'] = int(task_pool_match.group(1))
    
    # Hacking Pool (for deckers)
    hacking_pool_match = re.search(r'[-*]\s*\*\*Hacking Pool\*\*:\s*(\d+)', content, re.I)
    if hacking_pool_match:
        char['hacking_pool'] = int(hacking_pool_match.group(1))
    
    # Skills
    skills = []
    skills_section = re.search(r'##\s*Skills(.*?)(?=##|$)', content, re.S | re.I)
    if skills_section:
        for line in skills_section.group(1).split('\n'):
            # Match "- Skill: Rating" or "- Skill: Rating (Specialization)"
            skill_match = re.search(r'[-*]\s*\*?\*?([^:*]+)\*?\*?:\s*(\d+)(?:\s*\(([^)]+)\))?', line)
            if skill_match:
                skill_name = skill_match.group(1).strip()
                # Skip if it looks like an attribute or stat
                if skill_name.lower() not in ['body', 'quickness', 'strength', 'charisma', 'intelligence', 'willpower']:
                    skill = {
                        'name': skill_name,
                        'rating': int(skill_match.group(2))
                    }
                    if skill_match.group(3):
                        skill['specialization'] = skill_match.group(3).strip()
                    skills.append(skill)
    
    char['skills'] = skills
    
    # Edges
    edges = []
    edges_section = re.search(r'##\s*Edges(?:\s+and\s+Flaws)?(.*?)(?=##|$)', content, re.S | re.I)
    if edges_section:
        for line in edges_section.group(1).split('\n'):
            if '**Edges**' in line or 'Edges:' in line:
                continue
            edge_match = re.search(r'[-*]\s*\*?\*?([^:*\n]+)', line)
            if edge_match and edge_match.group(1).strip():
                edges.append(edge_match.group(1).strip())
    
    if edges:
        char['edges'] = edges
    
    # Flaws
    flaws = []
    flaws_section = re.search(r'\*\*Flaws\*\*:(.*?)(?=##|\*\*[A-Z]|$)', content, re.S | re.I)
    if flaws_section:
        for line in flaws_section.group(1).split('\n'):
            flaw_match = re.search(r'[-*]\s*\*?\*?([^:*\n]+)', line)
            if flaw_match and flaw_match.group(1).strip():
                flaws.append(flaw_match.group(1).strip())
    
    if flaws:
        char['flaws'] = flaws
    
    # Spells (for mages)
    spells = []
    spells_section = re.search(r'##\s*Spells(.*?)(?=##|$)', content, re.S | re.I)
    if spells_section:
        for line in spells_section.group(1).split('\n'):
            spell_match = re.search(r'[-*]\s*\*?\*?([^:]+):\s*Force\s*(\d+)', line, re.I)
            if spell_match:
                spells.append({
                    'name': spell_match.group(1).strip(),
                    'force': int(spell_match.group(2))
                })
            else:
                # Try simpler format
                spell_match2 = re.search(r'[-*]\s*\*?\*?([^\d]+)\s+(\d+)', line)
                if spell_match2:
                    spell_name = spell_match2.group(1).strip()
                    if spell_name and len(spell_name) > 3:  # Avoid false matches
                        spells.append({
                            'name': spell_name,
                            'force': int(spell_match2.group(2))
                        })
    
    if spells:
        char['spells'] = spells
    
    # Adept Powers
    adept_powers = []
    adept_section = re.search(r'##\s*Adept Powers(.*?)(?=##|$)', content, re.S | re.I)
    if adept_section:
        for line in adept_section.group(1).split('\n'):
            power_match = re.search(r'[-*]\s*\*?\*?([^:]+):\s*([\d.]+)\s*point', line, re.I)
            if power_match:
                adept_powers.append({
                    'name': power_match.group(1).strip(),
                    'cost': float(power_match.group(2))
                })
    
    if adept_powers:
        char['adept_powers'] = adept_powers
    
    return char, warnings

def prompt_for_missing(char, field_name, prompt_text, default=None):
    """Prompt user for missing critical field"""
    if field_name in char and char[field_name]:
        return char[field_name]
    
    print(f"\n⚠️  Missing: {field_name}")
    if default:
        response = input(f"{prompt_text} [default: {default}]: ").strip()
        return response if response else default
    else:
        while True:
            response = input(f"{prompt_text}: ").strip()
            if response:
                return response
            print("This field is required. Please enter a value.")

def display_character_summary(char):
    """Display parsed character for review"""
    print("\n" + "="*60)
    print("📋 Parsed Character Data:")
    print("-"*60)
    print(f"Name: {char.get('name', 'MISSING')}")
    print(f"Street Name: {char.get('street_name', 'MISSING')}")
    print(f"Race: {char.get('race', 'MISSING')}")
    print(f"Archetype: {char.get('archetype', 'N/A')}")
    print(f"\nNuyen: {char.get('nuyen', 'MISSING'):,}¥" if char.get('nuyen') else "\nNuyen: MISSING")
    print(f"Karma Pool: {char.get('karma_pool', 'MISSING')}")
    print(f"Total Karma: {char.get('total_karma', 'MISSING')}")
    print(f"\nEssence: {char.get('essence', 'MISSING')}")
    print(f"Magic: {char.get('magic', 0)}")
    if char.get('magic', 0) > 0:
        print(f"Magic Pool: {char.get('magic_pool', 'N/A')}")
        print(f"Initiate Level: {char.get('initiate_level', 'N/A')}")
        if char.get('metamagics'):
            print(f"Metamagics: {', '.join(char['metamagics'])}")
        if char.get('tradition'):
            print(f"Tradition: {char['tradition']}")
    
    if char.get('attributes'):
        print(f"\nAttributes: {len(char['attributes'])} found")
        for attr, val in sorted(char['attributes'].items()):
            print(f"  {attr.title()}: {val}")
    
    if char.get('skills'):
        print(f"\nSkills: {len(char['skills'])} found")
        for skill in char['skills'][:5]:  # Show first 5
            spec = f" ({skill.get('specialization')})" if skill.get('specialization') else ""
            print(f"  {skill['name']}: {skill['rating']}{spec}")
        if len(char['skills']) > 5:
            print(f"  ... and {len(char['skills']) - 5} more")
    
    if char.get('spells'):
        print(f"\nSpells: {len(char['spells'])} found")
    
    if char.get('adept_powers'):
        print(f"\nAdept Powers: {len(char['adept_powers'])} found")
    
    print("="*60)

def import_character(conn, char):
    """Import character into PostgreSQL database"""
    
    cursor = conn.cursor()
    
    try:
        # Prepare attributes as JSONB
        attributes_json = json.dumps(char.get('attributes', {}))
        
        # Prepare skills as JSONB array
        skills_json = json.dumps(char.get('skills', []))
        
        # Prepare optional JSONB fields
        extra_data = {}
        if char.get('edges'):
            extra_data['edges'] = char['edges']
        if char.get('flaws'):
            extra_data['flaws'] = char['flaws']
        if char.get('spells'):
            extra_data['spells'] = char['spells']
        if char.get('adept_powers'):
            extra_data['adept_powers'] = char['adept_powers']
        if char.get('metamagics'):
            extra_data['metamagics'] = char['metamagics']
        if char.get('tradition'):
            extra_data['tradition'] = char['tradition']
        if char.get('totem'):
            extra_data['totem'] = char['totem']
        if char.get('initiate_level'):
            extra_data['initiate_level'] = char['initiate_level']
        if char.get('magic_pool'):
            extra_data['magic_pool'] = char['magic_pool']
        if char.get('task_pool'):
            extra_data['task_pool'] = char['task_pool']
        if char.get('hacking_pool'):
            extra_data['hacking_pool'] = char['hacking_pool']
        if char.get('lifestyle'):
            extra_data['lifestyle'] = char['lifestyle']
        if char.get('description'):
            extra_data['description'] = char['description']
        if char.get('sex'):
            extra_data['sex'] = char['sex']
        
        extra_data_json = json.dumps(extra_data) if extra_data else '{}'
        
        # Insert character
        cursor.execute('''
            INSERT INTO characters (
                name, street_name, character_type, archetype,
                attributes, skills, combat_pool,
                nuyen, karma_pool, karma_total,
                initiative, notes,
                created_at, updated_at
            ) VALUES (
                %s, %s, %s, %s,
                %s::jsonb, %s::jsonb, %s,
                %s, %s, %s,
                %s, %s::jsonb,
                %s, %s
            ) RETURNING id
        ''', (
            char['name'],
            char['street_name'],
            char.get('race'),  # character_type in schema
            char.get('archetype'),
            attributes_json,
            skills_json,
            char.get('combat_pool', 0),
            char.get('nuyen', 0),
            char.get('karma_pool', 0),
            char.get('total_karma', 0),
            char.get('initiative', '1d6'),
            extra_data_json,
            datetime.now(),
            datetime.now()
        ))
        
        char_id = cursor.fetchone()[0]
        
        conn.commit()
        return char_id
        
    except Exception as e:
        conn.rollback()
        raise e

def main():
    """Main import process"""
    
    print("🎲 Shadowrun Character Import Tool")
    print("="*60)
    print(f"Source: {CHARACTERS_DIR}")
    print(f"Database: PostgreSQL at {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print("="*60)
    
    # Find character files
    if not os.path.exists(CHARACTERS_DIR):
        print(f"\n❌ Directory not found: {CHARACTERS_DIR}")
        return
    
    files = []
    
    # Numbered files (version 13)
    for i in [1, 2, 3, 4, 6]:
        pattern = f"{i}-*_Updated_Character_Sheet*13*.markdown"
        matches = list(Path(CHARACTERS_DIR).glob(pattern))
        if matches:
            files.append(matches[0])
    
    # Raven (different format)
    raven_file = Path(CHARACTERS_DIR) / "Raven Character Sheet.markdown"
    if raven_file.exists():
        files.append(raven_file)
    
    print(f"\n📁 Found {len(files)} character files to import\n")
    
    if not files:
        print("❌ No character files found")
        return
    
    # Connect to database
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("✅ Connected to PostgreSQL\n")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return
    
    imported = 0
    
    for filepath in files:
        print("\n" + "="*60)
        print(f"📄 Processing: {filepath.name}")
        print("="*60)
        
        # Parse file
        char, warnings = parse_character_file(filepath)
        
        # Display what we found
        display_character_summary(char)
        
        # Show warnings
        if warnings:
            print("\n⚠️  Warnings:")
            for warning in warnings:
                print(f"  - {warning}")
        
        # Prompt for missing critical fields
        print("\n🔍 Checking critical fields...")
        
        char['name'] = prompt_for_missing(
            char, 'name', 
            "Enter character's full name",
            default=filepath.stem.split('_')[0] if '_' in filepath.stem else None
        )
        
        char['street_name'] = prompt_for_missing(
            char, 'street_name',
            "Enter street name/handle"
        )
        
        char['race'] = prompt_for_missing(
            char, 'race',
            "Enter race/metatype (Human/Elf/Dwarf/Ork/Troll/Shapeshifter)",
            default="Human"
        )
        
        # Confirm import
        print(f"\n✅ Ready to import: {char['name']} \"{char['street_name']}\"")
        confirm = input("Import this character? [Y/n]: ").strip().lower()
        
        if confirm in ['', 'y', 'yes']:
            try:
                char_id = import_character(conn, char)
                print(f"✅ Imported successfully! Character ID: {char_id}")
                imported += 1
            except Exception as e:
                print(f"❌ Import failed: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("⏭️  Skipped")
    
    conn.close()
    
    print("\n" + "="*60)
    print(f"✅ Import Complete! Imported {imported} of {len(files)} characters")
    print("="*60)

if __name__ == '__main__':
    main()
