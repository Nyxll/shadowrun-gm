#!/usr/bin/env python3
"""
Import character sheets v8 - PROPER FIXES
- Handles BOTH plain numbers (Block) AND parenthetical format
- Stores explanations WITHOUT creating orphaned modifiers  
- Fixes multi-target modifiers (ONE modifier, not duplicates)
- Preserves vehicle descriptions
"""
import os
import re
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row
from typing import Dict, List, Tuple, Optional

load_dotenv()

class CharacterImporterV8:
    """Import characters with proper handling of all formats"""
    
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
    
    def parse_stat_with_modifiers(self, stat_line: str) -> Tuple[int, Optional[int], str]:
        """
        Parse BOTH formats:
        - Plain number: "6" (Block's format)
        - Parenthetical: "6 (10) (+4 from source)"
        
        Returns: (base_value, modified_value, explanation_text)
        """
        stat_line = stat_line.strip()
        
        # Try: base (modified) (explanation)
        match = re.match(r'^(\d+)\s*\((\d+)\)\s*\(([^)]+)\)\s*$', stat_line)
        if match:
            return (int(match.group(1)), int(match.group(2)), match.group(3))
        
        # Try: base (modified)
        match = re.match(r'^(\d+)\s*\((\d+)\)\s*$', stat_line)
        if match:
            return (int(match.group(1)), int(match.group(2)), '')
        
        # Try: base (explanation)
        match = re.match(r'^(\d+)\s*\(([^)]+)\)\s*$', stat_line)
        if match:
            explanation = match.group(2)
            # Check if it's a number (modified value) or text (explanation)
            if explanation.isdigit():
                return (int(match.group(1)), int(explanation), '')
            else:
                return (int(match.group(1)), None, explanation)
        
        # Plain number (Block's format)
        match = re.match(r'^(\d+)\s*$', stat_line)
        if match:
            return (int(match.group(1)), None, '')
        
        # Fallback
        return (0, None, '')
    
    def extract_modifiers_from_explanation(self, explanations: List[str], attr_name: str) -> List[Dict]:
        """
        Extract structured modifiers from explanation text
        Example: "+4 from Quickened Increase Attribute +4 force 3"
        Returns list of modifier dicts
        """
        modifiers = []
        
        for exp in explanations:
            # Pattern: +X from SOURCE or +X SOURCE
            match = re.match(r'([+-]\d+)\s+(?:from\s+)?(.+)', exp.strip())
            if match:
                value = int(match.group(1))
                source = match.group(2).strip()
                
                # Determine modifier type and source_type
                source_type = 'unknown'
                if 'quickened' in source.lower() or 'spell' in source.lower():
                    source_type = 'spell'
                elif 'cyber' in source.lower():
                    source_type = 'cyberware'
                elif any(bio in source.lower() for bio in ['bioware', 'muscle', 'cerebral', 'supra-thyroid', 'enhanced articulation']):
                    source_type = 'bioware'
                elif 'smartlink' in source.lower() or 'smartgun' in source.lower():
                    source_type = 'cyberware'
                    # This is a TN modifier, not attribute
                    continue
                
                modifiers.append({
                    'type': 'attribute',
                    'target': attr_name.lower(),
                    'value': value,
                    'source': source,
                    'source_type': source_type
                })
        
        return modifiers
    
    def parse_modifier_line(self, line: str) -> List[Dict]:
        """
        Parse modifier line - ALWAYS returns at least one modifier with description
        Tries to extract structured data, but falls back to generic modifier
        """
        original_line = line.strip()
        if not original_line:
            return []
        
        # Try to parse for structured data, but ALWAYS include description
        modifiers = []
        
        # Pattern 1: +XDY Initiative (e.g., "+3D6 Initiative")
        init_match = re.match(r'([+-])(\d+)D(\d+)\s+Initiative', line, re.IGNORECASE)
        if init_match:
            sign = init_match.group(1)
            num_dice = int(init_match.group(2))
            value = num_dice if sign == '+' else -num_dice
            return [{
                'modifier_type': 'initiative',
                'target_name': 'initiative_dice',
                'modifier_value': value,
                'description': original_line
            }]
        
        # Pattern 2: +X ATTRIBUTE(S) - handles multiple attributes or single
        attr_match = re.match(r'([+-]\d+)\s+((?:Body|Quickness|Strength|Charisma|Intelligence|Willpower|Reaction|Essence|Magic)(?:(?:/|,\s*)(?:Body|Quickness|Strength|Charisma|Intelligence|Willpower|Reaction|Essence|Magic))*)', line, re.IGNORECASE)
        if attr_match:
            value = int(attr_match.group(1))
            # Split on both / and comma
            attrs = re.split(r'[/,]\s*', attr_match.group(2))
            for attr in attrs:
                attr = attr.strip()
                if attr:
                    modifiers.append({
                        'modifier_type': 'attribute',
                        'target_name': attr.lower(),
                        'modifier_value': value,
                        'description': original_line
                    })
            return modifiers
        
        # Pattern 3: +X die/dice to physical skills - CREATE ONE MODIFIER, NOT 6!
        phys_skill_match = re.match(r'([+-]\d+)\s+(?:die|dice)\s+to\s+physical\s+skills?', line, re.IGNORECASE)
        if phys_skill_match:
            value = int(phys_skill_match.group(1))
            return [{
                'modifier_type': 'skill',
                'target_name': 'physical_skills',  # ONE modifier for all physical skills
                'modifier_value': value,
                'description': original_line
            }]
        
        # Pattern 4: +X die/dice to Knowledge/Language skills
        know_skill_match = re.match(r'([+-]\d+)\s+(?:die|dice)\s+to\s+Knowledge/Language\s+skills?', line, re.IGNORECASE)
        if know_skill_match:
            value = int(know_skill_match.group(1))
            return [{
                'modifier_type': 'skill',
                'target_name': 'knowledge/language skills',
                'modifier_value': value,
                'description': original_line
            }]
        
        # Pattern 5: +X SPECIFIC_SKILL (e.g., "+1 Firearms")
        specific_skill_match = re.match(r'([+-]\d+)\s+([A-Za-z\s]+?)(?:\s|$)', line)
        if specific_skill_match:
            value = int(specific_skill_match.group(1))
            skill_name = specific_skill_match.group(2).strip().lower()
            # Check if it's a known skill
            if skill_name in ['firearms', 'gunnery', 'athletics', 'stealth', 'whips', 'monowhip']:
                return [{
                    'modifier_type': 'skill',
                    'target_name': skill_name,
                    'modifier_value': value,
                    'description': original_line
                }]
        
        # Pattern 6: -X TN (combat modifier)
        tn_match = re.match(r'([+-]\d+)\s+TN', line, re.IGNORECASE)
        if tn_match:
            return [{
                'modifier_type': 'combat',
                'target_name': 'ranged_tn',
                'modifier_value': int(tn_match.group(1)),
                'description': original_line
            }]
        
        # Pattern 7: Vision enhancements
        if 'thermographic' in line.lower():
            return [{'modifier_type': 'vision', 'target_name': 'thermographic', 'modifier_value': 1, 'description': original_line}]
        elif 'low-light' in line.lower() or 'low light' in line.lower():
            return [{'modifier_type': 'vision', 'target_name': 'lowLight', 'modifier_value': 1, 'description': original_line}]
        elif 'optical magnification' in line.lower():
            mag_match = re.search(r'optical\s+magnification\s+(\d+)', line, re.IGNORECASE)
            if mag_match:
                return [{'modifier_type': 'vision', 'target_name': 'magnification', 'modifier_value': int(mag_match.group(1)), 'description': original_line}]
        elif 'flare compensation' in line.lower():
            return [{'modifier_type': 'vision', 'target_name': 'flare_compensation', 'modifier_value': 1, 'description': original_line}]
        
        # Pattern 8: Task Pool
        task_match = re.match(r'([+-]\d+)\s+Task Pool', line, re.IGNORECASE)
        if task_match:
            return [{'modifier_type': 'pool', 'target_name': 'task_pool', 'modifier_value': int(task_match.group(1)), 'description': original_line}]
        
        # Pattern 9: Hacking Pool
        hack_pool_match = re.match(r'([+-]\d+)\s+(?:dice?\s+)?for\s+Hacking\s+pool', line, re.IGNORECASE)
        if hack_pool_match:
            return [{'modifier_type': 'pool', 'target_name': 'hacking_pool', 'modifier_value': int(hack_pool_match.group(1)), 'description': original_line}]
        
        # Pattern 10: Conditional skill bonuses (e.g., "+4 dice for Computer tests involving calculations")
        cond_skill_match = re.match(r'([+-]\d+)\s+(?:dice?\s+)?for\s+(\w+)\s+tests?\s+involving\s+(.+)', line, re.IGNORECASE)
        if cond_skill_match:
            value = int(cond_skill_match.group(1))
            skill = cond_skill_match.group(2).lower()
            condition = cond_skill_match.group(3).strip()
            return [{
                'modifier_type': 'skill',
                'target_name': skill,
                'modifier_value': value,
                'condition': condition,
                'description': original_line
            }]
        
        # Pattern 11: Technical skills (e.g., "+2 dice for technical and technical B/R skills")
        tech_skill_match = re.match(r'([+-]\d+)\s+(?:dice?\s+)?for\s+technical(?:\s+and\s+technical\s+B/R)?\s+skills?', line, re.IGNORECASE)
        if tech_skill_match:
            value = int(tech_skill_match.group(1))
            return [{
                'modifier_type': 'skill',
                'target_name': 'technical_skills',
                'modifier_value': value,
                'description': original_line
            }]
        
        # Pattern 12: "Increases ATTRIBUTE by X" format
        inc_attr_match = re.match(r'Increases?\s+(\w+)\s+by\s+([+-]?\d+)', line, re.IGNORECASE)
        if inc_attr_match:
            attr = inc_attr_match.group(1).lower()
            value = int(inc_attr_match.group(2))
            return [{
                'modifier_type': 'attribute',
                'target_name': attr,
                'modifier_value': value,
                'description': original_line
            }]
        
        # Pattern 13: Matrix Initiative (e.g., "+2D6 Matrix Initiative")
        matrix_init_match = re.match(r'([+-])(\d+)D(\d+)\s+Matrix\s+Initiative', line, re.IGNORECASE)
        if matrix_init_match:
            sign = matrix_init_match.group(1)
            num_dice = int(matrix_init_match.group(2))
            value = num_dice if sign == '+' else -num_dice
            return [{
                'modifier_type': 'initiative',
                'target_name': 'matrix_initiative_dice',
                'modifier_value': value,
                'description': original_line
            }]
        
        # Pattern 14: Boosts Matrix performance (generic)
        if 'boosts matrix performance' in line.lower() or 'matrix performance' in line.lower():
            return [{
                'modifier_type': 'pool',
                'target_name': 'matrix_performance',
                'modifier_value': 1,
                'description': original_line
            }]
        
        # Pattern 15: Social dice (e.g., "+4 social dice")
        social_match = re.match(r'([+-]\d+)\s+social\s+dice?', line, re.IGNORECASE)
        if social_match:
            return [{
                'modifier_type': 'pool',
                'target_name': 'social_pool',
                'modifier_value': int(social_match.group(1)),
                'description': original_line
            }]
        
        # Pattern 16: Fractional effects (e.g., "1/2 effect on non-dwarves")
        fraction_match = re.match(r'(\d+)/(\d+)\s+effect\s+on\s+(.+)', line, re.IGNORECASE)
        if fraction_match:
            numerator = int(fraction_match.group(1))
            denominator = int(fraction_match.group(2))
            condition = fraction_match.group(3).strip()
            return [{
                'modifier_type': 'conditional',
                'target_name': 'effect_modifier',
                'modifier_value': numerator / denominator,
                'condition': condition,
                'description': original_line
            }]
        
        # Pattern 17: Grade/Level descriptors (not actual modifiers, skip)
        if re.match(r'Level\s+\d+|Grade', line, re.IGNORECASE):
            return None
        
        # Pattern 18: Vision Magnification (e.g., "Vision Magnification 3")
        vis_mag_match = re.match(r'Vision\s+Magnification\s+(\d+)', line, re.IGNORECASE)
        if vis_mag_match:
            return [{
                'modifier_type': 'vision',
                'target_name': 'magnification',
                'modifier_value': int(vis_mag_match.group(1)),
                'description': original_line
            }]
        
        # Pattern 19: Enhanced with software (extract TN from parentheses)
        enhanced_match = re.search(r'Enhanced\s+with.*\(([^)]+)\)', original_line, re.IGNORECASE)
        if enhanced_match:
            paren_content = enhanced_match.group(1)
            # Try to parse what's in parentheses
            tn_match = re.search(r'([+-]\d+)\s+TN', paren_content, re.IGNORECASE)
            if tn_match:
                return [{
                    'modifier_type': 'combat',
                    'target_name': 'ranged_tn',
                    'modifier_value': int(tn_match.group(1)),
                    'description': original_line
                }]
        
        # Fallback: If we couldn't parse anything, still store the description
        return [{
            'modifier_type': 'special',
            'target_name': 'description_only',
            'modifier_value': 0,
            'description': original_line
        }]
    
    def parse_cyberware_bioware(self, content: str) -> Tuple[List[Dict], List[Dict]]:
        """
        Parse cyberware and bioware items with costs and parsed modifiers
        Returns: (cyberware_list, bioware_list)
        """
        cyberware = []
        bioware = []
        
        section_match = re.search(r'##\s+Cyberware/Bioware(?:\s*\([^)]*\))?\s*\n(.*)(?=\n##|\Z)', content, re.DOTALL | re.IGNORECASE)
        if not section_match:
            return (cyberware, bioware)
        
        section = section_match.group(1).strip()
        
        # Parse Cyberware
        cyber_match = re.search(r'###\s+Cyberware(.*?)(?=###|\Z)', section, re.DOTALL | re.IGNORECASE)
        if cyber_match:
            cyber_section = cyber_match.group(1)
            items = re.split(r'\n-\s+\*\*', cyber_section)
            for item in items[1:]:
                lines = item.split('\n')
                if not lines:
                    continue
                
                first_line = lines[0]
                # Match: Name (optional grade/type in parens) ** (essence cost)
                # Example: "Datajack Prototype (Delta-Grade)** (0.1 Essence)"
                name_match = re.match(r'(.+?)\*\*\s*\(([\d.]+)\s+Essence\)', first_line)
                if name_match:
                    # Extract full name including any parenthetical grade/type info
                    name = name_match.group(1).strip()
                    essence = float(name_match.group(2))
                    
                    # Parse ALL modifier lines (lines starting with "  - ")
                    parsed_modifiers = []
                    for line in lines[1:]:
                        # Match pattern: "  - modifier text"
                        if re.match(r'^\s+-\s+', line):
                            modifier_text = re.sub(r'^\s+-\s+', '', line).strip()
                            if modifier_text:
                                mods = self.parse_modifier_line(modifier_text)
                                parsed_modifiers.extend(mods)
                    
                    cyberware.append({
                        'name': name,
                        'essence_cost': essence,
                        'modifiers': parsed_modifiers
                    })
        
        # Parse Bioware
        bio_match = re.search(r'###\s+Bioware(.*?)(?=\n###|\n---|\Z)', section, re.DOTALL | re.IGNORECASE)
        if bio_match:
            bio_section = bio_match.group(1)
            items = re.split(r'\n-\s+\*\*', bio_section)
            for item in items[1:]:
                lines = item.split('\n')
                if not lines:
                    continue
                
                first_line = lines[0]
                name_match = re.match(r'(.+?)\*\*\s*\(([\d.]+)\s+Body Index\)', first_line)
                if name_match:
                    name = name_match.group(1).strip()
                    cost = float(name_match.group(2))
                    
                    # Parse ALL modifier lines
                    parsed_modifiers = []
                    for line in lines[1:]:
                        if re.match(r'^\s+-\s+', line):
                            modifier_text = re.sub(r'^\s+-\s+', '', line).strip()
                            if modifier_text:
                                mods = self.parse_modifier_line(modifier_text)
                                parsed_modifiers.extend(mods)
                    
                    bioware.append({
                        'name': name,
                        'body_index_cost': cost,
                        'modifiers': parsed_modifiers
                    })
        
        return (cyberware, bioware)
    
    def extract_weapon_modifications(self, gear_text: str) -> Dict:
        """Extract weapon modifications from gear text"""
        mods = {}
        text = gear_text.lower()
        
        # Smartlink
        if 'smartlink' in text or 'smartgun' in text:
            rating = 1
            match = re.search(r'smartlink (\d+)', text)
            if match:
                rating = int(match.group(1))
            
            # Check for Project Aegis enhancement
            if 'project aegis' in text or 'aegis' in text:
                rating += 1
            
            mods['smartlink'] = {
                'rating': rating,
                'tn_modifier': -(rating + 1)  # Base -2, +1 per rating above 1
            }
        
        # Optical Magnification
        if 'optical magnification' in text:
            match = re.search(r'optical magnification (\d+)', text)
            if match:
                mods['optical_magnification'] = {
                    'rating': int(match.group(1)),
                    'range_reduction': int(match.group(1))
                }
        
        # Sound Suppressor
        if 'sound suppressor' in text:
            mods['sound_suppressor'] = {'conceal_bonus': 2}
        
        # Gas Vent
        if 'gas vent' in text:
            match = re.search(r'gas vent (\d+)', text)
            if match:
                mods['gas_vent'] = {'recoil_comp': int(match.group(1))}
        
        # Customization (weapon-specific skill bonus)
        if 'customized' in text or 'personalized' in text:
            mods['customization'] = {'skill_bonus': 1}
        
        return mods
    
    def parse_character_file(self, filepath: str) -> Dict:
        """Parse a character markdown file with new format"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        char_data = {
            'name': '',
            'street_name': '',
            'archetype': '',
            'metatype': 'Human',
            'attributes': {},
            'attribute_modifiers': [],
            'skills': {},
            'skill_modifiers': [],
            'power_points': {'total': 0, 'used': 0, 'available': 0},
            'gear': [],
            'contacts': [],
            'nuyen': 0,
            'karma_pool': 0,
            'karma_total': 0,
            'karma_available': 0,
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
        
        # Extract attributes with new format
        # Handle both "### Base Form" and "### Base Form (Human Form for Shapeshifters)"
        attr_section = re.search(r'## Attributes\s*\n### Base Form[^\n]*\n(.*?)(?:\n###|\n##)', content, re.DOTALL)
        if attr_section:
            for line in attr_section.group(1).split('\n'):
                match = re.match(r'-\s*\*\*(\w+)\*\*:\s*(.+)', line)
                if match:
                    attr_name = match.group(1).lower()
                    stat_text = match.group(2).strip()
                    
                    base, modified, explanation = self.parse_stat_with_modifiers(stat_text)
                    
                    char_data['attributes'][attr_name] = {
                        'base': base,
                        'current': modified if modified is not None else base,
                        'explanation': explanation  # Store for display, don't create modifiers
                    }
        
        # Extract skills with new format
        skills_section = re.search(r'## Skills\s*\n(.*?)(?:\n##)', content, re.DOTALL)
        if skills_section:
            current_skill_type = 'active'
            
            for line in skills_section.group(1).split('\n'):
                # Check for skill type headers
                if '### Active Skills' in line:
                    current_skill_type = 'active'
                    continue
                elif '### Knowledge Skills' in line:
                    current_skill_type = 'knowledge'
                    continue
                elif '### Language Skills' in line:
                    current_skill_type = 'language'
                    continue
                
                # Parse skill line
                match = re.match(r'-\s*\*\*([^*]+)\*\*:\s*(.+)', line)
                if match:
                    skill_name = match.group(1).strip()
                    stat_text = match.group(2).strip()
                    
                    base, modified, explanation = self.parse_stat_with_modifiers(stat_text)
                    
                    char_data['skills'][skill_name] = {
                        'base_rating': base,
                        'current_rating': modified if modified is not None else base,
                        'skill_type': current_skill_type,
                        'specialization': None,
                        'explanation': explanation  # Store for display, don't create modifiers
                    }
                    #     # Check for TN modifiers (like smartlink)
                    #     tn_match = re.search(r'([+-]\d+)\s+TN\s+(?:with\s+)?(.+)', exp, re.IGNORECASE)
                    #     if tn_match:
                    #         value = int(tn_match.group(1))
                    #         source = tn_match.group(2).strip()
                    #         
                    #         char_data['skill_modifiers'].append({
                    #             'type': 'combat',
                    #             'target': 'ranged_tn',
                    #             'value': value,
                    #             'source': source,
                    #             'source_type': 'cyberware' if 'smartlink' in source.lower() or 'smartgun' in source.lower() else 'equipment',
                    #             'skill_name': skill_name
                    #         })
                    #     else:
                    #         # Regular skill bonus
                    #         bonus_match = re.search(r'([+-]\d+)\s+(?:dice?\s+)?(?:with\s+)?(.+)', exp, re.IGNORECASE)
                    #         if bonus_match:
                    #             value = int(bonus_match.group(1))
                    #             source = bonus_match.group(2).strip()
                    #             
                    #             source_type = 'unknown'
                    #             if any(bio in source.lower() for bio in ['enhanced articulation', 'reflex recorder', 'mnemonic']):
                    #                 source_type = 'bioware'
                    #             elif 'software' in source.lower() or 'aegis' in source.lower():
                    #                 source_type = 'software'
                    #             
                    #             char_data['skill_modifiers'].append({
                    #                 'type': 'skill',
                    #                 'target': skill_name.lower(),
                    #                 'value': value,
                    #                 'source': source,
                    #                 'source_type': source_type
                    #             })
        
        # Extract power points (for adepts)
        power_points_match = re.search(r'\*\*Power Points\*\*:\s*(.+)', content)
        if power_points_match:
            pp_text = power_points_match.group(1).strip()
            if pp_text != 'N/A':
                # Parse format like "6" or "6 (4 used, 2 available)"
                base_match = re.match(r'(\d+(?:\.\d+)?)', pp_text)
                if base_match:
                    total = float(base_match.group(1))
                    char_data['power_points']['total'] = total
                    
                    # Try to extract used/available
                    used_match = re.search(r'(\d+(?:\.\d+)?)\s+used', pp_text)
                    if used_match:
                        char_data['power_points']['used'] = float(used_match.group(1))
                    
                    avail_match = re.search(r'(\d+(?:\.\d+)?)\s+available', pp_text)
                    if avail_match:
                        char_data['power_points']['available'] = float(avail_match.group(1))
                    else:
                        # Calculate available
                        char_data['power_points']['available'] = total - char_data['power_points']['used']
        
        # Extract numeric values
        nuyen_match = re.search(r'\*\*Nuyen\*\*:\s*([\d,]+)', content)
        if nuyen_match:
            char_data['nuyen'] = int(nuyen_match.group(1).replace(',', '').replace('¥', ''))
        
        karma_pool_match = re.search(r'\*\*Karma Pool\*\*:\s*(\d+)', content)
        if karma_pool_match:
            char_data['karma_pool'] = int(karma_pool_match.group(1))
        
        karma_total_match = re.search(r'\*\*Total Karma (?:Earned|Total)\*\*:\s*(\d+)', content)
        if karma_total_match:
            char_data['karma_total'] = int(karma_total_match.group(1))
        
        karma_avail_match = re.search(r'\*\*Total Karma Available\*\*:\s*(\d+)', content)
        if karma_avail_match:
            char_data['karma_available'] = int(karma_avail_match.group(1))
        
        essence_match = re.search(r'\*\*Essence\*\*:\s*([\d.]+)', content)
        if essence_match:
            char_data['essence'] = float(essence_match.group(1))
        
        initiative_match = re.search(r'\*\*Initiative\*\*:\s*(.+)', content)
        if initiative_match:
            char_data['initiative'] = initiative_match.group(1).strip()
        
        # Extract cyberware/bioware items with costs using new parser
        char_data['cyberware'], char_data['bioware'] = self.parse_cyberware_bioware(content)
        
        # Extract gear - parse Weapons, Armor, Equipment, and Vehicles sections
        # Use negative lookahead to match ## followed by space (not ###)
        gear_section = re.search(r'## Gear\s*\n(.*?)(?:\n## (?!#)|$)', content, re.DOTALL)
        if gear_section:
            current_category = None
            current_item = None
            
            for line in gear_section.group(1).split('\n'):
                line_stripped = line.strip()
                
                if line_stripped.startswith('### '):
                    # Category header like "### Weapons", "### Armor", "### Equipment", "### Vehicles"
                    current_category = line_stripped[4:].strip()
                    current_item = None
                
                elif line_stripped.startswith('- **'):
                    # Item name line like "- **Morrissey Alta**" or "- **Secure Jacket**"
                    # Extract item name (remove ** markers)
                    item_match = re.match(r'-\s+\*\*([^*]+)\*\*', line_stripped)
                    if item_match:
                        item_name = item_match.group(1).strip()
                        
                        # Skip N/A and None entries
                        if item_name.upper() in ('N/A', 'NONE'):
                            current_item = None
                            continue
                        
                        current_item = {
                            'category': current_category,
                            'name': item_name,
                            'details': []
                        }
                        char_data['gear'].append(current_item)
                
                elif line_stripped.startswith('- ') and current_item:
                    # Detail line - add to current item's details
                    detail = line_stripped[2:].strip()
                    current_item['details'].append(detail)
        
        # Extract contacts
        contacts_section = re.search(r'## Contacts\s*\n(.*?)(?:\n##|$)', content, re.DOTALL)
        if contacts_section:
            for line in contacts_section.group(1).split('\n'):
                # Format: - **Name** - Role
                match = re.match(r'-\s*\*\*([^*]+)\*\*\s*-\s*(.+)', line)
                if match:
                    contact_name = match.group(1).strip()
                    contact_info = match.group(2).strip()
                    
                    # Try to extract level
                    level_match = re.search(r'Level:\s*(\d+)', contact_info)
                    level = int(level_match.group(1)) if level_match else 1
                    
                    char_data['contacts'].append({
                        'name': contact_name,
                        'info': contact_info,
                        'level': level
                    })
        
        # Extract bound spirits
        char_data['spirits'] = []
        spirits_section = re.search(r'### Bound Spirits\s*\n(.*?)(?:\n###|\n---|\n##|$)', content, re.DOTALL)
        if spirits_section:
            current_spirit = None
            for line in spirits_section.group(1).split('\n'):
                line_stripped = line.strip()
                
                # Spirit entry: - **Spirit Name** (Force X)
                spirit_match = re.match(r'-\s*\*\*([^*]+)\*\*\s*\(Force\s+(\d+)\)', line_stripped, re.IGNORECASE)
                if spirit_match:
                    if current_spirit:
                        char_data['spirits'].append(current_spirit)
                    
                    spirit_name = spirit_match.group(1).strip()
                    force = int(spirit_match.group(2))
                    
                    # Determine spirit type from name
                    spirit_type = 'unknown'
                    name_lower = spirit_name.lower()
                    if 'fire' in name_lower or 'flame' in name_lower:
                        spirit_type = 'fire_elemental'
                    elif 'earth' in name_lower:
                        spirit_type = 'earth_elemental'
                    elif 'water' in name_lower:
                        spirit_type = 'water_elemental'
                    elif 'air' in name_lower or 'wind' in name_lower or 'storm' in name_lower:
                        spirit_type = 'air_elemental'
                    elif 'loa' in name_lower or 'baron' in name_lower:
                        spirit_type = 'loa'
                    elif 'spirit of man' in name_lower or 'man' in name_lower:
                        spirit_type = 'spirit_of_man'
                    elif 'nature' in name_lower:
                        spirit_type = 'nature_spirit'
                    
                    current_spirit = {
                        'name': spirit_name,
                        'type': spirit_type,
                        'force': force,
                        'services': 0,
                        'special_abilities': [],
                        'notes': ''
                    }
                
                # Detail lines for current spirit
                elif current_spirit and line_stripped.startswith('- '):
                    detail = line_stripped[2:].strip()
                    
                    # Services line
                    services_match = re.match(r'Services:\s*(.+)', detail, re.IGNORECASE)
                    if services_match:
                        services_text = services_match.group(1).strip()
                        if 'permanent' in services_text.lower():
                            current_spirit['services'] = -1  # -1 indicates permanent
                        else:
                            # Try to extract number
                            num_match = re.search(r'(\d+)', services_text)
                            if num_match:
                                current_spirit['services'] = int(num_match.group(1))
                    
                    # Special Abilities line
                    abilities_match = re.match(r'Special Abilities:\s*(.+)', detail, re.IGNORECASE)
                    if abilities_match:
                        abilities_text = abilities_match.group(1).strip()
                        if abilities_text.upper() != 'N/A':
                            # Split on commas
                            abilities = [a.strip() for a in abilities_text.split(',')]
                            current_spirit['special_abilities'] = abilities
                    
                    # Notes line
                    notes_match = re.match(r'Notes:\s*(.+)', detail, re.IGNORECASE)
                    if notes_match:
                        current_spirit['notes'] = notes_match.group(1).strip()
            
            # Add last spirit
            if current_spirit:
                char_data['spirits'].append(current_spirit)
        
        return char_data
    
    def import_character(self, filepath: str):
        """Import a single character"""
        print(f"\nImporting {os.path.basename(filepath)}...")
        
        # Parse file
        char_data = self.parse_character_file(filepath)
        
        if not char_data['name']:
            print(f"  ✗ Could not parse character name")
            return
        
        # Get attribute values
        attrs = char_data['attributes']
        
        # Ensure all attributes exist with defaults
        for attr in ['body', 'quickness', 'strength', 'charisma', 'intelligence', 'willpower', 'reaction', 'magic', 'essence']:
            if attr not in attrs:
                attrs[attr] = {'base': 0, 'current': 0}
        
        # Insert character
        self.cursor.execute("""
            INSERT INTO characters (
                name, street_name, archetype, metatype,
                base_body, base_quickness, base_strength,
                base_charisma, base_intelligence, base_willpower,
                base_essence, base_magic, base_reaction,
                current_body, current_quickness, current_strength,
                current_charisma, current_intelligence, current_willpower,
                current_essence, current_magic, current_reaction,
                nuyen, karma_pool, karma_total, karma_available, initiative,
                power_points_total, power_points_used, power_points_available
            ) VALUES (
                %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s
            ) RETURNING id
        """, (
            char_data['name'], char_data['street_name'], char_data['archetype'], char_data['metatype'],
            attrs['body']['base'], attrs['quickness']['base'], attrs['strength']['base'],
            attrs['charisma']['base'], attrs['intelligence']['base'], attrs['willpower']['base'],
            attrs['essence']['base'], attrs['magic']['base'], attrs['reaction']['base'],
            attrs['body']['current'], attrs['quickness']['current'], attrs['strength']['current'],
            attrs['charisma']['current'], attrs['intelligence']['current'], attrs['willpower']['current'],
            attrs['essence']['current'], attrs['magic']['current'], attrs['reaction']['current'],
            char_data['nuyen'], char_data['karma_pool'], char_data['karma_total'], 
            char_data['karma_available'], char_data['initiative'],
            char_data['power_points']['total'], char_data['power_points']['used'], 
            char_data['power_points']['available']
        ))
        
        char_id = self.cursor.fetchone()['id']
        print(f"  ✓ Created character: {char_data['name']} (ID: {char_id})")
        
        # Insert attribute modifiers
        for mod in char_data['attribute_modifiers']:
            self.cursor.execute("""
                INSERT INTO character_modifiers (
                    character_id, modifier_type, target_name, modifier_value, 
                    source, source_type, is_permanent
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (char_id, mod['type'], mod['target'], mod['value'], 
                  mod['source'], mod['source_type'], True))
        
        print(f"  ✓ Added {len(char_data['attribute_modifiers'])} attribute modifiers")
        
        # Insert skills
        for skill_name, skill_data in char_data['skills'].items():
            self.cursor.execute("""
                INSERT INTO character_skills (
                    character_id, skill_name, base_rating, current_rating, 
                    skill_type, specialization
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, (char_id, skill_name, skill_data['base_rating'], 
                  skill_data['current_rating'], skill_data['skill_type'], 
                  skill_data['specialization']))
        
        print(f"  ✓ Added {len(char_data['skills'])} skills")
        
        # Insert skill modifiers
        for mod in char_data['skill_modifiers']:
            # Determine if this is weapon-specific
            weapon_specific = None
            if mod['type'] == 'combat' and 'skill_name' in mod:
                # TN modifiers might be weapon-specific
                weapon_specific = None  # For now, apply to all weapons
            
            self.cursor.execute("""
                INSERT INTO character_modifiers (
                    character_id, modifier_type, target_name, modifier_value,
                    source, source_type, is_permanent, weapon_specific
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (char_id, mod['type'], mod['target'], mod['value'],
                  mod['source'], mod['source_type'], True, weapon_specific))
        
        print(f"  ✓ Added {len(char_data['skill_modifiers'])} skill modifiers")
        
        # Insert cyberware items with parent-child relationships
        for cyber in char_data.get('cyberware', []):
            # Insert parent augmentation entry
            self.cursor.execute("""
                INSERT INTO character_modifiers (
                    character_id, modifier_type, target_name, modifier_value,
                    source, source_type, is_permanent, essence_cost
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (char_id, 'augmentation', 'cyberware', 0,
                  cyber['name'], 'cyberware', True, cyber['essence_cost']))
            
            parent_id = self.cursor.fetchone()['id']
            
            # Insert child modifier entries
            for mod in cyber.get('modifiers', []):
                condition = mod.get('condition', None)
                description = mod.get('description', None)
                
                # Build modifier_data JSONB with description
                modifier_data = {}
                if description:
                    modifier_data['description'] = description
                
                self.cursor.execute("""
                    INSERT INTO character_modifiers (
                        character_id, modifier_type, target_name, modifier_value,
                        source, source_type, is_permanent, parent_modifier_id, condition,
                        modifier_data
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (char_id, mod['modifier_type'], mod['target_name'], mod['modifier_value'],
                      cyber['name'], 'cyberware', True, parent_id, condition,
                      psycopg.types.json.Jsonb(modifier_data) if modifier_data else None))
        
        print(f"  ✓ Added {len(char_data.get('cyberware', []))} cyberware items with modifiers")
        
        # Insert bioware items with parent-child relationships
        for bio in char_data.get('bioware', []):
            # Insert parent augmentation entry with body_index_cost in dedicated column
            self.cursor.execute("""
                INSERT INTO character_modifiers (
                    character_id, modifier_type, target_name, modifier_value,
                    source, source_type, is_permanent, body_index_cost
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (char_id, 'augmentation', 'bioware', 0,
                  bio['name'], 'bioware', True, bio['body_index_cost']))
            
            parent_id = self.cursor.fetchone()['id']
            
            # Insert child modifier entries
            for mod in bio.get('modifiers', []):
                condition = mod.get('condition', None)
                description = mod.get('description', None)
                
                # Build modifier_data JSONB with description
                modifier_data = {}
                if description:
                    modifier_data['description'] = description
                
                self.cursor.execute("""
                    INSERT INTO character_modifiers (
                        character_id, modifier_type, target_name, modifier_value,
                        source, source_type, is_permanent, parent_modifier_id, condition,
                        modifier_data
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (char_id, mod['modifier_type'], mod['target_name'], mod['modifier_value'],
                      bio['name'], 'bioware', True, parent_id, condition,
                      psycopg.types.json.Jsonb(modifier_data) if modifier_data else None))
        
        print(f"  ✓ Added {len(char_data.get('bioware', []))} bioware items with modifiers")
        
        # Separate vehicles from other gear
        vehicles = [item for item in char_data['gear'] if item['category'] == 'Vehicles']
        other_gear = [item for item in char_data['gear'] if item['category'] != 'Vehicles']
        
        # Insert gear (weapons, armor, equipment)
        for item in other_gear:
            gear_type = 'equipment'
            if item['category'] == 'Weapons':
                gear_type = 'weapon'
            elif item['category'] == 'Armor':
                gear_type = 'armor'
            elif item['category'] == 'Equipment':
                gear_type = 'equipment'
            
            gear_name = item['name']
            
            # Build full text from details
            full_text = f"**{gear_name}**"
            if item['details']:
                full_text += "\n" + "\n".join(f"  - {detail}" for detail in item['details'])
            
            # Extract modifications (for weapons)
            mods = {}
            if gear_type == 'weapon':
                mods = self.extract_weapon_modifications(full_text)
            
            self.cursor.execute("""
                INSERT INTO character_gear (
                    character_id, gear_name, gear_type, modifications, notes
                ) VALUES (%s, %s, %s, %s, %s)
            """, (char_id, gear_name, gear_type, 
                  psycopg.types.json.Jsonb(mods) if mods else None,
                  full_text))
            
            # If weapon has customization, add weapon-specific skill modifier
            if 'customization' in mods:
                # Determine which skill this weapon uses
                weapon_skill = 'firearms'  # Default
                if 'whip' in gear_name.lower():
                    weapon_skill = 'whips'
                
                self.cursor.execute("""
                    INSERT INTO character_modifiers (
                        character_id, modifier_type, target_name, modifier_value,
                        source, source_type, is_permanent, weapon_specific
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (char_id, 'skill', weapon_skill, 1,
                      f'Customized {gear_name}', 'equipment', True, gear_name))
        
        print(f"  ✓ Added {len(other_gear)} gear items")
        
        # Insert vehicles into character_vehicles table
        for vehicle in vehicles:
            vehicle_name = vehicle['name']
            
            # Build notes from details
            notes = "\n".join(vehicle['details']) if vehicle['details'] else None
            
            # Try to determine vehicle type from name
            vehicle_type = 'ground'
            name_lower = vehicle_name.lower()
            if 'helicopter' in name_lower or 'drone' in name_lower or 'aircraft' in name_lower:
                vehicle_type = 'air'
            elif 'boat' in name_lower or 'ship' in name_lower:
                vehicle_type = 'water'
            
            self.cursor.execute("""
                INSERT INTO character_vehicles (
                    character_id, vehicle_name, vehicle_type, notes
                ) VALUES (%s, %s, %s, %s)
            """, (char_id, vehicle_name, vehicle_type, notes))
        
        if vehicles:
            print(f"  ✓ Added {len(vehicles)} vehicles")
        
        # Insert contacts
        for contact in char_data['contacts']:
            # Default loyalty and connection to the level value
            loyalty = contact.get('level', 1)
            connection = contact.get('level', 1)
            
            self.cursor.execute("""
                INSERT INTO character_contacts (
                    character_id, name, archetype, loyalty, connection, notes
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, (char_id, contact['name'], contact['info'], loyalty, connection, contact['info']))
        
        print(f"  ✓ Added {len(char_data['contacts'])} contacts")
        
        # Insert bound spirits
        for spirit in char_data.get('spirits', []):
            self.cursor.execute("""
                INSERT INTO character_spirits (
                    character_id, spirit_name, spirit_type, force, services,
                    special_abilities, notes
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (char_id, spirit['name'], spirit['type'], spirit['force'], 
                  spirit['services'], spirit['special_abilities'], spirit['notes']))
        
        if char_data.get('spirits'):
            print(f"  ✓ Added {len(char_data['spirits'])} bound spirits")
        
        self.conn.commit()
        print(f"  ✓ Import complete!")
    
    def clear_all_characters(self):
        """Delete all existing character data"""
        print("Clearing existing character data...")
        
        # Delete in correct order due to foreign key constraints
        tables = [
            'character_modifiers',
            'character_skills', 
            'character_gear',
            'character_vehicles',
            'character_contacts',
            'character_spirits',
            'characters'
        ]
        
        for table in tables:
            self.cursor.execute(f"DELETE FROM {table}")
            count = self.cursor.rowcount
            print(f"  ✓ Deleted {count} rows from {table}")
        
        self.conn.commit()
        print()

    def import_all(self):
        """Import all character files"""
        # Clear existing data first
        self.clear_all_characters()
        
        char_dir = 'characters'
        files = [f for f in os.listdir(char_dir) if f.endswith('.md') and f != 'README.md']

        print(f"Found {len(files)} character files")
        print("=" * 70)
        
        for filename in files:
            filepath = os.path.join(char_dir, filename)
            try:
                self.import_character(filepath)
            except Exception as e:
                print(f"  ✗ Error importing {filename}: {e}")
                import traceback
                traceback.print_exc()
                self.conn.rollback()
        
        print()
        print("=" * 70)
        print("Import complete!")
    
    def close(self):
        """Close database connection"""
        self.cursor.close()
        self.conn.close()


if __name__ == "__main__":
    importer = CharacterImporterV8()
    try:
        importer.import_all()
    finally:
        importer.close()
