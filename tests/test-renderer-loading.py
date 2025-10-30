#!/usr/bin/env python3
"""
Test that character-sheet-renderer.js loads properly and CharacterSheetRenderer is defined
"""
import asyncio
from playwright.async_api import async_playwright

async def test_renderer_loading():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # Navigate to the page
        await page.goto('http://localhost:8001')
        
        # Wait for page to load
        await page.wait_for_load_state('networkidle')
        
        # Check if CharacterSheetRenderer is defined
        is_defined = await page.evaluate('typeof CharacterSheetRenderer !== "undefined"')
        
        print(f"CharacterSheetRenderer defined: {is_defined}")
        
        if not is_defined:
            # Get any console errors
            console_messages = []
            page.on('console', lambda msg: console_messages.append(f"{msg.type}: {msg.text}"))
            
            # Try to load the script manually to see errors
            try:
                await page.evaluate('console.log("Testing...")')
                await asyncio.sleep(1)
            except Exception as e:
                print(f"Error: {e}")
            
            print("\nConsole messages:")
            for msg in console_messages:
                print(f"  {msg}")
            
            # Check if script loaded
            script_loaded = await page.evaluate('''
                Array.from(document.scripts).some(s => s.src.includes('character-sheet-renderer'))
            ''')
            print(f"\nScript tag found: {script_loaded}")
            
            # Get script content to check for syntax errors
            script_content = await page.evaluate('''
                Array.from(document.scripts)
                    .find(s => s.src.includes('character-sheet-renderer'))
                    ?.src || 'not found'
            ''')
            print(f"Script src: {script_content}")
        
        await browser.close()
        
        return is_defined

if __name__ == "__main__":
    result = asyncio.run(test_renderer_loading())
    if result:
        print("\n✓ CharacterSheetRenderer is properly defined")
    else:
        print("\n✗ CharacterSheetRenderer is NOT defined - there's a problem")
        exit(1)
