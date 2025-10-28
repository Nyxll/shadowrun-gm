#!/usr/bin/env python3
"""
Enhanced character import that properly parses cyberware/bioware/spell modifiers
"""
import os
import re
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row
from typing import Dict, List

load_dotenv()

class EnhancedCharacterImporter:
    """Import characters with comprehensive modifier parsing"""
    
    def __init__(self):
        self.conn = psycopg.connect(
            host=os.getenv('POSTGRES_HOST'),
            port=os.getenv('POSTGRES_PORT'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            dbname=os.getenv('POSTGRES_DB'),
            row_factory=dict_row
        )
        self.cursor = self.conn.cursor()
    
    def parse_character_file(self, filepath: str) -> Dict:
        """Parse a character markdown file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        char_data = {
            'name': '',
            'street_name': '',
            'archetype': '',
            'metatype': '',
            'attributes': {},
            'skills': {},
            'cyberware': [],
            'bioware': [],
            'spells': [],
            'gear': [],
            'nuyen': 0,
            'karma_pool': 0,
            'karma_total': 0,
            'essence': 6.0,
            'initiative': ''
        }
        
        # Extract basic info
        name_match = re.search(r'\*\*Name\*\*:\s*(.+)', content)
        if name_match:
            char_data['name'] = name_match.group(1).strip()
        
        street_match = re.search(r'\*\*Street Name\*\*:\s*(.+)', content)
        if street_match:
            char_data['street_name'] = street_match.group(1).strip()
        
        archetype_match = re.search(r'\*\*Archetype\*\*:\s*(.+)', content)
        if archetype_match:
            char_data['archetype'] = archetype_match.group(1).strip()
        
        metatype_match = re.search(r'\*\*Metatype\*\*:\s*(.+)', content)
        if metatype_match:
            char_data['metatype'] = metatype_match.group(1).strip()
        
        # Extract attributes - look for current values with base in parentheses
        attr_section = re.search(r'### Base Form\s*\n(.*?)(?:\n###|\n---|\n##)', content, re.DOTALL)
        if attr_section:
            for line in attr_section.group(1).split('\n'):
                # Match "- **Body**: 10 (9 base +1 Supra-Thyroid)" or "- **Body**: 10"
                match = re.match(r'-\s*\*\*(\w+)\*\*:\s*(\d+)', line)
                if match:
                    attr_name = match.group(1).lower()
                    value = int(match.group(2))
                    char_data['attributes'][attr_name] = value
        
        # Extract skills
        skills_section = re.search(r'### Active Skills\s*\n(.*?)(?:\n###|\n---|\n##)', content, re.DOTALL)
        if skills_section:
            for line in skills_section.group(1).split('\n'):
                match = re.match(r'-\s*\*\*([^*]+)\*\*:\s*(\d+)', line)
                if match:
                    skill_name = match.group(1).strip()
                    rating = int(match.group(2))
                    char_data['skills'][skill_name] = {'rating': rating, 'specialization': None}
        
        # Extract cyberware
        cyber_section = re.search(r'### Cyberware\s*\n(.*?)(?:\n###|\n---|\n##)', content, re.DOTALL)
        if cyber_section:
            current_item = None
            for line in cyber_section.group(1).split('\n'):
                line = line.strip()
                if line.startswith('- **') and '**' in line[4:]:
                    item_match = re.match(r'-\s*\*\*([^*]+)\*\*', line)
                    if item_match:
                        current_item = {
                            'name': item_match.group(1).strip(),
                            'essence': 0.0,
                            'effects': []
                        }
                        essence_match = re.search(r'\(([0-9.]+)\s*Essence\)', line)
                        if essence_match:
                            current_item['essence'] = float(essence_match.group(1))
                        char_data['cyberware'].append(current_item)
                elif line.startswith('-') and current_item:
                    current_item['effects'].append(line[1:].strip())
        
        # Extract bioware
        bio_section = re.search(r'### Bioware\s*\n(.*?)(?:\n###|\n---|\n##)', content, re.DOTALL)
        if bio_section:
            current_item = None
            for line in bio_section.group(1).split('\n'):
                line = line.strip()
                if line.startswith('- **') and '**' in line[4:]:
                    item_match = re.match(r'-\s*\*\*([^*]+)\*\*', line)
                    if item_match:
                        current_item = {
                            'name': item_match.group(1).strip(),
                            'body_index': 0.0,
                            'effects': []
                        }
                        bi_match = re.search(r'\(([0-9.]+)\s*Body Index\)', line)
                        if bi_match:
                            current_item['body_index'] = float(bi_match.group(1))
                        char_data['bioware'].append(current_item)
                elif line.startswith('-') and current_item:
                    current_item['effects'].append(line[1:].strip())
        
        # Extract spells
        spells_section = re.search(r'### Spells\s*\n(.*?)(?:\n###|\n---|\n##)', content, re.DOTALL)
        if spells_section:
            for line in spells_section.group(1).split('\n'):
                if line.strip().startswith('- **') and line.strip() != '- **None**':
                    spell_match = re.match(r'-\s*\*\*([^*]+)\*\*', line)
                    if spell_match:
                        char_data['spells'].append(spell_match.group(1).strip())
        
        # Extract gear
        gear_section = re.search(r'## Gear\s*\n(.*?)(?:\n---|\n##)', content, re.DOTALL)
        if gear_section:
            current_category = None
            for line in gear_section.group(1).split('\n'):
                if line.strip().startswith('### '):
                    current_category = line.strip()[4:]
                elif line.strip().startswith('- **'):
                    item_match = re.match(r'-\s*\*\*([^*]+)\*\*', line)
                    if item_match:
                        char_data['gear'].append({
                            'category': current_category,
                            'name': item_match.group(1).strip(),
                            'text': line.strip()[2:]
                        })
        
        # Extract numeric values
        nuyen_match = re.search(r'\*\*Nuyen\*\*:\s*([\d,]+)', content)
        if nuyen_match:
            char_data['nuyen'] = int(nuyen_match.group(1).replace(',', '').replace('¥', ''))
        
        karma_pool_match = re.search(r'\*\*Karma Pool\*\*:\s*(\d+)', content)
        if karma_pool_match:
            char_data['karma_pool'] = int(karma_pool_match.group(1))
        
        karma_total_match = re.search(r'\*\*Total Karma Earned\*\*:\s*(\d+)', content)
        if karma_total_match:
            char_data['karma_total'] = int(karma_total_match.group(1))
        
        essence_match = re.search(r'\*\*Essence\*\*:\s*([\d.]+)', content)
        if essence_match:
            char_data['essence'] = float(essence_match.group(1))
        
        initiative_match = re.search(r'\*\*Initiative\*\*:\s*(.+)', content)
        if initiative_match:
            char_data['initiative'] = initiative_match.group(1).strip()
        
        return char_data
    
    def parse_modifiers_from_cyberware(self, cyber_item: Dict) -> List[Dict]:
        """Parse modifiers from cyberware effects"""
        modifiers = []
        name = cyber_item['name']
        
        for effect in cyber_item['effects']:
            effect_lower = effect.lower()
            
            # Attribute bonuses
            for attr in ['body', 'quickness', 'strength', 'charisma', 'intelligence', 'willpower', 'reaction']:
                pattern = rf'\+(\d+)\s+{attr}'
                match = re.search(pattern, effect_lower)
                if match:
                    modifiers.append({
                        'type': 'attribute',
                        'target': attr,
                        'value': int(match.group(1)),
                        'source': name,
                        'source_type': 'cyberware'
                    })
            
            # Initiative dice
            if '+' in effect and 'd6' in effect_lower:
                dice_match = re.search(r'\+(\d+)d6', effect_lower)
                if dice_match:
                    modifiers.append({
                        'type': 'initiative_dice',
                        'target': 'initiative',
                        'value': int(dice_match.group(1)),
                        'source': name,
                        'source_type': 'cyberware'
                    })
            
            # Task Pool bonuses
            if 'task pool' in effect_lower:
                pool_match = re.search(r'\+(\d+)\s+task pool', effect_lower)
                if pool_match:
                    modifiers.append({
                        'type': 'pool',
                        'target': 'task_pool',
                        'value': int(pool_match.group(1)),
                        'source': name,
                        'source_type': 'cyberware'
                    })
            
            # Smartlink TN reduction
            if 'tn' in effect_lower and ('-' in effect or 'reduction' in effect_lower):
                tn_match = re.search(r'-(\d+)\s+tn', effect_lower)
                if tn_match:
                    modifiers.append({
                        'type': 'tn_modifier',
                        'target': 'firearms',
                        'value': -int(tn_match.group(1)),
                        'source': name,
                        'source_type': 'cyberware'
                    })
            
            # Dice bonuses for skills
            if 'dice' in effect_lower and '+' in effect:
                dice_match = re.search(r'\+(\d+)\s+dice', effect_lower)
                if dice_match:
                    skill = 'unknown'
                    if 'computer' in effect_lower or 'technical' in effect_lower:
                        skill = 'computer'
                    elif 'social' in effect_lower:
                        skill = 'social'
                    elif 'calculation' in effect_lower:
                        skill = 'calculations'
                    
                    modifiers.append({
                        'type': 'skill_dice',
                        'target': skill,
                        'value': int(dice_match.group(1)),
                        'source': name,
                        'source_type': 'cyberware'
                    })
        
        return modifiers
    
    def parse_modifiers_from_bioware(self, bio_item: Dict) -> List[Dict]:
        """Parse modifiers from bioware effects"""
        modifiers = []
        name = bio_item['name']
        
        for effect in bio_item['effects']:
            effect_lower = effect.lower()
            
            # Attribute bonuses
            for attr in ['body', 'quickness', 'strength', 'charisma', 'intelligence', 'willpower', 'reaction']:
                pattern = rf'\+(\d+)\s+{attr}'
                match = re.search(pattern, effect_lower)
                if match:
                    modifiers.append({
                        'type': 'attribute',
                        'target': attr,
                        'value': int(match.group(1)),
                        'source': name,
                        'source_type': 'bioware'
                    })
            
            # Skill dice bonuses
            if 'dice' in effect_lower and '+' in effect:
                dice_match = re.search(r'\+(\d+)\s+dice', effect_lower)
                if dice_match:
                    skill = 'unknown'
                    if 'physical' in effect_lower:
                        skill = 'physical_skills'
                    elif 'social' in effect_lower:
                        skill = 'social'
                    elif 'knowledge' in effect_lower or 'language' in effect_lower:
                        skill = 'knowledge_language'
                    elif 'technical' in effect_lower:
                        skill = 'technical'
                    
                    modifiers.append({
                        'type': 'skill_dice',
                        'target': skill,
                        'value': int(dice_match.group(1)),
                        'source': name,
                        'source_type': 'bioware'
                    })
            
            # Task Pool bonuses
            if 'task pool' in effect_lower:
                pool_match = re.search(r'\+(\d+)\s+task pool', effect_lower)
                if pool_match:
                    modifiers.append({
                        'type': 'pool',
                        'target': 'task_pool',
                        'value': int(pool_match.group(1)),
                        'source': name,
                        'source_type': 'bioware'
                    })
        
        return modifiers
    
    def calculate_base_attributes(self, char_data: Dict) -> Dict:
        """Calculate base attributes by subtracting all modifiers"""
        current_attrs = char_data['attributes'].copy()
        base_attrs = current_attrs.copy()
        
        # Collect all attribute modifiers
        all_modifiers = []
        for cyber in char_data['cyberware']:
            all_modifiers.extend(self.parse_modifiers_from_cyberware(cyber))
        for bio in char_data['bioware']:
            all_modifiers.extend(self.parse_modifiers_from_bioware(bio))
        
        # Subtract attribute modifiers to get base
        for mod in all_modifiers:
            if mod['type'] == 'attribute' and mod['target'] in base_attrs:
                base_attrs[mod['target']] -= mod['value']
        
        # Ensure all attributes exist
        for attr in ['body', 'quickness', 'strength', 'charisma', 'intelligence', 'willpower', 'reaction', 'magic
