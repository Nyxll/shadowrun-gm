#!/usr/bin/env python3
"""
Comprehensive test suite for ALL character fields
Tests every single line from every character markdown file
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row

load_dotenv()

class CharacterFieldTester:
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
        self.failures = []
        self.successes = []
        self.total_tests = 0
    
    def test(self, test_name, condition, expected=None, actual=None):
        """Record a test result"""
        self.total_tests += 1
        if condition:
            self.successes.append(test_name)
            print(f"  ✓ {test_name}")
            return True
        else:
            self.failures.append({
                'test': test_name,
                'expected': expected,
                'actual': actual
            })
            print(f"  ✗ {test_name}")
            if expected is not None and actual is not None:
                print(f"    Expected: {expected}")
                print(f"    Actual: {actual}")
            return False
    
    def get_character(self, name):
        """Get character by name"""
        self.cursor.execute(
            "SELECT * FROM characters WHERE name = %s",
            (name,)
        )
        return self.cursor.fetchone()
    
    def get_character_skills(self, char_id):
        """Get all skills for a character"""
        self.cursor.execute(
            "SELECT * FROM character_skills WHERE character_id = %s",
            (char_id,)
        )
        return self.cursor.fetchall()
    
    def get_character_modifiers(self, char_id, source_type=None):
        """Get all modifiers for a character"""
        if source_type:
            self.cursor.execute(
                "SELECT * FROM character_modifiers WHERE character_id = %s AND source_type = %s",
                (char_id, source_type)
            )
        else:
            self.cursor.execute(
                "SELECT * FROM character_modifiers WHERE character_id = %s",
                (char_id,)
            )
        return self.cursor.fetchall()
    
    def get_character_gear(self, char_id, gear_type=None):
        """Get all gear for a character"""
        if gear_type:
            self.cursor.execute(
                "SELECT * FROM character_gear WHERE character_id = %s AND gear_type = %s",
                (char_id, gear_type)
            )
        else:
            self.cursor.execute(
                "SELECT * FROM character_gear WHERE character_id = %s",
                (char_id,)
            )
        return self.cursor.fetchall()
    
    def get_character_contacts(self, char_id):
        """Get all contacts for a character"""
        self.cursor.execute(
            "SELECT * FROM character_contacts WHERE character_id = %s",
            (char_id,)
        )
        return self.cursor.fetchall()
    
    def get_character_vehicles(self, char_id):
        """Get all vehicles for a character"""
        self.cursor.execute(
            "SELECT * FROM character_vehicles WHERE character_id = %s",
            (char_id,)
        )
        return self.cursor.fetchall()
    
    def get_character_edges_flaws(self, char_id, edge_type=None):
        """Get all edges/flaws for a character"""
        if edge_type:
            self.cursor.execute(
                "SELECT * FROM character_edges_flaws WHERE character_id = %s AND type = %s",
                (char_id, edge_type)
            )
        else:
            self.cursor.execute(
                "SELECT * FROM character_edges_flaws WHERE character_id = %s",
                (char_id,)
            )
        return self.cursor.fetchall()
    
    def test_platinum(self):
        """Test ALL fields for Platinum character"""
        print("\n" + "=" * 70)
        print("TESTING: Platinum (Kent Jefferies)")
        print("=" * 70)
        
        char = self.get_character("Kent Jefferies")
        if not self.test("Platinum character exists", char is not None):
            return
        
        char_id = char['id']
        
        # Basic Information
        print("\n### Basic Information")
        self.test("Name", char['name'] == "Kent Jefferies", "Kent Jefferies", char.get('name'))
        self.test("Street Name", char['street_name'] == "Platinum", "Platinum", char.get('street_name'))
        self.test("Metatype", char['metatype'] == "Human", "Human", char.get('metatype'))
        self.test("Archetype", char['archetype'] == "Street Samurai", "Street Samurai", char.get('archetype'))
        self.test("Sex", char['sex'] == "Male", "Male", char.get('sex'))
        self.test("Height", char['height'] == "6 feet", "6 feet", char.get('height'))
        self.test("Weight", char['weight'] == "200 lbs", "200 lbs", char.get('weight'))
        self.test("Hair", char['hair'] == "Brown short-cropped hair", "Brown short-cropped hair", char.get('hair'))
        self.test("Eyes", char['eyes'] == "Hazel cybereyes", "Hazel cybereyes", char.get('eyes'))
        
        # Attributes
        print("\n### Attributes")
        self.test("Base Body", char['base_body'] == 10, 10, char.get('base_body'))
        self.test("Base Quickness", char['base_quickness'] == 15, 15, char.get('base_quickness'))
        self.test("Base Strength", char['base_strength'] == 14, 14, char.get('base_strength'))
        self.test("Base Charisma", char['base_charisma'] == 4, 4, char.get('base_charisma'))
        self.test("Base Intelligence", char['base_intelligence'] == 12, 12, char.get('base_intelligence'))
        self.test("Base Willpower", char['base_willpower'] == 9, 9, char.get('base_willpower'))
        self.test("Base Essence", char['base_essence'] == 2.55, 2.55, char.get('base_essence'))
        self.test("Base Reaction", char['base_reaction'] == 27, 27, char.get('base_reaction'))
        
        # Derived Stats
        print("\n### Derived Stats")
        self.test("Initiative", char['initiative'] == "27 +4D6", "27 +4D6", char.get('initiative'))
        self.test("Combat Pool", char['combat_pool'] == 17, 17, char.get('combat_pool'))
        self.test("Karma Pool", char['karma_pool'] == 45, 45, char.get('karma_pool'))
        self.test("Karma Total", char['karma_total'] == 445, 445, char.get('karma_total'))
        self.test("Karma Available", char['karma_available'] == 57, 57, char.get('karma_available'))
        self.test("Nuyen", char['nuyen'] == 498148, 498148, char.get('nuyen'))
        self.test("Lifestyle", char['lifestyle'] == "High", "High", char.get('lifestyle'))
        self.test("Lifestyle Cost", char['lifestyle_cost'] == 5000, 5000, char.get('lifestyle_cost'))
        self.test("Lifestyle Months", char['lifestyle_months_prepaid'] == 1, 1, char.get('lifestyle_months_prepaid'))
        self.test("Body Index Current", char['body_index_current'] == 8.35, 8.35, char.get('body_index_current'))
        self.test("Body Index Max", char['body_index_max'] == 9, 9, char.get('body_index_max'))
        
        # Skills - Test count and specific skills
        print("\n### Skills")
        skills = self.get_character_skills(char_id)
        skill_dict = {s['skill_name']: s for s in skills}
        
        self.test("Total skills count", len(skills) == 16, 16, len(skills))
        
        # Active Skills
        expected_active = {
            'Gunnery': 5, 'Athletics': 6, 'Stealth': 6, 'Firearms': 7,
            'Whips': 2, 'Monowhip': 6, 'Cars': 2, 'Negotiation': 3,
            'Computers': 7, 'Demolitions': 3
        }
        for skill_name, rating in expected_active.items():
            if skill_name in skill_dict:
                self.test(f"{skill_name} rating", skill_dict[skill_name]['base_rating'] == rating, rating, skill_dict[skill_name].get('base_rating'))
                self.test(f"{skill_name} type", skill_dict[skill_name]['skill_type'] == 'active', 'active', skill_dict[skill_name].get('skill_type'))
            else:
                self.test(f"{skill_name} exists", False, "exists", "missing")
        
        # Knowledge Skills
        expected_knowledge = {
            'Physical Sciences': 2, 'Magical Theory': 2, 'Military Theory': 2
        }
        for skill_name, rating in expected_knowledge.items():
            if skill_name in skill_dict:
                self.test(f"{skill_name} rating", skill_dict[skill_name]['base_rating'] == rating, rating, skill_dict[skill_name].get('base_rating'))
                self.test(f"{skill_name} type", skill_dict[skill_name]['skill_type'] == 'knowledge', 'knowledge', skill_dict[skill_name].get('skill_type'))
            else:
                self.test(f"{skill_name} exists", False, "exists", "missing")
        
        # Language Skills
        expected_language = {
            'English': 6, 'French': 2, 'Cooking': 1
        }
        for skill_name, rating in expected_language.items():
            if skill_name in skill_dict:
                self.test(f"{skill_name} rating", skill_dict[skill_name]['base_rating'] == rating, rating, skill_dict[skill_name].get('base_rating'))
                self.test(f"{skill_name} type", skill_dict[skill_name]['skill_type'] == 'language', 'language', skill_dict[skill_name].get('skill_type'))
            else:
                self.test(f"{skill_name} exists", False, "exists", "missing")
        
        # Cyberware
        print("\n### Cyberware")
        cyberware = self.get_character_modifiers(char_id, 'cyberware')
        cyber_dict = {c['source']: c for c in cyberware}
        
        self.test("Total cyberware count", len(cyberware) == 5, 5, len(cyberware))
        
        expected_cyber = {
            'Wired Reflexes 3 (Beta-Grade)': 2.4,
            'Reaction Enhancers 6 (Delta-Grade)': 1.2,
            'Cybereyes': 0.2,
            'Smartlink 2': 0.5,
            'Datajack (Delta-Grade)': 0.1
        }
        for cyber_name, essence in expected_cyber.items():
            if cyber_name in cyber_dict:
                self.test(f"{cyber_name} essence", cyber_dict[cyber_name]['essence_cost'] == essence, essence, cyber_dict[cyber_name].get('essence_cost'))
            else:
                self.test(f"{cyber_name} exists", False, "exists", "missing")
        
        # Bioware
        print("\n### Bioware")
        bioware = self.get_character_modifiers(char_id, 'bioware')
        bio_dict = {b['source']: b for b in bioware}
        
        self.test("Total bioware count", len(bioware) == 7, 7, len(bioware))
        
        expected_bioware = [
            'Enhanced Articulation',
            'Cerebral Booster 3',
            'Supra-Thyroid Gland',
            'Muscle Augmentation 4',
            'Damage Compensator 3',
            'Reflex Recorder (Firearms)',
            'Mnemonic Enhancer 4'
        ]
        for bio_name in expected_bioware:
            self.test(f"{bio_name} exists", bio_name in bio_dict, "exists", "missing" if bio_name not in bio_dict else "found")
        
        # Weapons
        print("\n### Weapons")
        weapons = self.get_character_gear(char_id, 'weapon')
        weapon_dict = {w['gear_name']: w for w in weapons}
        
        self.test("Total weapons count", len(weapons) == 8, 8, len(weapons))
        
        expected_weapons = [
            'Morrissey Alta',
            'Monowhip',
            'Ares Alpha with Grenade Launcher',
            'Armtech MGL-12 mini',
            'Prototype Panther Assault Cannon',
            'Panther Assault Cannon',
            'MP Laser 3',
            'Walther MA-2100 Sniper Rifle'
        ]
        for weapon_name in expected_weapons:
            self.test(f"{weapon_name} exists", weapon_name in weapon_dict, "exists", "missing" if weapon_name not in weapon_dict else "found")
        
        # Armor
        print("\n### Armor")
        armor = self.get_character_gear(char_id, 'armor')
        armor_dict = {a['gear_name']: a for a in armor}
        
        self.test("Total armor count", len(armor) == 7, 7, len(armor))
        
        expected_armor = [
            'Secure Jacket',
            'Form-Fitting Body Armor 4',
            'Forearm Guards',
            'Armored Jacket (London Fog)',
            'Hardened Military-Grade Armor',
            'Secure Helmet (Additional)',
            'Boomer Suit (Additional Gear)'
        ]
        for armor_name in expected_armor:
            self.test(f"{armor_name} exists", armor_name in armor_dict, "exists", "missing" if armor_name not in armor_dict else "found")
        
        # Contacts
        print("\n### Contacts")
        contacts = self.get_character_contacts(char_id)
        contact_dict = {c['name']: c for c in contacts}
        
        self.test("Total contacts count", len(contacts) == 9, 9, len(contacts))
        
        expected_contacts = [
            'Tanis Driscol', 'Volaren', 'Fuzzy Eddy', 'Manticore',
            'Puppetmaster', 'Mattias', 'Loretta', 'Leroy/Gord', 'Colonel Tanner'
        ]
        for contact_name in expected_contacts:
            self.test(f"{contact_name} exists", contact_name in contact_dict, "exists", "missing" if contact_name not in contact_dict else "found")
        
        # Vehicles
        print("\n### Vehicles")
        vehicles = self.get_character_vehicles(char_id)
        vehicle_dict = {v['vehicle_name']: v for v in vehicles}
        
        self.test("Total vehicles count", len(vehicles) == 2, 2, len(vehicles))
        
        expected_vehicles = [
            'GMC Bulldog Stepvan',
            'Eurocar Westwind'
        ]
        for vehicle_name in expected_vehicles:
            self.test(f"{vehicle_name} exists", vehicle_name in vehicle_dict, "exists", "missing" if vehicle_name not in vehicle_dict else "found")
        
        # Edges
        print("\n### Edges")
        edges = self.get_character_edges_flaws(char_id, 'edge')
        edge_dict = {e['name']: e for e in edges}
        
        self.test("Total edges count", len(edges) == 2, 2, len(edges))
        
        expected_edges = [
            'Ambidexterity',
            'Exceptional Attribute'
        ]
        for edge_name in expected_edges:
            self.test(f"{edge_name} exists", edge_name in edge_dict, "exists", "missing" if edge_name not in edge_dict else "found")
        
        # Flaws
        print("\n### Flaws")
        flaws = self.get_character_edges_flaws(char_id, 'flaw')
        flaw_dict = {f['name']: f for f in flaws}
        
        self.test("Total flaws count", len(flaws) == 3, 3, len(flaws))
        
        expected_flaws = [
            'Amnesia',
            'Distinctive Style',
            'Guilt Spur'
        ]
        for flaw_name in expected_flaws:
            self.test(f"{flaw_name} exists", flaw_name in flaw_dict, "exists", "missing" if flaw_name not in flaw_dict else "found")
    
    def print_summary(self):
        """Print test summary"""
        print(f"\n{'='*80}")
        print("TEST SUMMARY")
        print(f"{'='*80}\n")
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {len(self.successes)} ✓")
        print(f"Failed: {len(self.failures)} ✗")
        
        if self.failures:
            print(f"\n{'='*80}")
            print("FAILURES:")
            print(f"{'='*80}\n")
            for failure in self.failures:
                print(f"✗ {failure['test']}")
                if failure.get('expected') and failure.get('actual'):
                    print(f"  Expected: {failure['expected']}")
                    print(f"  Actual: {failure['actual']}")
        
        print(f"\n{'='*80}\n")
        
        return len(self.failures) == 0


def main():
    """Run all tests"""
    tester = CharacterFieldTester()
    
    try:
        tester.test_platinum()
        success = tester.print_summary()
        
        if success:
            print("✅ ALL TESTS PASSED!")
            return 0
        else:
            print("❌ SOME TESTS FAILED")
            return 1
    
    finally:
        tester.conn.close()


if __name__ == "__main__":
    import sys
    sys.exit(main())
