#!/usr/bin/env python3
"""
Validate UI rendering with actual data checks using Playwright
"""
import asyncio
from playwright.async_api import async_playwright
import json

async def test_ui_validation():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        print("="*80)
        print("UI VALIDATION TEST - CHECKING ACTUAL RENDERED VALUES")
        print("="*80)
        
        # Navigate and load character
        print("\n1. Loading Platinum character sheet...")
        await page.goto('http://localhost:8001')
        await page.wait_for_load_state('networkidle')
        await asyncio.sleep(2)
        
        await page.select_option('select#character-select', 'Kent Jefferies')
        await asyncio.sleep(1)
        await page.click('button:has-text("View Sheet")')
        await asyncio.sleep(3)
        
        # Take screenshot
        await page.screenshot(path='screenshots/validation-test.png', full_page=True)
        print("   Screenshot saved: screenshots/validation-test.png")
        
        # Get the modal content
        modal = await page.query_selector('#character-sheet-modal')
        if not modal:
            print("   ❌ FATAL: Modal not found!")
            await browser.close()
            return
        
        modal_html = await modal.inner_html()
        
        print("\n2. VALIDATING ESSENCE DISPLAY:")
        # Check for essence value
        if 'Essence' in modal_html:
            print("   ✅ Essence label found")
            # Extract the actual value shown
            if '0.0' in modal_html or '0 (0)' in modal_html:
                print("   ❌ PROBLEM: Essence showing as 0.0 or 0 (0)")
                print("      This is a DATA issue - base_essence in DB is 0.0")
            else:
                print("   ✅ Essence has non-zero value")
        else:
            print("   ❌ Essence label not found")
        
        print("\n3. VALIDATING BODY INDEX DISPLAY:")
        if 'Body Index' in modal_html:
            print("   ✅ Body Index label found")
            if '8.35' in modal_html or '8.35/9' in modal_html:
                print("   ✅ Body Index showing correct value: 8.35/9.0")
            else:
                print("   ❌ Body Index value not found or incorrect")
        else:
            print("   ❌ Body Index label not found")
        
        print("\n4. VALIDATING CYBERWARE SECTION:")
        if 'Cyberware' in modal_html:
            print("   ✅ Cyberware section found")
            # Check for specific cyberware items
            if 'Cybereyes' in modal_html:
                print("   ✅ Cybereyes found")
                if '0.2' in modal_html:
                    print("   ✅ Essence cost displayed")
                else:
                    print("   ❌ Essence cost not displayed")
            else:
                print("   ❌ Cybereyes not found")
            
            # Check for undefined
            if 'undefined' in modal_html.lower():
                print("   ❌ WARNING: 'undefined' found in cyberware section")
        else:
            print("   ❌ Cyberware section not found")
        
        print("\n5. VALIDATING BIOWARE SECTION:")
        if 'Bioware' in modal_html:
            print("   ✅ Bioware section found")
            # Check for specific bioware items
            if 'Cerebral Booster' in modal_html:
                print("   ✅ Cerebral Booster found")
                if '0.4' in modal_html:
                    print("   ✅ Body Index cost displayed")
                else:
                    print("   ❌ Body Index cost not displayed")
            else:
                print("   ❌ Cerebral Booster not found")
        else:
            print("   ❌ Bioware section not found")
        
        print("\n6. VALIDATING CONTACTS SECTION:")
        if 'Contacts' in modal_html:
            print("   ✅ Contacts section found")
            if 'Colonel Tanner' in modal_html:
                print("   ✅ Colonel Tanner found")
                if 'Military Fixer' in modal_html:
                    print("   ✅ Archetype displayed")
                if 'Loyalty' in modal_html:
                    print("   ✅ Loyalty field displayed")
                if 'Connection' in modal_html:
                    print("   ✅ Connection field displayed")
            else:
                print("   ❌ Colonel Tanner not found")
        else:
            print("   ❌ Contacts section not found")
        
        print("\n7. VALIDATING VEHICLES SECTION:")
        if 'Vehicles' in modal_html:
            print("   ✅ Vehicles section found")
            if 'Eurocar Westwind' in modal_html:
                print("   ✅ Eurocar Westwind found")
                if 'Handling' in modal_html or 'Speed' in modal_html:
                    print("   ✅ Vehicle stats displayed")
                else:
                    print("   ❌ Vehicle stats not displayed")
            else:
                print("   ❌ Eurocar Westwind not found")
        else:
            print("   ❌ Vehicles section not found")
        
        print("\n8. CHECKING FOR COMMON ERRORS:")
        errors = []
        if 'undefined' in modal_html.lower():
            errors.append("Found 'undefined' in page")
        if 'NaN' in modal_html:
            errors.append("Found 'NaN' in page")
        if modal_html.count('null') > 5:
            errors.append("Multiple 'null' values found")
        
        if errors:
            print("   ❌ ERRORS FOUND:")
            for error in errors:
                print(f"      - {error}")
        else:
            print("   ✅ No common errors found")
        
        print("\n9. Keeping browser open for 30 seconds for manual inspection...")
        await asyncio.sleep(30)
        
        await browser.close()
        print("\n" + "="*80)
        print("VALIDATION TEST COMPLETE")
        print("="*80)

if __name__ == "__main__":
    asyncio.run(test_ui_validation())
