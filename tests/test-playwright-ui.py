#!/usr/bin/env python3
"""
Playwright UI test - verify character sheet displays correctly
"""
import asyncio
from playwright.async_api import async_playwright
import sys

async def test_character_sheet():
    """Test character sheet rendering with Playwright"""
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Navigate to the app
        await page.goto('http://localhost:8001')
        
        # Wait for character list to load
        await page.wait_for_selector('.character-card', timeout=10000)
        
        print("✓ Page loaded successfully")
        
        # Click on Oak character
        oak_card = page.locator('.character-card:has-text("Oak")')
        await oak_card.click()
        
        # Wait for character sheet to load
        await page.wait_for_selector('#sheet-character-name', timeout=10000)
        
        print("✓ Character sheet loaded")
        
        # Check character name
        name = await page.locator('#sheet-character-name').text_content()
        print(f"  Character name: {name}")
        
        # Check attributes section
        attributes_section = page.locator('.sheet-section:has-text("Attributes")')
        await attributes_section.wait_for()
        
        print("✓ Attributes section found")
        
        # Get all stat boxes in attributes section
        stat_boxes = attributes_section.locator('.stat-box')
        count = await stat_boxes.count()
        
        print(f"  Found {count} attribute stat boxes")
        
        # Check each attribute
        for i in range(count):
            stat_box = stat_boxes.nth(i)
            label = await stat_box.locator('.stat-label').text_content()
            value = await stat_box.locator('.stat-value').text_content()
            print(f"  {label}: {value}")
            
            # Verify value is not just "1"
            if value.strip() == "1" and label not in ["Essence"]:
                print(f"  ⚠ WARNING: {label} shows value '1' - may be incorrect")
        
        # Check skills section
        skills_section = page.locator('.sheet-section:has-text("Skills")')
        await skills_section.wait_for()
        
        print("✓ Skills section found")
        
        # Get skill items
        skill_items = skills_section.locator('.skill-item')
        skill_count = await skill_items.count()
        
        print(f"  Found {skill_count} skills")
        
        # Check first few skills
        for i in range(min(3, skill_count)):
            skill = skill_items.nth(i)
            name = await skill.locator('.skill-name').text_content()
            rating = await skill.locator('.skill-rating').text_content()
            print(f"  {name}: {rating}")
        
        # Take a screenshot
        await page.screenshot(path='tests/screenshots/oak-character-sheet.png', full_page=True)
        print("✓ Screenshot saved to tests/screenshots/oak-character-sheet.png")
        
        # Keep browser open for manual inspection
        print("\n=== Browser will stay open for 30 seconds for manual inspection ===")
        await asyncio.sleep(30)
        
        await browser.close()
        
        print("\n✓ Test completed successfully")
        return True

async def main():
    try:
        success = await test_character_sheet()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
