#!/usr/bin/env python3
"""
Test UI rendering with Playwright
"""
import asyncio
from playwright.async_api import async_playwright
import time

async def test_character_sheet_ui():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        print("="*80)
        print("TESTING CHARACTER SHEET UI RENDERING")
        print("="*80)
        
        # Navigate to the app
        print("\n1. Loading main page...")
        await page.goto('http://localhost:8001')
        await page.wait_for_load_state('networkidle')
        await asyncio.sleep(2)
        
        # Select Platinum from dropdown and click View Sheet
        print("\n2. Selecting Platinum character from dropdown...")
        await page.select_option('select#character-select', 'Kent Jefferies')
        await asyncio.sleep(1)
        
        print("\n3. Clicking View Sheet button...")
        await page.click('button:has-text("View Sheet")')
        await asyncio.sleep(3)
        
        # Take screenshot
        await page.screenshot(path='screenshots/platinum-sheet.png')
        print("   Screenshot saved: screenshots/platinum-sheet.png")
        
        # Get the full page content for analysis
        print("\n4. Analyzing page content...")
        page_content = await page.content()
        
        # Check for specific sections
        sections_found = []
        sections_missing = []
        
        checks = [
            ('Essence', 'Essence'),
            ('Body Index', 'Body Index'),
            ('Cyberware', 'Cyberware'),
            ('Bioware', 'Bioware'),
            ('Vehicles', 'Vehicles'),
            ('Contacts', 'Contacts'),
            ('Spells', 'Magic'),
            ('Skills', 'Skills')
        ]
        
        for name, search_term in checks:
            if search_term in page_content:
                sections_found.append(name)
                print(f"   ✅ {name} section found")
            else:
                sections_missing.append(name)
                print(f"   ❌ {name} section missing")
        
        # Check for common issues
        print("\n5. Checking for common issues...")
        issues = []
        if 'undefined' in page_content.lower():
            issues.append("Found 'undefined' in page")
        if page_content.count('0.0') > 5:
            issues.append("Multiple instances of '0.0' (possible essence display issue)")
        if 'NaN' in page_content:
            issues.append("Found 'NaN' in page")
        if '1 (1)' in page_content:  # Attributes showing as 1
            issues.append("Attributes showing as 1 (data not loading)")
        
        if issues:
            print("   ❌ ISSUES FOUND:")
            for issue in issues:
                print(f"      - {issue}")
        else:
            print("   ✅ No obvious issues found")
        
        # Summary
        print("\n6. SUMMARY:")
        print(f"   Sections found: {len(sections_found)}/{len(checks)}")
        print(f"   Issues found: {len(issues)}")
        
        print("\n7. Waiting for manual inspection...")
        print("    Browser will stay open for 30 seconds for manual inspection")
        await asyncio.sleep(30)
        
        await browser.close()
        print("\n" + "="*80)
        print("TEST COMPLETE")
        print("="*80)

if __name__ == "__main__":
    asyncio.run(test_character_sheet_ui())
