#!/usr/bin/env python3
"""
Import character sheets v11 - USES COMPREHENSIVE CRUD API
- All v10 features (spell force parsing, proper number parsing, etc.)
- NEW: Uses comprehensive_crud.py instead of direct SQL
- NEW: Auto-populates edge/flaw costs from RAG
- NEW: Proper schema alignment (base_rating/current_rating, source, is_permanent, etc.)
"""
import os
import re
import sys
from dotenv import load_dotenv
from typing import Dict, List, Tuple, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.comprehensive_crud import ComprehensiveCRUD, get_system_user_id
import psycopg

load_dotenv()

# Import the parser class directly
import importlib.util
spec = importlib.util.spec_from_file_location("import_v10", os.path.join(os.path.dirname(__file__), "import-characters-v10.py"))
import_v10 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(import_v10)
CharacterImporterV9 = import_v10.CharacterImporterV9

class CharacterImporterV11:
    """Import characters using comprehensive CRUD API"""
    
    def __init__(self):
        # Get system user ID for audit logging
        conn = psycopg.connect(
            host=os.getenv('POSTGRES_HOST'),
            port=os.getenv('POSTGRES_PORT'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            dbname=os.getenv('POSTGRES_DB')
        )
        self.system_user_id = get_system_user_id(conn)
        conn.close()
        
        # Create CRUD API instance
        self.crud = ComprehensiveCRUD(user_id=self.system_user_id, user_type='SYSTEM')
        
        # Create parser instance (reuse v10 parsing logic)
        self.parser = CharacterImporterV9()
    
    def import_character(self, filepath: str):
        """Import a single character using CRUD API"""
        print(f"\nImporting {os.path.basename(filepath)}...")
        
        # Parse file using v10 parser
        char_data = self.parser.parse_character_file(filepath)
        
        if not char_data['name']:
            print(f"  ✗ Could not parse character name")
            return
        
        # Get attribute values
        attrs = char_data['attributes']
        
        # Ensure all attributes exist with defaults
        for attr in ['body', 'quickness', 'strength', 'charisma', 'intelligence', 'willpower', 'reaction', 'magic', 'essence']:
            if attr not in attrs:
                attrs[attr] = {'base': 0, 'current': 0}
        
        # Calculate body index
        body_index_max = (attrs['body']['base'] + attrs['willpower']['base']) / 2.0
        body_index_current = sum(bio.get('body_index_cost', 0) for bio in char_data.get('bioware', []))
        
        # Insert character (direct SQL since CRUD doesn't have create_character yet)
        cursor = self.crud.conn.cursor()
        cursor.execute("""
            INSERT INTO characters (
                name, street_name, archetype, metatype,
                base_body, base_quickness, base_strength,
                base_charisma, base_intelligence, base_willpower,
                base_essence, base_magic, base_reaction,
                current_body, current_quickness, current_strength,
                current_charisma, current_intelligence, current_willpower,
                current_essence, current_magic, current_reaction,
                nuyen, karma_pool, karma_total, karma_available, initiative,
                power_points_total, power_points_used, power_points_available,
                magic_pool, spell_pool, initiate_level, metamagics, magical_group, tradition, totem,
                body_index_max, body_index_current
            ) VALUES (
                %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s,
                %s, %s
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
            char_data['power_points']['available'],
            char_data.get('magic_pool', 0), char_data.get('spell_pool', 0), 
            char_data.get('initiate_level', 0), char_data.get('metamagics', []),
            char_data.get('magical_group'), char_data.get('tradition'), char_data.get('totem'),
            body_index_max, body_index_current
        ))
        
        char_id = cursor.fetchone()[0]
        self.crud.conn.commit()
        cursor.close()
        
        totem_info = f" (Totem: {char_data.get('totem')})" if char_data.get('totem') else ""
        print(f"  ✓ Created character: {char_data['name']} (ID: {char_id}){totem_info}")
        
        # Insert skills using CRUD API
        for skill_name, skill_data in char_data['skills'].items():
            self.crud.add_skill(char_id, {
                'skill_name': skill_name,
                'base_rating': skill_data['base_rating'],
                'current_rating': skill_data['current_rating'],
                'skill_type': skill_data['skill_type'],
                'specialization': skill_data.get('specialization')
            }, reason='Character import')
        
        print(f"  ✓ Added {len(char_data['skills'])} skills")
        
        # Insert cyberware modifiers using CRUD API
        for cyber in char_data.get('cyberware', []):
            # Add parent modifier - store essence_cost in BOTH column AND modifier_data
            parent = self.crud.add_modifier(char_id, {
                'modifier_type': 'augmentation',
                'target_name': 'cyberware',
                'modifier_value': 0,
                'source': cyber['name'],
                'source_type': 'cyberware',
                'is_permanent': True,
                'essence_cost': cyber['essence_cost'],  # Store in column
                'modifier_data': {'essence_cost': cyber['essence_cost']}  # ALSO in JSONB for consistency
            }, reason='Character import')
            
            # Add child modifiers
            for mod in cyber.get('modifiers', []):
                mod_data = {
                    'modifier_type': mod['modifier_type'],
                    'target_name': mod['target_name'],
                    'modifier_value': mod['modifier_value'],
                    'source': cyber['name'],
                    'source_type': 'cyberware',
                    'is_permanent': True,
                    'source_id': parent['id']
                }
                
                if mod.get('condition'):
                    mod_data['modifier_data'] = {'condition': mod['condition']}
                if mod.get('description'):
                    if 'modifier_data' not in mod_data:
                        mod_data['modifier_data'] = {}
                    mod_data['modifier_data']['description'] = mod['description']
                
                self.crud.add_modifier(char_id, mod_data, reason='Character import')
        
        print(f"  ✓ Added {len(char_data.get('cyberware', []))} cyberware items with modifiers")
        
        # Insert bioware modifiers using CRUD API  
        for bio in char_data.get('bioware', []):
            # Add parent modifier - store body_index_cost in modifier_data (no column for this)
            parent = self.crud.add_modifier(char_id, {
                'modifier_type': 'augmentation',
                'target_name': 'bioware',
                'modifier_value': 0,
                'source': bio['name'],
                'source_type': 'bioware',
                'is_permanent': True,
                'modifier_data': {'body_index_cost': bio['body_index_cost']}  # Store in JSONB
            }, reason='Character import')
            
            # Add child modifiers
            for mod in bio.get('modifiers', []):
                mod_data = {
                    'modifier_type': mod['modifier_type'],
                    'target_name': mod['target_name'],
                    'modifier_value': mod['modifier_value'],
                    'source': bio['name'],
                    'source_type': 'bioware',
                    'is_permanent': True,
                    'source_id': parent['id']
                }
                
                if mod.get('condition'):
                    mod_data['modifier_data'] = {'condition': mod['condition']}
                if mod.get('description'):
                    if 'modifier_data' not in mod_data:
                        mod_data['modifier_data'] = {}
                    mod_data['modifier_data']['description'] = mod['description']
                
                self.crud.add_modifier(char_id, mod_data, reason='Character import')
        
        print(f"  ✓ Added {len(char_data.get('bioware', []))} bioware items with modifiers")
        
        # Separate vehicles from other gear
        vehicles = [item for item in char_data['gear'] if item['category'] == 'Vehicles']
        other_gear = [item for item in char_data['gear'] if item['category'] != 'Vehicles']
        
        # Insert gear using CRUD API
        for item in other_gear:
            gear_type = 'equipment'
            if item['category'] == 'Weapons':
                gear_type = 'weapon'
            elif item['category'] == 'Armor':
                gear_type = 'armor'
            
            # Build notes from details
            notes = "\n".join(item['details']) if item['details'] else None
            
            # Extract modifications (for weapons)
            mods = {}
            if gear_type == 'weapon':
                full_text = f"**{item['name']}**\n" + (notes or '')
                mods = self.parser.extract_weapon_modifications(full_text)
            
            self.crud.add_gear(char_id, {
                'gear_name': item['name'],
                'gear_type': gear_type,
                'modifications': mods if mods else None,
                'notes': notes
            }, reason='Character import')
        
        print(f"  ✓ Added {len(other_gear)} gear items")
        
        # Insert vehicles using CRUD API
        for vehicle in vehicles:
            notes = "\n".join(vehicle['details']) if vehicle['details'] else None
            
            # Determine vehicle type
            vehicle_type = 'ground'
            name_lower = vehicle['name'].lower()
            if 'helicopter' in name_lower or 'drone' in name_lower or 'aircraft' in name_lower:
                vehicle_type = 'air'
            elif 'boat' in name_lower or 'ship' in name_lower:
                vehicle_type = 'water'
            
            self.crud.add_vehicle(char_id, {
                'vehicle_name': vehicle['name'],
                'vehicle_type': vehicle_type,
                'notes': notes
            }, reason='Character import')
        
        if vehicles:
            print(f"  ✓ Added {len(vehicles)} vehicles")
        
        # Insert contacts using CRUD API
        for contact in char_data['contacts']:
            loyalty = contact.get('level', 1)
            connection = contact.get('level', 1)
            
            self.crud.add_contact(char_id, {
                'name': contact['name'],
                'archetype': contact['info'],
                'loyalty': loyalty,
                'connection': connection,
                'notes': contact['info']
            }, reason='Character import')
        
        print(f"  ✓ Added {len(char_data['contacts'])} contacts")
        
        # Insert bound spirits using CRUD API
        for spirit in char_data.get('spirits', []):
            self.crud.add_spirit(char_id, {
                'spirit_name': spirit['name'],
                'spirit_type': spirit['type'],
                'force': spirit['force'],
                'services': spirit['services'],
                'special_abilities': spirit['special_abilities'],
                'notes': spirit['notes']
            }, reason='Character import')
        
        if char_data.get('spirits'):
            print(f"  ✓ Added {len(char_data['spirits'])} bound spirits")
        
        # Insert spells using CRUD API
        for spell in char_data.get('spells', []):
            self.crud.add_spell(char_id, {
                'spell_name': spell['spell_name'],
                'spell_category': spell['spell_category'],
                'spell_type': spell['spell_type'],
                'learned_force': spell.get('learned_force', 1)
            }, reason='Character import')
        
        if char_data.get('spells'):
            print(f"  ✓ Added {len(char_data['spells'])} spells (with force values)")
        
        print(f"  ✓ Import complete!")
    
    def clear_all_characters(self):
        """Delete all existing character data"""
        print("Clearing existing character data...")
        
        cursor = self.crud.conn.cursor()
        
        # Delete in correct order due to foreign key constraints
        tables = [
            'character_modifiers',
            'character_skills', 
            'character_gear',
            'character_vehicles',
            'character_contacts',
            'character_spirits',
            'character_spells',
            'character_foci',
            'character_active_effects',
            'characters'
        ]
        
        for table in tables:
            cursor.execute(f"DELETE FROM {table}")
            count = cursor.rowcount
            print(f"  ✓ Deleted {count} rows from {table}")
        
        self.crud.conn.commit()
        cursor.close()
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
                self.crud.conn.rollback()
        
        print()
        print("=" * 70)
        print("Import complete!")
    
    def close(self):
        """Close database connection"""
        self.crud.close()
        self.parser.close()


if __name__ == "__main__":
    importer = CharacterImporterV11()
    try:
        importer.import_all()
    finally:
        importer.close()
