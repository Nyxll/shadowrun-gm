"""  """#!/usr/bin/env python3
"""
Test character sheet display in UI
Tests that all character data displays correctly
"""
import asyncio
from playwright.async_api import async_playwright
import json

async def test_character_sheet(character_name="Oak"):
    """Test character sheet display for a specific character"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Enable console logging
        console_messages = []
        page.on("console", lambda msg: console_messages.append(msg.text))
        page.on("pageerror", lambda err: print(f"PAGE ERROR: {err}"))
        
        print(f"\n{'='*80}")
        print(f"Testing Character Sheet Display: {character_name}")
        print(f"{'='*80}\n")
        
        # Navigate to page
        print("1. Loading UI...")
        await page.goto("http://localhost:8001")
        await asyncio.sleep(2)
        
        # Wait for characters to load (check dropdown has options)
        print("2. Waiting for characters to load...")
        await page.wait_for_function(
            "document.querySelector('#character-select').options.length > 1",
            timeout=10000
        )
        
        # Select character from dropdown
        print(f"3. Selecting character: {character_name}")
        await page.select_option("#character-select", character_name)
        
        # Click VIEW SHEET button
        print("4. Clicking VIEW SHEET button...")
        await page.click("#view-sheet-button")
        
        # Wait for modal to appear
        print("5. Waiting for character sheet modal...")
        await page.wait_for_selector(".character-sheet-modal.active", timeout=5000)
        
        # Wait for content to load
        await asyncio.sleep(2)
        
        # Take screenshot
        screenshot_path = f"tests/screenshots/character-sheet-{character_name.lower()}.png"
        await page.screenshot(path=screenshot_path, full_page=True)
        print(f"6. Screenshot saved: {screenshot_path}")
        
        # Check what sections are present
        print("\n7. Checking character sheet sections...")
        sections = await page.query_selector_all(".sheet-section")
        print(f"   Found {len(sections)} sections")
        
        for section in sections:
            header = await section.query_selector(".section-header")
            if header:
                title = await header.inner_text()
                print(f"   - {title}")
        
        # Check for specific data (using correct CSS classes from renderer)
        print("\n8. Checking for specific character data...")
        
        # Attributes (uses .stat-grid inside attributes section)
        stat_grids = await page.query_selector_all(".stat-grid")
        if len(stat_grids) > 0:
            print(f"   ✓ Found {len(stat_grids)} stat grids")
            # Count stat boxes in first grid (attributes)
            stat_boxes = await stat_grids[0].query_selector_all(".stat-box")
            print(f"     - {len(stat_boxes)} stat boxes in first grid (likely attributes)")
        else:
            print("   ✗ Stat grids NOT found")
        
        # Skills (uses .skill-grid)
        skill_grids = await page.query_selector_all(".skill-grid")
        if len(skill_grids) > 0:
            print(f"   ✓ Found {len(skill_grids)} skill grids")
            total_skills = 0
            for grid in skill_grids:
                skills = await grid.query_selector_all(".skill-item")
                total_skills += len(skills)
            print(f"     - {total_skills} total skills displayed")
        else:
            print("   ✗ Skill grids NOT found")
        
        # Gear/Items (uses .item-list)
        item_lists = await page.query_selector_all(".item-list")
        if len(item_lists) > 0:
            print(f"   ✓ Found {len(item_lists)} item lists")
            total_items = 0
            for item_list in item_lists:
                items = await item_list.query_selector_all(".list-item")
                total_items += len(items)
            print(f"     - {total_items} total items displayed")
        else:
            print("   ✗ Item lists NOT found")
        
        # Spells (uses .spell-list)
        spell_lists = await page.query_selector_all(".spell-list")
        if len(spell_lists) > 0:
            print(f"   ✓ Found {len(spell_lists)} spell lists")
            total_spells = 0
            for spell_list in spell_lists:
                spells = await spell_list.query_selector_all(".spell-item")
                total_spells += len(spells)
            print(f"     - {total_spells} total spells displayed")
        else:
            print("   ✗ Spell lists NOT found")
        
        # Check console for errors
        print("\n9. Console messages:")
        for msg in console_messages[-10:]:  # Last 10 messages
            if "error" in msg.lower() or "failed" in msg.lower():
                print(f"   ⚠ {msg}")
        
        print(f"\n{'='*80}")
        print("Test complete. Check screenshot for visual verification.")
        print(f"{'='*80}\n")
        
        # Keep browser open for manual inspection
        print("Browser will stay open for 10 seconds for manual inspection...")
        await asyncio.sleep(10)
        
        await browser.close()

async def test_all_characters():
    """Test character sheets for all characters"""
    characters = ["Oak", "Platinum", "Manticore"]
    
    for char in characters:
        try:
            await test_character_sheet(char)
            await asyncio.sleep(2)
        except Exception as e:
            print(f"\n✗ Failed to test {char}: {e}\n")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Test specific character
        asyncio.run(test_character_sheet(sys.argv[1]))
    else:
        # Test Oak by default
        asyncio.run(test_character_sheet("Oak"))
