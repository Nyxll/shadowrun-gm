#!/usr/bin/env python3
"""
Test Character Removal Functionality
Tests the remove_character WebSocket message and UI behavior
"""

import asyncio
import os
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()

# Test configuration
BASE_URL = "http://localhost:8001"
TEST_CHARACTER_1 = "Platinum"
TEST_CHARACTER_2 = "Block"


async def test_character_removal_before_scenario():
    """Test that characters can be removed before scenario starts"""
    print("\n=== Testing Character Removal Before Scenario ===")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # Navigate and connect
            await page.goto(BASE_URL)
            await page.wait_for_load_state("networkidle")
            await page.wait_for_selector('#connection-status:has-text("Connected")', timeout=5000)
            await page.wait_for_selector('#character-select option:not([value=""])', timeout=5000)
            print("✓ Page loaded and connected")
            
            # Add first character
            await page.select_option('#character-select', TEST_CHARACTER_1)
            await page.click('#add-character-button')
            await asyncio.sleep(1.5)
            print(f"✓ Added {TEST_CHARACTER_1}")
            
            # Verify character appears
            char1 = await page.query_selector(f'.character-name:has-text("{TEST_CHARACTER_1}")')
            assert char1 is not None, f"{TEST_CHARACTER_1} not found in list"
            print(f"✓ {TEST_CHARACTER_1} appears in list")
            
            # Verify remove button exists
            remove_btn = await page.query_selector('.character-remove')
            assert remove_btn is not None, "Remove button not found"
            print("✓ Remove button visible")
            
            # Click remove button
            await remove_btn.click()
            await asyncio.sleep(0.5)
            print("✓ Clicked remove button")
            
            # Verify character is removed
            char1_after = await page.query_selector(f'.character-name:has-text("{TEST_CHARACTER_1}")')
            assert char1_after is None, f"{TEST_CHARACTER_1} still in list after removal"
            print(f"✓ {TEST_CHARACTER_1} removed from list")
            
            # Verify system message
            messages = await page.text_content('#messages')
            assert "Removed" in messages and TEST_CHARACTER_1 in messages, "No removal confirmation message"
            print("✓ Removal confirmation message displayed")
            
            print("\n✓ Character removal test passed")
            return True
            
        except Exception as e:
            print(f"✗ Character removal test failed: {e}")
            await page.screenshot(path="test-failure-character-removal.png")
            return False
        finally:
            await browser.close()


async def test_remove_button_hidden_after_scenario():
    """Test that remove buttons are hidden after scenario starts"""
    print("\n=== Testing Remove Button Hidden After Scenario ===")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # Navigate and connect
            await page.goto(BASE_URL)
            await page.wait_for_load_state("networkidle")
            await page.wait_for_selector('#connection-status:has-text("Connected")', timeout=5000)
            await page.wait_for_selector('#character-select option:not([value=""])', timeout=5000)
            print("✓ Page loaded and connected")
            
            # Add character
            await page.select_option('#character-select', TEST_CHARACTER_1)
            await page.click('#add-character-button')
            await asyncio.sleep(1.5)
            print(f"✓ Added {TEST_CHARACTER_1}")
            
            # Verify remove button exists before scenario
            remove_btn_before = await page.query_selector('.character-remove')
            assert remove_btn_before is not None, "Remove button not found before scenario"
            print("✓ Remove button visible before scenario")
            
            # Start scenario
            await page.click('#create-scenario-button')
            await asyncio.sleep(0.5)
            print("✓ Started scenario")
            
            # Verify remove button is hidden after scenario
            remove_btn_after = await page.query_selector('.character-remove')
            assert remove_btn_after is None, "Remove button still visible after scenario"
            print("✓ Remove button hidden after scenario")
            
            print("\n✓ Remove button hiding test passed")
            return True
            
        except Exception as e:
            print(f"✗ Remove button hiding test failed: {e}")
            await page.screenshot(path="test-failure-remove-button-hiding.png")
            return False
        finally:
            await browser.close()


async def test_multiple_character_removal():
    """Test removing multiple characters"""
    print("\n=== Testing Multiple Character Removal ===")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # Navigate and connect
            await page.goto(BASE_URL)
            await page.wait_for_load_state("networkidle")
            await page.wait_for_selector('#connection-status:has-text("Connected")', timeout=5000)
            await page.wait_for_selector('#character-select option:not([value=""])', timeout=5000)
            print("✓ Page loaded and connected")
            
            # Add first character
            await page.select_option('#character-select', TEST_CHARACTER_1)
            await page.click('#add-character-button')
            await asyncio.sleep(1.5)
            print(f"✓ Added {TEST_CHARACTER_1}")
            
            # Add second character
            await page.select_option('#character-select', TEST_CHARACTER_2)
            await page.click('#add-character-button')
            await asyncio.sleep(1.5)
            print(f"✓ Added {TEST_CHARACTER_2}")
            
            # Verify both characters appear
            char1 = await page.query_selector(f'.character-name:has-text("{TEST_CHARACTER_1}")')
            char2 = await page.query_selector(f'.character-name:has-text("{TEST_CHARACTER_2}")')
            assert char1 is not None and char2 is not None, "Not all characters in list"
            print("✓ Both characters in list")
            
            # Get all remove buttons
            remove_buttons = await page.query_selector_all('.character-remove')
            assert len(remove_buttons) == 2, f"Expected 2 remove buttons, found {len(remove_buttons)}"
            print("✓ Two remove buttons present")
            
            # Remove first character
            await remove_buttons[0].click()
            await asyncio.sleep(0.5)
            print(f"✓ Removed first character")
            
            # Verify only one character remains
            remaining_chars = await page.query_selector_all('.character-name')
            assert len(remaining_chars) == 1, f"Expected 1 character, found {len(remaining_chars)}"
            print("✓ One character remains")
            
            # Remove second character
            remaining_remove_btn = await page.query_selector('.character-remove')
            await remaining_remove_btn.click()
            await asyncio.sleep(0.5)
            print(f"✓ Removed second character")
            
            # Verify no characters remain
            final_chars = await page.query_selector_all('.character-name')
            assert len(final_chars) == 0, f"Expected 0 characters, found {len(final_chars)}"
            print("✓ No characters remain")
            
            print("\n✓ Multiple character removal test passed")
            return True
            
        except Exception as e:
            print(f"✗ Multiple character removal test failed: {e}")
            await page.screenshot(path="test-failure-multiple-removal.png")
            return False
        finally:
            await browser.close()


async def run_all_tests():
    """Run all character removal tests"""
    print("=" * 60)
    print("CHARACTER REMOVAL - TEST SUITE")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(await test_character_removal_before_scenario())
    results.append(await test_remove_button_hidden_after_scenario())
    results.append(await test_multiple_character_removal())
    
    # Summary
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"RESULTS: {passed} passed, {total - passed} failed, {total} total")
    print("=" * 60)
    
    return all(results)


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)
