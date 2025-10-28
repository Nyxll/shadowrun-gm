#!/usr/bin/env python3
"""
Comprehensive Character Sheet Test Suite
Tests all characters and validates specific data fields
"""
import asyncio
from playwright.async_api import async_playwright
import json

class CharacterSheetTester:
    """Comprehensive character sheet testing"""
    
    def __init__(self):
        self.results = []
        self.failures = []
    
    async def test_character(self, page, character_name):
        """Test a single character's sheet"""
        print(f"\n{'='*80}")
        print(f"Testing: {character_name}")
        print(f"{'='*80}")
        
        test_results = {
            'character': character_name,
            'sections_found': 0,
            'attributes_count': 0,
            'skills_count': 0,
            'items_count': 0,
            'spells_count': 0,
            'errors': []
        }
        
        try:
            # Select character
            await page.select_option("#character-select", character_name)
            await asyncio.sleep(0.5)
            
            # Click VIEW SHEET
            await page.click("#view-sheet-button")
            
            # Wait for modal
            await page.wait_for_selector(".character-sheet-modal.active", timeout=5000)
            await asyncio.sleep(1)
            
            # Count sections
            sections = await page.query_selector_all(".sheet-section")
            test_results['sections_found'] = len(sections)
            print(f"✓ Found {len(sections)} sections")
            
            # Check attributes
            stat_grids = await page.query_selector_all(".stat-grid")
            if len(stat_grids) > 0:
                stat_boxes = await stat_grids[0].query_selector_all(".stat-box")
                test_results['attributes_count'] = len(stat_boxes)
                print(f"✓ {len(stat_boxes)} attributes")
            
            # Check skills
            skill_grids = await page.query_selector_all(".skill-grid")
            total_skills = 0
            for grid in skill_grids:
                skills = await grid.query_selector_all(".skill-item")
                total_skills += len(skills)
            test_results['skills_count'] = total_skills
            print(f"✓ {total_skills} skills")
            
            # Check items
            item_lists = await page.query_selector_all(".item-list")
            total_items = 0
            for item_list in item_lists:
                items = await item_list.query_selector_all(".list-item")
                total_items += len(items)
            test_results['items_count'] = total_items
            print(f"✓ {total_items} items")
            
            # Check spells
            spell_lists = await page.query_selector_all(".spell-list")
            total_spells = 0
            for spell_list in spell_lists:
                spells = await spell_list.query_selector_all(".spell-item")
                total_spells += len(spells)
            test_results['spells_count'] = total_spells
            if total_spells > 0:
                print(f"✓ {total_spells} spells")
            
            # Validate specific data is present
            await self.validate_character_data(page, character_name, test_results)
            
            # Take screenshot
            screenshot_path = f"tests/screenshots/comprehensive-{character_name.lower()}.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            print(f"✓ Screenshot: {screenshot_path}")
            
            # Close modal
            await page.click(".sheet-close")
            await asyncio.sleep(0.5)
            
            self.results.append(test_results)
            print(f"✅ {character_name} test PASSED")
            
        except Exception as e:
            test_results['errors'].append(str(e))
            self.failures.append(character_name)
            print(f"❌ {character_name} test FAILED: {e}")
            self.results.append(test_results)
    
    async def validate_character_data(self, page, character_name, test_results):
        """Validate specific character data is displayed correctly"""
        
        # Get all text content
        content = await page.inner_text(".sheet-body")
        
        # Character-specific validations
        if character_name == "Oak":
            # Oak is a shaman - should have magic
            if test_results['spells_count'] == 0:
                test_results['errors'].append("No spells found for shaman")
            else:
                print(f"  ✓ Magic character validation passed ({test_results['spells_count']} spells)")
        
        elif character_name == "Platinum":
            # Platinum is a street samurai - should have cyberware
            if "Smartlink" not in content and "Cyberware" not in content:
                test_results['errors'].append("Cyberware section not found")
            else:
                print(f"  ✓ Street samurai validation passed")
        
        elif character_name == "Manticore":
            # Manticore is a decker - should have cyberdeck
            if "Computer" not in content and "Cyberdeck" not in content:
                test_results['errors'].append("Decker skills/equipment not found")
            else:
                print(f"  ✓ Decker validation passed")
        
        # Validate sections are present (more reliable than text search)
        sections = await page.query_selector_all(".section-title")
        section_titles = []
        for section in sections:
            title = await section.inner_text()
            section_titles.append(title.strip())
        
        # Check for key sections
        required_sections = ["ATTRIBUTES", "SKILLS"]
        for req_section in required_sections:
            found = any(req_section in title.upper() for title in section_titles)
            if not found:
                test_results['errors'].append(f"{req_section} section not found")
    
    async def run_all_tests(self):
        """Run tests for all characters"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            
            # Enable console logging
            console_errors = []
            page.on("console", lambda msg: 
                console_errors.append(msg.text) if msg.type == "error" else None)
            page.on("pageerror", lambda err: console_errors.append(str(err)))
            
            print("\n" + "="*80)
            print("COMPREHENSIVE CHARACTER SHEET TEST SUITE")
            print("="*80)
            
            # Navigate to page
            print("\n1. Loading UI...")
            await page.goto("http://localhost:8001")
            await asyncio.sleep(2)
            
            # Wait for characters to load
            print("2. Waiting for characters to load...")
            await page.wait_for_function(
                "document.querySelector('#character-select').options.length > 1",
                timeout=10000
            )
            
            # Get list of all characters
            options = await page.query_selector_all("#character-select option")
            characters = []
            for option in options[1:]:  # Skip first "Select a character..." option
                value = await option.get_attribute("value")
                if value:
                    characters.append(value)
            
            print(f"3. Found {len(characters)} characters to test")
            print(f"   Characters: {', '.join(characters)}\n")
            
            # Test each character
            for char in characters:
                await self.test_character(page, char)
            
            # Print summary
            self.print_summary(console_errors)
            
            # Keep browser open briefly
            print("\nBrowser will close in 5 seconds...")
            await asyncio.sleep(5)
            
            await browser.close()
    
    def print_summary(self, console_errors):
        """Print test summary"""
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        
        total_tests = len(self.results)
        passed = total_tests - len(self.failures)
        
        print(f"\nTotal Characters Tested: {total_tests}")
        print(f"Passed: {passed}")
        print(f"Failed: {len(self.failures)}")
        
        if self.failures:
            print(f"\nFailed Characters: {', '.join(self.failures)}")
        
        # Detailed results
        print("\nDetailed Results:")
        print("-" * 80)
        for result in self.results:
            char = result['character']
            status = "✅ PASS" if char not in self.failures else "❌ FAIL"
            print(f"\n{char}: {status}")
            print(f"  Sections: {result['sections_found']}")
            print(f"  Attributes: {result['attributes_count']}")
            print(f"  Skills: {result['skills_count']}")
            print(f"  Items: {result['items_count']}")
            print(f"  Spells: {result['spells_count']}")
            
            if result['errors']:
                print(f"  Errors:")
                for error in result['errors']:
                    print(f"    - {error}")
        
        # Console errors
        if console_errors:
            print("\nConsole Errors:")
            for error in set(console_errors):  # Unique errors only
                if "404" not in error:  # Ignore 404s (favicon)
                    print(f"  - {error}")
        
        print("\n" + "="*80)
        
        if len(self.failures) == 0:
            print("✅ ALL TESTS PASSED!")
        else:
            print(f"❌ {len(self.failures)} TEST(S) FAILED")
        print("="*80 + "\n")

async def main():
    """Main test runner"""
    tester = CharacterSheetTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
