#!/usr/bin/env python3
"""
Debug UI loading issues
"""
import asyncio
from playwright.async_api import async_playwright

async def test_ui():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Enable console logging
        page.on("console", lambda msg: print(f"CONSOLE: {msg.text}"))
        page.on("pageerror", lambda err: print(f"PAGE ERROR: {err}"))
        
        print("Navigating to http://localhost:8001...")
        await page.goto("http://localhost:8001")
        
        print("Waiting 5 seconds...")
        await asyncio.sleep(5)
        
        # Check what's on the page
        html = await page.content()
        print(f"\nPage HTML length: {len(html)}")
        
        # Check for specific elements
        title = await page.title()
        print(f"Page title: {title}")
        
        # Check if app.js loaded
        scripts = await page.query_selector_all("script")
        print(f"\nScripts found: {len(scripts)}")
        for script in scripts:
            src = await script.get_attribute("src")
            if src:
                print(f"  - {src}")
        
        # Check for errors in console
        print("\nWaiting for any async operations...")
        await asyncio.sleep(3)
        
        # Take screenshot
        await page.screenshot(path="tests/screenshots/ui-debug.png")
        print("\nScreenshot saved to tests/screenshots/ui-debug.png")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_ui())
