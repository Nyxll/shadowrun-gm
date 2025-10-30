#!/usr/bin/env python3
"""
Test character UI display with Playwright to diagnose rendering issues
"""
import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
import time

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_character_ui_display():
    """Test character sheet UI with Playwright to see actual rendering"""
    
    print("\n" + "="*80)
    print("CHARACTER UI DISPLAY TEST")
    print("="*80)
    
    with sync_playwright() as p:
        # Launch browser
        print("\n1. Launching browser...")
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()
        
        # Set viewport
        page.set_viewport_size({"width": 1920, "height": 1080})
        
        try:
            # Navigate to character sheet
            print("\n2. Navigating to http://localhost:5000...")
            page.goto("http://localhost:5000")
            
            # Wait for page to load
            page.wait_for_load_state("networkidle")
            time.sleep(2)
            
            # Take screenshot of initial state
            print("\n3. Taking screenshot of initial page...")
            page.screenshot(path="tests/screenshots/01-initial-page.png")
            
            # Check if character selector exists
            print("\n4. Checking for character selector...")
            selector_exists = page.locator("#character-selector").count() > 0
            print(f"   Character selector exists: {selector_exists}")
            
            if selector_exists:
                # Get available characters
                options = page.locator("#character-selector option").all()
                print(f"\n5. Found {len(options)} character options:")
                for i, option in enumerate(options):
                    value = option.get_attribute("value")
                    text = option.inner_text()
                    print(f"   {i+1}. {text} (value: {value})")
                
                # Select first real character (skip "Select a character")
                if len(options) > 1:
                    first_char_value = options[1].get_attribute("value")
                    print(f"\n6. Selecting character: {first_char_value}")
                    page.select_option("#character-selector", first_char_value)
                    
                    # Wait for character to load
                    time.sleep(3)
                    
                    # Take screenshot after selection
                    print("\n7. Taking screenshot after character selection...")
                    page.screenshot(path="tests/screenshots/02-character-selected.png")
                    
                    # Check what's actually displayed
                    print("\n8. Checking displayed values...")
                    
                    # Character name
                    name_elem = page.locator("#sheet-character-name")
                    if name_elem.count() > 0:
                        name_text = name_elem.inner_text()
                        print(f"   Character Name: '{name_text}'")
                    else:
                        print("   Character Name: NOT FOUND")
                    
                    # Subtitle
                    subtitle_elem = page.locator("#sheet-character-subtitle")
                    if subtitle_elem.count() > 0:
                        subtitle_text = subtitle_elem.inner_text()
                        print(f"   Subtitle: '{subtitle_text}'")
                    else:
                        print("   Subtitle: NOT FOUND")
                    
                    # Check for sections
                    print("\n9. Checking for sheet sections...")
                    sections = page.locator(".sheet-section").all()
                    print(f"   Found {len(sections)} sections")
                    
                    for i, section in enumerate(sections[:5]):  # First 5 sections
                        title_elem = section.locator(".section-title")
                        if title_elem.count() > 0:
                            title = title_elem.inner_text()
                            print(f"   Section {i+1}: {title}")
                            
                            # Check if section has content
                            content_elem = section.locator(".section-content")
                            if content_elem.count() > 0:
                                content_text = content_elem.inner_text()
                                # Show first 100 chars
                                preview = content_text[:100].replace('\n', ' ')
                                print(f"      Content preview: {preview}...")
                    
                    # Check specific attribute values
                    print("\n10. Checking attribute stat boxes...")
                    stat_boxes = page.locator(".stat-box").all()
                    print(f"   Found {len(stat_boxes)} stat boxes")
                    
                    for i, box in enumerate(stat_boxes[:10]):  # First 10
                        label_elem = box.locator(".stat-label")
                        value_elem = box.locator(".stat-value")
                        
                        if label_elem.count() > 0 and value_elem.count() > 0:
                            label = label_elem.inner_text()
                            value = value_elem.inner_text()
                            print(f"   {label}: {value}")
                    
                    # Check console for errors
                    print("\n11. Checking browser console...")
                    console_messages = []
                    
                    def handle_console(msg):
                        console_messages.append(f"   [{msg.type}] {msg.text}")
                    
                    page.on("console", handle_console)
                    
                    # Reload to capture console messages
                    page.reload()
                    time.sleep(2)
                    
                    if console_messages:
                        print("   Console messages:")
                        for msg in console_messages[-10:]:  # Last 10 messages
                            print(msg)
                    else:
                        print("   No console messages")
                    
                    # Take final screenshot
                    print("\n12. Taking final screenshot...")
                    page.screenshot(path="tests/screenshots/03-final-state.png")
                    
                    # Check network requests
                    print("\n13. Checking network activity...")
                    print("   (Monitoring for 5 seconds...)")
                    
                    network_requests = []
                    
                    def handle_request(request):
                        network_requests.append({
                            'url': request.url,
                            'method': request.method
                        })
                    
                    page.on("request", handle_request)
                    time.sleep(5)
                    
                    # Filter for API calls
                    api_calls = [r for r in network_requests if '/api/' in r['url']]
                    if api_calls:
                        print(f"   Found {len(api_calls)} API calls:")
                        for call in api_calls:
                            print(f"   {call['method']} {call['url']}")
                    else:
                        print("   No API calls detected")
                    
                    print("\n" + "="*80)
                    print("TEST COMPLETE")
                    print("="*80)
                    print("\nScreenshots saved to tests/screenshots/")
                    print("- 01-initial-page.png")
                    print("- 02-character-selected.png")
                    print("- 03-final-state.png")
                    print("\nBrowser will remain open for 10 seconds for manual inspection...")
                    time.sleep(10)
                    
            else:
                print("\n   ERROR: Character selector not found!")
                page.screenshot(path="tests/screenshots/error-no-selector.png")
        
        except Exception as e:
            print(f"\n   ERROR: {e}")
            page.screenshot(path="tests/screenshots/error-exception.png")
            raise
        
        finally:
            browser.close()

if __name__ == "__main__":
    # Create screenshots directory
    os.makedirs("tests/screenshots", exist_ok=True)
    
    test_character_ui_display()
