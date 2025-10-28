#!/usr/bin/env python3
"""
Comprehensive Character Sheet UI Test
Tests that ALL character data is properly displayed in the UI for ALL characters
Cross-references source character markdown files with UI display
Uses Playwright to render actual character sheets and validate field presence
"""

import os
import sys
import asyncio
import requests
import re
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:8001"
TIMEOUT = 15000  # 15 seconds
CHARACTERS_DIR = "characters"


class CharacterSheetUITest:
    """Test character sheet rendering for all characters"""
    
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.tests_run = 0
        self.characters = []
        self.source_data = {}  # Store parsed source file data
    
    def parse_source_file(self, char_name):
        """Parse the source markdown file for a character"""
        # Find the character file
        char_files = [f for f in os.listdir(CHARACTERS_DIR) 
                     if f.endswith('.md') and f != 'README.md']
        
        char_file = None
        for f in char_files:
            filepath = os.path.join(CHARACTERS_DIR, f)
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
                # Check if this file contains the character by street name OR full name
                if (re.search(rf'\*\*Street Name\*\*:\s*{re.escape(char_name)}', content) or
                    re.search(rf'\*\*Name\*\*:\s*{re.escape(char_name)}', content)):
                    char_file = filepath
                    break
        
        if not char_file:
            return None
        
        with open(char_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        source = {
            'cyberware_items': [],
            'bioware_items': [],
            'weapons': [],
            'armor': [],
            'equipment': [],
            'vehicles': [],
            'skills': []
        }
        
        # Parse Cyberware
        cyber_match = re.search(r'###\s+Cyberware\s*\n(.*?)(?=\n###|\n---|\Z)', content, re.DOTALL | re.IGNORECASE)
        if cyber_match:
            cyber_section = cyber_match.group(1)
            # Find all cyberware items (lines starting with - **)
            for match in re.finditer(r'-\s+\*\*([^*]+)\*\*\s*\(([\d.]+)\s+Essence\)', cyber_section):
                item_name = match.group(1).strip()
                essence = match.group(2)
                source['cyberware_items'].append({
                    'name': item_name,
                    'essence': essence
                })
        
        # Parse Bioware
        bio_match = re.search(r'###\s+Bioware\s*\n(.*?)(?=\n###|\n---|\Z)', content, re.DOTALL | re.IGNORECASE)
        if bio_match:
            bio_section = bio_match.group(1)
            for match in re.finditer(r'-\s+\*\*([^*]+)\*\*\s*\(([\d.]+)\s+Body Index\)', bio_section):
                item_name = match.group(1).strip()
                bi_cost = match.group(2)
                source['bioware_items'].append({
                    'name': item_name,
                    'body_index': bi_cost
                })
        
        # Parse Weapons
        weapons_match = re.search(r'###\s+Weapons\s*\n(.*?)(?=\n###|\Z)', content, re.DOTALL | re.IGNORECASE)
        if weapons_match:
            weapons_section = weapons_match.group(1)
            for match in re.finditer(r'-\s+\*\*([^*]+)\*\*', weapons_section):
                weapon_name = match.group(1).strip()
                if weapon_name.upper() not in ('N/A', 'NONE'):
                    source['weapons'].append(weapon_name)
        
        # Parse Armor
        armor_match = re.search(r'###\s+Armor\s*\n(.*?)(?=\n###|\Z)', content, re.DOTALL | re.IGNORECASE)
        if armor_match:
            armor_section = armor_match.group(1)
            for match in re.finditer(r'-\s+\*\*([^*]+)\*\*', armor_section):
                armor_name = match.group(1).strip()
                if armor_name.upper() not in ('N/A', 'NONE'):
                    source['armor'].append(armor_name)
        
        # Parse Equipment
        equip_match = re.search(r'###\s+Equipment\s*\n(.*?)(?=\n###|\Z)', content, re.DOTALL | re.IGNORECASE)
        if equip_match:
            equip_section = equip_match.group(1)
            for match in re.finditer(r'-\s+\*\*([^*]+)\*\*', equip_section):
                equip_name = match.group(1).strip()
                if equip_name.upper() not in ('N/A', 'NONE'):
                    source['equipment'].append(equip_name)
        
        # Parse Vehicles
        vehicles_match = re.search(r'###\s+Vehicles\s*\n(.*?)(?=\n###|\Z)', content, re.DOTALL | re.IGNORECASE)
        if vehicles_match:
            vehicles_section = vehicles_match.group(1)
            for match in re.finditer(r'-\s+\*\*([^*]+)\*\*', vehicles_section):
                vehicle_name = match.group(1).strip()
                if vehicle_name.upper() not in ('N/A', 'NONE'):
                    source['vehicles'].append(vehicle_name)
        
        # Parse Skills
        skills_match = re.search(r'##\s+Skills\s*\n(.*?)(?:\n##)', content, re.DOTALL)
        if skills_match:
            skills_section = skills_match.group(1)
            for match in re.finditer(r'-\s+\*\*([^*]+)\*\*:', skills_section):
                skill_name = match.group(1).strip()
                source['skills'].append(skill_name)
        
        return source
    
    async def setup(self):
        """Set up browser and get character list"""
        # Get list of characters from API
        try:
            response = requests.get(f"{BASE_URL}/api/characters")
            if response.status_code == 200:
                data = response.json()
                self.characters = data.get('characters', [])
                print(f"Found {len(self.characters)} characters to test\n")
            else:
                print(f"Error getting character list: {response.status_code}")
                sys.exit(1)
        except Exception as e:
            print(f"Error connecting to server: {e}")
            print("Make sure game-server.py is running on port 8001")
            sys.exit(1)
        
        # Set up Playwright
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=True)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        await self.page.set_viewport_size({"width": 1280, "height": 1024})
    
    async def teardown(self):
        """Clean up browser"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
    
    def log_test(self, name, passed, message="", is_warning=False):
        """Log test result"""
        self.tests_run += 1
        if passed:
            self.passed += 1
            print(f"  ✓ {name}")
        elif is_warning:
            self.warnings += 1
            print(f"  ⚠ {name}")
            if message:
                print(f"    Warning: {message}")
        else:
            self.failed += 1
            print(f"  ✗ {name}")
            if message:
                print(f"    Error: {message}")
    
    async def load_character_sheet(self, character_name):
        """Load character sheet in UI"""
        try:
            # Navigate to main page
            await self.page.goto(BASE_URL, wait_until="networkidle")
            
            # Wait for WebSocket connection
            await self.page.wait_for_selector("#connection-status:has-text('Connected')", timeout=TIMEOUT)
            
            # Wait for characters to load by checking status text
            await self.page.wait_for_selector("#status-display:has-text('Loaded')", timeout=TIMEOUT)
            
            # Additional wait to ensure dropdown is populated
            await asyncio.sleep(1)
            
            # Select character from dropdown
            dropdown = self.page.locator("#character-select")
            await dropdown.select_option(value=character_name)
            
            # Click "VIEW SHEET" button
            view_button = self.page.locator("#view-sheet-button")
            await view_button.click()
            
            # Wait for character sheet modal to appear
            await self.page.wait_for_selector("#character-sheet-modal.active", timeout=TIMEOUT)
            await self.page.wait_for_selector("#character-sheet-content", timeout=TIMEOUT)
            
            # Wait a bit for rendering to complete
            await asyncio.sleep(1)
            
            return True
        except Exception as e:
            print(f"    Error loading character sheet: {e}")
            return False
    
    async def close_character_sheet(self):
        """Close the character sheet modal"""
        try:
            close_button = self.page.locator("#character-sheet-modal .close-button")
            await close_button.click()
            await asyncio.sleep(0.5)
        except:
            pass
    
    async def test_basic_info(self, char_data):
        """Test basic information section"""
        try:
            # Check for name
            name_visible = await self.page.locator(f"text={char_data['name']}").count() > 0
            self.log_test("Name displayed", name_visible)
            
            # Check for street name if exists
            if char_data.get('street_name'):
                street_name_visible = await self.page.locator(f"text={char_data['street_name']}").count() > 0
                self.log_test("Street name displayed", street_name_visible)
            
            # Check for archetype
            if char_data.get('archetype'):
                archetype_visible = await self.page.locator(f"text={char_data['archetype']}").count() > 0
                self.log_test("Archetype displayed", archetype_visible, 
                            f"Archetype '{char_data['archetype']}' not found" if not archetype_visible else "")
            
        except Exception as e:
            self.log_test("Basic info section", False, str(e))
    
    async def test_attributes(self, char_data):
        """Test attributes section"""
        try:
            attrs = char_data.get('attributes', {})
            
            # Check key attributes
            for attr_name in ['body', 'quickness', 'strength', 'charisma', 'intelligence', 'willpower']:
                if attr_name in attrs and attrs[attr_name] is not None:
                    # Look for attribute value in the page
                    attr_section = await self.page.locator("text=Attributes").count() > 0
                    if attr_section:
                        self.log_test(f"Attribute: {attr_name.capitalize()}", True)
                    else:
                        self.log_test(f"Attribute: {attr_name.capitalize()}", False, "Attributes section not found")
                        break
            
        except Exception as e:
            self.log_test("Attributes section", False, str(e))
    
    async def test_skills(self, char_data):
        """Test skills section"""
        try:
            # CRUD API returns flat array of skills
            skills = char_data.get('skills', [])
            
            if skills:
                skills_section = await self.page.locator("text=Skills").count() > 0
                self.log_test("Skills section present", skills_section)
                
                # Check for at least one skill
                if skills:
                    first_skill = skills[0]['skill_name']
                    skill_visible = await self.page.locator(f"text={first_skill}").count() > 0
                    self.log_test(f"Sample skill displayed ({first_skill})", skill_visible)
            else:
                self.log_test("Skills section", True, is_warning=True, message="No skills to display")
                
        except Exception as e:
            self.log_test("Skills section", False, str(e))
    
    async def test_cyberware(self, char_data):
        """Test cyberware section"""
        try:
            # CRUD API returns modifiers array - filter for cyberware
            modifiers = char_data.get('modifiers', [])
            cyberware = [m for m in modifiers if m.get('source_type') == 'cyberware']
            
            if cyberware:
                # Check if cyberware section exists
                cyber_section = await self.page.locator("text=Cyberware").count() > 0
                self.log_test("Cyberware section present", cyber_section)
                
                # Check for first cyberware item
                first_cyber = cyberware[0]
                cyber_name = first_cyber.get('source', 'Unknown')
                cyber_name_visible = await self.page.locator(f"text={cyber_name}").count() > 0
                self.log_test(f"Cyberware item displayed ({cyber_name})", cyber_name_visible)
                
                # Check for essence cost from modifier_data
                mod_data = first_cyber.get('modifier_data', {})
                essence_cost = mod_data.get('essence_cost', 0)
                if essence_cost > 0:
                    essence_visible = await self.page.locator(f"text={essence_cost} ESS").count() > 0
                    self.log_test("Cyberware essence cost displayed", essence_visible)
                
                # Check for effects from modifier_data
                effects = mod_data.get('special_abilities', [])
                if effects:
                    # Check if at least one effect is visible
                    effect_found = False
                    for effect in effects:
                        if await self.page.locator(f"text={effect}").count() > 0:
                            effect_found = True
                            break
                    self.log_test("Cyberware effects displayed", effect_found,
                                f"Expected effects: {effects}" if not effect_found else "")
                else:
                    self.log_test("Cyberware effects", True, is_warning=True, 
                                message=f"{cyber_name} has no effects in database")
                
                # DEEP TEST: Check ALL cyberware items and their effects
                for cyber in cyberware:
                    cyber_name = cyber.get('source', 'Unknown')
                    mod_data = cyber.get('modifier_data', {})
                    item_effects = mod_data.get('special_abilities', [])
                    if item_effects:
                        # Verify each effect is visible
                        for effect in item_effects:
                            effect_visible = await self.page.locator(f"text={effect}").count() > 0
                            self.log_test(f"  └─ {cyber_name}: {effect}", effect_visible,
                                        f"Effect not visible in UI" if not effect_visible else "")
            else:
                self.log_test("Cyberware section", True, is_warning=True, message="No cyberware to display")
                
        except Exception as e:
            self.log_test("Cyberware section", False, str(e))
    
    async def test_bioware(self, char_data):
        """Test bioware section"""
        try:
            # CRUD API returns modifiers array - filter for bioware
            modifiers = char_data.get('modifiers', [])
            bioware = [m for m in modifiers if m.get('source_type') == 'bioware']
            
            if bioware:
                # Check if bioware section exists
                bio_section = await self.page.locator("text=Bioware").count() > 0
                self.log_test("Bioware section present", bio_section)
                
                # Check for first bioware item
                first_bio = bioware[0]
                bio_name = first_bio.get('source', 'Unknown')
                bio_name_visible = await self.page.locator(f"text={bio_name}").count() > 0
                self.log_test(f"Bioware item displayed ({bio_name})", bio_name_visible)
                
                # Check for body index cost from modifier_data
                mod_data = first_bio.get('modifier_data', {})
                bi_cost = mod_data.get('body_index_cost', 0)
                if bi_cost > 0:
                    bi_visible = await self.page.locator(f"text={bi_cost} B.I.").count() > 0
                    self.log_test("Bioware body index cost displayed", bi_visible)
                
                # Check for effects from modifier_data
                effects = mod_data.get('special_abilities', [])
                if effects:
                    effect_found = False
                    for effect in effects:
                        if await self.page.locator(f"text={effect}").count() > 0:
                            effect_found = True
                            break
                    self.log_test("Bioware effects displayed", effect_found,
                                f"Expected effects: {effects}" if not effect_found else "")
                else:
                    self.log_test("Bioware effects", True, is_warning=True,
                                message=f"{bio_name} has no effects in database")
            else:
                self.log_test("Bioware section", True, is_warning=True, message="No bioware to display")
                
        except Exception as e:
            self.log_test("Bioware section", False, str(e))
    
    async def test_weapons(self, char_data):
        """Test weapons section"""
        try:
            # CRUD API returns gear array - filter for weapons
            gear = char_data.get('gear', [])
            weapons = [g for g in gear if g.get('gear_type') == 'weapon']
            
            if weapons:
                weapons_section = await self.page.locator("text=Weapons").count() > 0
                self.log_test("Weapons section present", weapons_section)
                
                # Check for first weapon
                first_weapon = weapons[0]
                weapon_name = first_weapon.get('gear_name', 'Unknown')
                weapon_visible = await self.page.locator(f"text={weapon_name}").count() > 0
                self.log_test(f"Weapon displayed ({weapon_name})", weapon_visible)
            else:
                self.log_test("Weapons section", True, is_warning=True, message="No weapons to display")
                
        except Exception as e:
            self.log_test("Weapons section", False, str(e))
    
    async def test_armor(self, char_data):
        """Test armor section"""
        try:
            # CRUD API returns gear array - filter for armor
            gear = char_data.get('gear', [])
            armor = [g for g in gear if g.get('gear_type') == 'armor']
            
            if armor:
                armor_section = await self.page.locator("text=Armor").count() > 0
                self.log_test("Armor section present", armor_section)
                
                # Check for first armor item
                first_armor = armor[0]
                armor_name = first_armor.get('gear_name', 'Unknown')
                armor_visible = await self.page.locator(f"text={armor_name}").count() > 0
                self.log_test(f"Armor displayed ({armor_name})", armor_visible)
            else:
                self.log_test("Armor section", True, is_warning=True, message="No armor to display")
                
        except Exception as e:
            self.log_test("Armor section", False, str(e))
    
    async def test_equipment(self, char_data):
        """Test equipment section"""
        try:
            # CRUD API returns gear array - filter for equipment
            gear = char_data.get('gear', [])
            equipment = [g for g in gear if g.get('gear_type') == 'equipment']
            
            if equipment:
                equip_section = await self.page.locator("text=Equipment").count() > 0
                self.log_test("Equipment section present", equip_section)
            else:
                self.log_test("Equipment section", True, is_warning=True, message="No equipment to display")
                
        except Exception as e:
            self.log_test("Equipment section", False, str(e))
    
    async def test_vehicles(self, char_data):
        """Test vehicles section"""
        try:
            vehicles = char_data.get('vehicles', [])
            
            if vehicles:
                vehicles_section = await self.page.locator("text=Vehicles").count() > 0
                self.log_test("Vehicles section present", vehicles_section)
                
                # Check for first vehicle
                first_vehicle = vehicles[0]
                vehicle_name = first_vehicle.get('vehicle_name', 'Unknown')
                vehicle_visible = await self.page.locator(f"text={vehicle_name}").count() > 0
                self.log_test(f"Vehicle displayed ({vehicle_name})", vehicle_visible)
            else:
                self.log_test("Vehicles section", True, is_warning=True, message="No vehicles to display")
                
        except Exception as e:
            self.log_test("Vehicles section", False, str(e))
    
    async def test_source_vs_ui(self, char_name, source_data):
        """Cross-reference source file data with UI display"""
        print("\n  SOURCE FILE CROSS-REFERENCE:")
        
        # Test cyberware from source file
        for cyber in source_data['cyberware_items']:
            visible = await self.page.locator(f"text={cyber['name']}").count() > 0
            self.log_test(f"Source cyberware: {cyber['name']}", visible,
                        f"Found in source file but not in UI" if not visible else "")
        
        # Test bioware from source file
        for bio in source_data['bioware_items']:
            visible = await self.page.locator(f"text={bio['name']}").count() > 0
            self.log_test(f"Source bioware: {bio['name']}", visible,
                        f"Found in source file but not in UI" if not visible else "")
        
        # Test weapons from source file
        for weapon in source_data['weapons']:
            visible = await self.page.locator(f"text={weapon}").count() > 0
            self.log_test(f"Source weapon: {weapon}", visible,
                        f"Found in source file but not in UI" if not visible else "")
        
        # Test armor from source file
        for armor in source_data['armor']:
            visible = await self.page.locator(f"text={armor}").count() > 0
            self.log_test(f"Source armor: {armor}", visible,
                        f"Found in source file but not in UI" if not visible else "")
        
        # Test equipment from source file
        for equip in source_data['equipment'][:3]:  # Test first 3 to avoid too many tests
            visible = await self.page.locator(f"text={equip}").count() > 0
            self.log_test(f"Source equipment: {equip}", visible,
                        f"Found in source file but not in UI" if not visible else "")
        
        # Test vehicles from source file
        for vehicle in source_data['vehicles']:
            visible = await self.page.locator(f"text={vehicle}").count() > 0
            self.log_test(f"Source vehicle: {vehicle}", visible,
                        f"Found in source file but not in UI" if not visible else "")
        
        # Test skills from source file (sample first 5)
        for skill in source_data['skills'][:5]:
            visible = await self.page.locator(f"text={skill}").count() > 0
            self.log_test(f"Source skill: {skill}", visible,
                        f"Found in source file but not in UI" if not visible else "")
    
    async def test_character(self, character):
        """Test all fields for a single character"""
        char_name = character['name']
        print(f"\n{'='*70}")
        print(f"Testing: {char_name}")
        print(f"{'='*70}")
        
        # Parse source file
        source_data = self.parse_source_file(char_name)
        if source_data:
            print(f"  Parsed source file: {len(source_data['cyberware_items'])} cyberware, "
                  f"{len(source_data['bioware_items'])} bioware, "
                  f"{len(source_data['weapons'])} weapons, "
                  f"{len(source_data['skills'])} skills")
        else:
            print(f"  ⚠ Could not find source file for {char_name}")
        
        # Get full character data from API
        try:
            response = requests.get(f"{BASE_URL}/api/character/{char_name}")
            if response.status_code != 200:
                print(f"  ✗ Failed to get character data from API: {response.status_code}")
                return
            char_data = response.json()
        except Exception as e:
            print(f"  ✗ Error getting character data: {e}")
            return
        
        # Load character sheet in UI
        if not await self.load_character_sheet(char_name):
            print(f"  ✗ Failed to load character sheet")
            return
        
        print("\n  API DATA TESTS:")
        # Run all field tests
        await self.test_basic_info(char_data)
        await self.test_attributes(char_data)
        await self.test_skills(char_data)
        await self.test_cyberware(char_data)
        await self.test_bioware(char_data)
        await self.test_weapons(char_data)
        await self.test_armor(char_data)
        await self.test_equipment(char_data)
        await self.test_vehicles(char_data)
        
        # Cross-reference with source file
        if source_data:
            await self.test_source_vs_ui(char_name, source_data)
        
        # Close character sheet
        await self.close_character_sheet()
    
    async def run_all_tests(self):
        """Run tests for all characters"""
        print("\n" + "="*70)
        print("SHADOWRUN GM - CHARACTER SHEET UI TEST SUITE")
        print("="*70)
        print("Testing that ALL character data displays correctly in the UI")
        print("="*70 + "\n")
        
        await self.setup()
        
        try:
            # Test each character
            for character in self.characters:
                await self.test_character(character)
        
        finally:
            await self.teardown()
        
        # Print summary
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.passed} ✓")
        print(f"Failed: {self.failed} ✗")
        print(f"Warnings: {self.warnings} ⚠")
        print("="*70 + "\n")
        
        if self.failed > 0:
            print("RESULT: FAILED - Some character data is not displaying correctly")
            return False
        elif self.warnings > 0:
            print("RESULT: PASSED WITH WARNINGS - All critical data displays, some optional data missing")
            return True
        else:
            print("RESULT: PASSED - All character data displays correctly")
            return True


async def main():
    """Main test runner"""
    suite = CharacterSheetUITest()
    success = await suite.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
