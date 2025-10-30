#!/usr/bin/env python3
"""
Test what's ACTUALLY displaying in the browser
"""
from playwright.sync_api import sync_playwright
import time

def test_actual_display():
    print("="*80)
    print("CHECKING ACTUAL BROWSER DISPLAY")
    print("="*80)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # Load character sheet
        page.goto('http://localhost:8001')
        time.sleep(2)
        
        # Wait for character select to load
        page.wait_for_selector('select#character-select')
        time.sleep(2)  # Give it time to populate
        
        # Select Platinum by real name (option value is char.name, not street_name)
        page.select_option('select#character-select', value='Kent Jefferies')
        time.sleep(1)
        
        # Click VIEW SHEET button
        page.click('button#view-sheet-button')
        time.sleep(2)
        
        print("\n1. CHECKING ESSENCE DISPLAY:")
        essence_section = page.locator('.stat-group:has-text("Essence")').inner_html()
        print(essence_section)
        
        print("\n2. CHECKING BODY INDEX DISPLAY:")
        try:
            body_index_section = page.locator('.stat-group:has-text("Body Index")').inner_html()
            print(body_index_section)
        except:
            print("❌ Body Index section NOT FOUND")
        
        print("\n3. CHECKING CYBERWARE SECTION:")
        cyber_section = page.locator('#cyberwareList').inner_html()
        print(cyber_section[:500])  # First 500 chars
        
        print("\n4. CHECKING BIOWARE SECTION:")
        bio_section = page.locator('#biowareList').inner_html()
        print(bio_section[:500])  # First 500 chars
        
        print("\n5. CHECKING EDGES/FLAWS:")
        try:
            edges_section = page.locator('.section:has-text("Edges")').inner_html()
            print("Edges found:", edges_section[:200])
        except:
            print("❌ Edges section NOT FOUND")
        
        try:
            flaws_section = page.locator('.section:has-text("Flaws")').inner_html()
            print("Flaws found:", flaws_section[:200])
        except:
            print("❌ Flaws section NOT FOUND")
        
        print("\n6. CHECKING NOTES FIELD:")
        try:
            notes = page.locator('textarea[name="notes"]').input_value()
            print(f"Notes: {notes[:200] if notes else 'EMPTY'}")
        except:
            print("❌ Notes field NOT FOUND")
        
        # Take screenshot
        page.screenshot(path='screenshots/actual-display.png', full_page=True)
        print("\n📸 Screenshot saved: screenshots/actual-display.png")
        
        print("\nKeeping browser open for 60 seconds...")
        time.sleep(60)
        
        browser.close()

if __name__ == "__main__":
    test_actual_display()
