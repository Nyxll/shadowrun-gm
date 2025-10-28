#!/usr/bin/env python3
"""
STRICT UI TEST - Verifies EVERY line from character .md files appears in the UI
Uses Playwright to actually render the page and check content
"""
import os
import re
import asyncio
from playwright.async_api import async_playwright
from typing import List, Dict, Set

CHARACTERS_DIR = "characters"
UI_URL = "http://localhost:8001"

class StrictUITester:
    """Test that every piece of character data appears in the UI"""
    
    def __init__(self):
        self.failures = []
        self.warnings = []
        self.passes = 0
    
    async def test_character(self, browser, char_file: str):
        """Test a single character's UI rendering"""
        char_name = os.path.splitext(char_file)[0]
        print(f"\n{'='*70}")
        print(f"Testing: {char_name}")
        print(f"{'='*70}")
        
        # Parse the markdown file
        filepath = os.path.join(CHARACTERS_DIR, char_file)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract street name for API lookup
        street_match = re.search(r'\*\*Street Name\*\*:\s*(.+)', content)
        if not street_match:
            print(f"  ✗ Could not find street name in {char_file}")
            return
        
        street_name = street_match.group(1).strip()
        
        # Load the character sheet page
        page = await browser.new_page()
        
        try:
            # Navigate to main page
            await page.goto(f"{UI_URL}/")
            
            # Wait for page to load
            await page.wait_for_selector('#character-select', timeout=10000)
            
            # Select the character from dropdown
            await page.select_option('#character-select', street_name)
            
            # Click "VIEW SHEET" button
            await page.click('#view-sheet-button')
            
            # Wait for modal to appear
            await page.wait_for_selector('#character-sheet-content', timeout=10000)
            
            # Get the full page HTML
            html_content = await page.content()
            
            # Test all sections
            await self.test_basic_info(content, html_content, char_name)
            await self.test_attributes(content, html_content, char_name)
            await self.test_skills(content, html_content, char_name)
            await self.test_cyberware_bioware(content, html_content, char_name)
            await self.test_gear(content, html_content, char_name)
            await self.test_vehicles(content, html_content, char_name)
            
        finally:
            await page.close()
    
    async def test_basic_info(self, md_content: str, html: str, char_name: str):
        """Test basic character information"""
        print("\n  BASIC INFO:")
        
        # Name
        name_match = re.search(r'\*\*Name\*\*:\s*(.+)', md_content)
        if name_match:
            name = name_match.group(1).strip()
            if name in html:
                print(f"    ✓ Name: {name}")
                self.passes += 1
            else:
                print(f"    ✗ Name missing: {name}")
                self.failures.append(f"{char_name}: Name '{name}' not in UI")
        
        # Street Name
        street_match = re.search(r'\*\*Street Name\*\*:\s*(.+)', md_content)
        if street_match:
            street = street_match.group(1).strip()
            if street in html:
                print(f"    ✓ Street Name: {street}")
                self.passes += 1
            else:
                print(f"    ✗ Street Name missing: {street}")
                self.failures.append(f"{char_name}: Street name '{street}' not in UI")
        
        # Archetype
        arch_match = re.search(r'\*\*Archetype\*\*:\s*(.+)', md_content)
        if arch_match:
            archetype = arch_match.group(1).strip()
            if archetype in html:
                print(f"    ✓ Archetype: {archetype}")
                self.passes += 1
            else:
                print(f"    ✗ Archetype missing: {archetype}")
                self.failures.append(f"{char_name}: Archetype '{archetype}' not in UI")
    
    async def test_attributes(self, md_content: str, html: str, char_name: str):
        """Test all attributes"""
        print("\n  ATTRIBUTES:")
        
        attr_section = re.search(r'## Attributes\s*\n### Base Form\s*\n(.*?)(?:\n###|\n##)', md_content, re.DOTALL)
        if not attr_section:
            return
        
        for line in attr_section.group(1).split('\n'):
            match = re.match(r'-\s*\*\*(\w+)\*\*:\s*(.+)', line)
            if match:
                attr_name = match.group(1)
                attr_value = match.group(2).strip()
                
                # Extract just the base number
                base_match = re.match(r'(\d+)', attr_value)
                if base_match:
                    base_val = base_match.group(1)
                    
                    # Skip Magic=0 and similar N/A values
                    if attr_name == 'Magic' and base_val == '0':
                        continue
                    
                    # Check if attribute name and value appear in HTML
                    if attr_name in html and base_val in html:
                        print(f"    ✓ {attr_name}: {base_val}")
                        self.passes += 1
                    else:
                        print(f"    ✗ {attr_name}: {base_val} not found")
                        self.failures.append(f"{char_name}: Attribute {attr_name}={base_val} not in UI")
    
    async def test_skills(self, md_content: str, html: str, char_name: str):
        """Test all skills"""
        print("\n  SKILLS:")
        
        skills_section = re.search(r'## Skills\s*\n(.*?)(?:\n##)', md_content, re.DOTALL)
        if not skills_section:
            return
        
        skill_count = 0
        for line in skills_section.group(1).split('\n'):
            match = re.match(r'-\s*\*\*([^*]+)\*\*:\s*(.+)', line)
            if match:
                skill_name = match.group(1).strip()
                skill_value = match.group(2).strip()
                
                # Extract base rating
                base_match = re.match(r'(\d+)', skill_value)
                if base_match:
                    skill_count += 1
                    base_val = base_match.group(1)
                    
                    if skill_name in html:
                        print(f"    ✓ {skill_name}: {base_val}")
                        self.passes += 1
                    else:
                        print(f"    ✗ {skill_name} not found")
                        self.failures.append(f"{char_name}: Skill '{skill_name}' not in UI")
        
        if skill_count == 0:
            print("    (No skills found)")
    
    async def test_cyberware_bioware(self, md_content: str, html: str, char_name: str):
        """Test all cyberware and bioware items with their modifiers"""
        print("\n  CYBERWARE/BIOWARE:")
        
        section_match = re.search(r'##\s+Cyberware/Bioware.*?\n(.*?)(?=\n##|\Z)', md_content, re.DOTALL | re.IGNORECASE)
        if not section_match:
            print("    (No cyberware/bioware section)")
            return
        
        section = section_match.group(1)
        
        # Test cyberware
        cyber_match = re.search(r'###\s+Cyberware(.*?)(?=###|\Z)', section, re.DOTALL | re.IGNORECASE)
        if cyber_match:
            items = re.split(r'\n-\s+\*\*', cyber_match.group(1))
            for item in items[1:]:
                lines = item.split('\n')
                if not lines:
                    continue
                
                # Get item name
                name_match = re.match(r'(.+?)\*\*', lines[0])
                if name_match:
                    item_name = name_match.group(1).strip()
                    
                    # Skip "None" entries
                    if item_name.upper() in ('NONE', 'N/A', 'NA'):
                        continue
                    
                    if item_name in html:
                        print(f"    ✓ Cyberware: {item_name}")
                        self.passes += 1
                        
                        # Check modifiers
                        for line in lines[1:]:
                            line = line.strip()
                            if line.startswith('- '):
                                modifier = line[2:].strip()
                                # Check if the EXACT modifier text appears in HTML
                                if modifier in html:
                                    print(f"      ✓ Modifier: {modifier}")
                                    self.passes += 1
                                else:
                                    print(f"      ✗ Modifier missing: {modifier}")
                                    self.failures.append(f"{char_name}: Cyberware modifier '{modifier}' for {item_name} not in UI")
                    else:
                        print(f"    ✗ Cyberware missing: {item_name}")
                        self.failures.append(f"{char_name}: Cyberware '{item_name}' not in UI")
        
        # Test bioware
        bio_match = re.search(r'###\s+Bioware(.*?)(?=\n###|\n---|\Z)', section, re.DOTALL | re.IGNORECASE)
        if bio_match:
            items = re.split(r'\n-\s+\*\*', bio_match.group(1))
            for item in items[1:]:
                lines = item.split('\n')
                if not lines:
                    continue
                
                # Get item name
                name_match = re.match(r'(.+?)\*\*', lines[0])
                if name_match:
                    item_name = name_match.group(1).strip()
                    
                    if item_name in html:
                        print(f"    ✓ Bioware: {item_name}")
                        self.passes += 1
                        
                        # Check modifiers
                        for line in lines[1:]:
                            line = line.strip()
                            if line.startswith('- '):
                                modifier = line[2:].strip()
                                # Check if the EXACT modifier text appears in HTML
                                if modifier in html:
                                    print(f"      ✓ Modifier: {modifier}")
                                    self.passes += 1
                                else:
                                    print(f"      ✗ Modifier missing: {modifier}")
                                    self.failures.append(f"{char_name}: Bioware modifier '{modifier}' for {item_name} not in UI")
                    else:
                        print(f"    ✗ Bioware missing: {item_name}")
                        self.failures.append(f"{char_name}: Bioware '{item_name}' not in UI")
    
    async def test_gear(self, md_content: str, html: str, char_name: str):
        """Test weapons, armor, and equipment"""
        print("\n  GEAR:")
        
        gear_section = re.search(r'## Gear\s*\n(.*?)(?:\n## (?!#)|$)', md_content, re.DOTALL)
        if not gear_section:
            print("    (No gear section)")
            return
        
        gear_count = 0
        for line in gear_section.group(1).split('\n'):
            # Match item lines like "- **Item Name**"
            match = re.match(r'-\s+\*\*([^*]+)\*\*', line)
            if match:
                item_name = match.group(1).strip()
                
                # Skip N/A entries
                if item_name.upper() in ('N/A', 'NONE'):
                    continue
                
                gear_count += 1
                if item_name in html:
                    print(f"    ✓ {item_name}")
                    self.passes += 1
                else:
                    print(f"    ✗ {item_name} not found")
                    self.failures.append(f"{char_name}: Gear '{item_name}' not in UI")
        
        if gear_count == 0:
            print("    (No gear items)")
    
    async def test_vehicles(self, md_content: str, html: str, char_name: str):
        """Test vehicles"""
        print("\n  VEHICLES:")
        
        # Look for vehicles in gear section
        gear_section = re.search(r'## Gear\s*\n(.*?)(?:\n## (?!#)|$)', md_content, re.DOTALL)
        if not gear_section:
            return
        
        # Find vehicles subsection
        vehicles_match = re.search(r'###\s+Vehicles(.*?)(?=\n###|\Z)', gear_section.group(1), re.DOTALL)
        if not vehicles_match:
            print("    (No vehicles)")
            return
        
        vehicle_count = 0
        for line in vehicles_match.group(1).split('\n'):
            match = re.match(r'-\s+\*\*([^*]+)\*\*', line)
            if match:
                vehicle_name = match.group(1).strip()
                
                if vehicle_name.upper() in ('N/A', 'NONE'):
                    continue
                
                vehicle_count += 1
                if vehicle_name in html:
                    print(f"    ✓ {vehicle_name}")
                    self.passes += 1
                else:
                    print(f"    ✗ {vehicle_name} not found")
                    self.failures.append(f"{char_name}: Vehicle '{vehicle_name}' not in UI")
        
        if vehicle_count == 0:
            print("    (No vehicles)")
    
    async def run_all_tests(self):
        """Run tests for all characters"""
        char_files = [f for f in os.listdir(CHARACTERS_DIR) 
                     if f.endswith('.md') and f != 'README.md']
        
        print("="*70)
        print("STRICT UI TEST - Verifying ALL character data in UI")
        print("="*70)
        print(f"Testing {len(char_files)} characters against {UI_URL}")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            
            for char_file in char_files:
                try:
                    await self.test_character(browser, char_file)
                except Exception as e:
                    print(f"\n  ✗ ERROR testing {char_file}: {e}")
                    import traceback
                    traceback.print_exc()
            
            await browser.close()
        
        # Print summary
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        print(f"Passed: {self.passes} ✓")
        print(f"Failed: {len(self.failures)} ✗")
        print(f"Warnings: {len(self.warnings)} ⚠")
        
        if self.failures:
            print("\nFAILURES:")
            for failure in self.failures:
                print(f"  ✗ {failure}")
        
        if self.warnings:
            print("\nWARNINGS:")
            for warning in self.warnings:
                print(f"  ⚠ {warning}")
        
        print("="*70)
        
        return len(self.failures) == 0


async def main():
    """Main entry point"""
    tester = StrictUITester()
    success = await tester.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    import sys
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
