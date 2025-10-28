#!/usr/bin/env python3
"""
Parse cyberware/bioware sections from character sheets and add modifiers
Run this after importing characters to add all the modifiers
"""
import os
import re
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row

load_dotenv()

def parse_cyberware_bioware(filepath: str):
    """Parse cyberware, bioware, and spell lock sections from character file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    modifiers = []
    
    # Get character name for reference
    name_match = re.search(r'\*\*Name\*\*:\s*(.+)', content)
    char_name = name_match.group(1).strip() if name_match else 'Unknown'
    
    # Parse Cyberware section
    cyber_section = re.search(r'### Cyberware\s*\n(.*?)(?:\n###|\n---|\n##)', content, re.DOTALL)
    if cyber_section:
        current_item = None
        for line in cyber_section.group(1).split('\n'):
            line = line.strip()
            if line.startswith('- **') and '**' in line[4:]:
                # New cyberware item
                item_match = re.match(r'-\s*\*\*([^*]+)\*\*', line)
                if item_match:
                    current_item = item_match.group(1).strip()
            elif line.startswith('-') and current_item:
                # Effect line - parse for modifiers
                effect = line[1:].strip()
                mods = parse_effect_line(effect, current_item, 'cyberware')
                modifiers.extend(mods)
    
    # Parse Bioware section
    bio_section = re.search(r'### Bioware\s*\n(.*?)(?:\n###|\n---|\n##)', content, re.DOTALL)
    if bio_section:
        current_item = None
        for line in bio_section.group(1).split('\n'):
            line = line.strip()
            if line.startswith('- **') and '**' in line[4:]:
                # New bioware item
                item_match = re.match(r'-\s*\*\*([^*]+)\*\*', line)
                if item_match:
                    current_item = item_match.group(1).strip()
            elif line.startswith('-') and current_item:
                # Effect line - parse for modifiers
                effect = line[1:].strip()
                mods = parse_effect_line(effect, current_item, 'bioware')
                modifiers.extend(mods)
    
    # Parse Spell Locks/Quickened Spells section
    spell_section = re.search(r'### Spell Locks/Quickened Spells\s*\n(.*?)(?:\n###|\n---|\n##)', content, re.DOTALL)
    if spell_section:
        current_spell = None
        for line in spell_section.group(1).split('\n'):
            line = line.strip()
            if line.startswith('- **') and '**' in line[4:]:
                # New spell
                spell_match = re.match(r'-\s*\*\*([^*]+)\*\*', line)
                if spell_match:
                    current_spell = spell_match.group(1).strip()
            elif line.startswith('-') and current_spell and 'Effect:' in line:
                # Effect line - parse for modifiers
                effect = line[1:].strip()
                mods = parse_spell_effect(effect, current_spell)
                modifiers.extend(mods)
    
    # Also check magical items for spell locks
    magic_items_section = re.search(r'### Magical Items.*?\n(.*?)(?:\n###|\n---|\n##)', content, re.DOTALL)
    if magic_items_section:
        current_item = None
        for line in magic_items_section.group(1).split('\n'):
            line = line.strip()
            if line.startswith('- **') and '**' in line[4:]:
                item_match = re.match(r'-\s*\*\*([^*]+)\*\*', line)
                if item_match:
                    current_item = item_match.group(1).strip()
            elif current_item and 'spell lock' in current_item.lower():
                if 'Bonuses:' in line or 'sustains' in line.lower():
                    # Parse spell lock bonuses
                    mods = parse_spell_lock_item(line, current_item)
                    modifiers.extend(mods)
    
    return char_name, modifiers


def parse_effect_line(effect: str, source: str, source_type: str):
    """Parse a single effect line for modifiers"""
    modifiers = []
    effect_lower = effect.lower()
    
    # Attribute bonuses (e.g., "+6 Reaction", "+3 Intelligence")
    for attr in ['body', 'quickness', 'strength', 'charisma', 'intelligence', 'willpower', 'reaction']:
        pattern = rf'\+(\d+)\s+{attr}'
        match = re.search(pattern, effect_lower)
        if match:
            modifiers.append({
                'type': 'attribute',
                'target': attr,
                'value': int(match.group(1)),
                'source': source,
                'source_type': source_type
            })
    
    # Initiative dice (e.g., "+3D6 Initiative")
    if 'd6' in effect_lower and 'initiative' in effect_lower:
        dice_match = re.search(r'\+(\d+)d6', effect_lower)
        if dice_match:
            modifiers.append({
                'type': 'initiative_dice',
                'target': 'initiative',
                'value': int(dice_match.group(1)),
                'source': source,
                'source_type': source_type
            })
    
    # Task Pool bonuses
    if 'task pool' in effect_lower:
        pool_match = re.search(r'\+(\d+)\s+task pool', effect_lower)
        if pool_match:
            modifiers.append({
                'type': 'pool',
                'target': 'task_pool',
                'value': int(pool_match.group(1)),
                'source': source,
                'source_type': source_type
            })
    
    # TN modifiers (e.g., "-3 TN")
    if 'tn' in effect_lower and '-' in effect:
        tn_match = re.search(r'-(\d+)\s+tn', effect_lower)
        if tn_match:
            # Determine target from context
            target = 'firearms' if 'firearm' in effect_lower or 'smartlink' in source.lower() else 'general'
            modifiers.append({
                'type': 'tn_modifier',
                'target': target,
                'value': -int(tn_match.group(1)),
                'source': source,
                'source_type': source_type
            })
    
    # Dice bonuses (e.g., "+2 dice", "+4 dice for calculations")
    if 'dice' in effect_lower and '+' in effect:
        dice_match = re.search(r'\+(\d+)\s+dice', effect_lower)
        if dice_match:
            # Determine target from context
            target = 'unknown'
            if 'physical' in effect_lower:
                target = 'physical_skills'
            elif 'social' in effect_lower:
                target = 'social'
            elif 'knowledge' in effect_lower or 'language' in effect_lower:
                target = 'knowledge_language'
            elif 'technical' in effect_lower:
                target = 'technical'
            elif 'computer' in effect_lower:
                target = 'computer'
            elif 'calculation' in effect_lower:
                target = 'calculations'
            
            modifiers.append({
                'type': 'skill_dice',
                'target': target,
                'value': int(dice_match.group(1)),
                'source': source,
                'source_type': source_type
            })
    
    # Matrix Initiative (e.g., "+2D6 Matrix Initiative")
    if 'matrix initiative' in effect_lower and 'd6' in effect_lower:
        dice_match = re.search(r'\+(\d+)d6', effect_lower)
        if dice_match:
            modifiers.append({
                'type': 'matrix_initiative_dice',
                'target': 'matrix_initiative',
                'value': int(dice_match.group(1)),
                'source': source,
                'source_type': source_type
            })
    
    return modifiers


def parse_spell_effect(effect: str, spell_name: str):
    """Parse spell effect line for modifiers"""
    modifiers = []
    effect_lower = effect.lower()
    
    # Remove "Effect:" prefix if present
    if effect_lower.startswith('effect:'):
        effect = effect[7:].strip()
        effect_lower = effect.lower()
    
    # Initiative dice (e.g., "+3D6 Initiative")
    if 'd6' in effect_lower and 'initiative' in effect_lower:
        dice_match = re.search(r'\+(\d+)d6', effect_lower)
        if dice_match:
            modifiers.append({
                'type': 'initiative_dice',
                'target': 'initiative',
                'value': int(dice_match.group(1)),
                'source': f'Quickened: {spell_name}',
                'source_type': 'spell'
            })
    
    # Reaction bonus (e.g., "+3 Reaction")
    if 'reaction' in effect_lower and '+' in effect:
        reaction_match = re.search(r'\+(\d+)\s+reaction', effect_lower)
        if reaction_match:
            modifiers.append({
                'type': 'attribute',
                'target': 'reaction',
                'value': int(reaction_match.group(1)),
                'source': f'Quickened: {spell_name}',
                'source_type': 'spell'
            })
    
    # Attribute bonuses (e.g., "+4 Charisma, +4 Intelligence, +4 Willpower")
    for attr in ['body', 'quickness', 'strength', 'charisma', 'intelligence', 'willpower']:
        pattern = rf'\+(\d+)\s+{attr}'
        match = re.search(pattern, effect_lower)
        if match:
            modifiers.append({
                'type': 'attribute',
                'target': attr,
                'value': int(match.group(1)),
                'source': f'Quickened: {spell_name}',
                'source_type': 'spell'
            })
    
    return modifiers


def parse_spell_lock_item(line: str, item_name: str):
    """Parse spell lock item bonuses"""
    modifiers = []
    line_lower = line.lower()
    
    # Look for "Sustains X" pattern
    if 'sustains' in line_lower:
        # Extract spell name and effects
        if 'increase reflex' in line_lower or 'increase reflexes' in line_lower:
            # Parse the level
            level_match = re.search(r'reflex(?:es)?\s+\+?(\d+)', line_lower)
            if level_match:
                level = int(level_match.group(1))
                modifiers.append({
                    'type': 'initiative_dice',
                    'target': 'initiative',
                    'value': level,
                    'source': f'Spell Lock: Increase Reflexes +{level}',
                    'source_type': 'spell'
                })
    
    return modifiers


def main():
    """Process all character files and add modifiers"""
    conn = psycopg.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB'),
        row_factory=dict_row
    )
    cursor = conn.cursor()
    
    char_dir = 'characters'
    files = [f for f in os.listdir(char_dir) if f.endswith('.md') and f != 'README.md']
    
    print("Adding cyberware/bioware modifiers...")
    print("=" * 70)
    
    for filename in files:
        filepath = os.path.join(char_dir, filename)
        char_name, modifiers = parse_cyberware_bioware(filepath)
        
        if not modifiers:
            print(f"\n{char_name}: No modifiers found")
            continue
        
        # Get character ID
        cursor.execute("SELECT id FROM characters WHERE name = %s", (char_name,))
        result = cursor.fetchone()
        if not result:
            print(f"\n{char_name}: Character not found in database")
            continue
        
        char_id = result['id']
        print(f"\n{char_name}:")
        
        # Insert modifiers
        for mod in modifiers:
            cursor.execute("""
                INSERT INTO character_modifiers (
                    character_id, modifier_type, target_name, modifier_value,
                    source, source_type, is_permanent
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (char_id, mod['type'], mod['target'], mod['value'],
                  mod['source'], mod['source_type'], True))
            
            print(f"  + {mod['source']}: {mod['type']} {mod['target']} {mod['value']:+d}")
        
        conn.commit()
        print(f"  ✓ Added {len(modifiers)} modifiers")
    
    print("\n" + "=" * 70)
    print("✓ All modifiers added!")
    
    cursor.close()
    conn.close()


if __name__ == "__main__":
    main()
