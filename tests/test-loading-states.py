#!/usr/bin/env python3
"""
Test Loading State Functionality
Tests button states and user feedback during operations
"""

import asyncio
import os
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()

# Test configuration
BASE_URL = "http://localhost:8001"
TEST_CHARACTER = "Platinum"


async def test_add_character_loading_state():
    """Test that Add Character button shows loading state"""
    print("\n=== Testing Add Character Loading State ===")
    
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
            
            # Select character
            await page.select_option('#character-select', TEST_CHARACTER)
            print(f"✓ Selected {TEST_CHARACTER}")
            
            # Get initial button text
            initial_text = await page.text_content('#add-character-button')
            print(f"✓ Initial button text: '{initial_text}'")
            
            # Click add button
            await page.click('#add-character-button')
            
            # Immediately check if button is disabled
            await asyncio.sleep(0.1)  # Small delay to let state update
            is_disabled = await page.is_disabled('#add-character-button')
            assert is_disabled, "Button should be disabled during operation"
            print("✓ Button disabled during operation")
            
            # Check button text changed
            loading_text = await page.text_content('#add-character-button')
            assert "Adding" in loading_text or "..." in loading_text, f"Expected loading text, got '{loading_text}'"
            print(f"✓ Button shows loading text: '{loading_text}'")
            
            # Check status message
            status_text = await page.text_content('#status-display')
            assert "Adding" in status_text or TEST_CHARACTER in status_text, f"Expected status update, got '{status_text}'"
            print(f"✓ Status shows: '{status_text}'")
            
            # Wait for operation to complete
            await asyncio.sleep(1.5)
            
            # Verify button is re-enabled
            is_enabled = not await page.is_disabled('#add-character-button')
            assert is_enabled, "Button should be re-enabled after operation"
            print("✓ Button re-enabled after operation")
            
            # Verify button text restored
            final_text = await page.text_content('#add-character-button')
            assert final_text == initial_text, f"Button text should be restored to '{initial_text}', got '{final_text}'"
            print(f"✓ Button text restored: '{final_text}'")
            
            print("\n✓ Add character loading state test passed")
            return True
            
        except Exception as e:
            print(f"✗ Add character loading state test failed: {e}")
            await page.screenshot(path="test-failure-loading-state.png")
            return False
        finally:
            await browser.close()


async def test_duplicate_prevention_during_loading():
    """Test that duplicate additions are prevented during loading"""
    print("\n=== Testing Duplicate Prevention During Loading ===")
    
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
            
            # Select character
            await page.select_option('#character-select', TEST_CHARACTER)
            
            # Click add button
            await page.click('#add-character-button')
            print("✓ Clicked add button")
            
            # Try to click again immediately (should be disabled)
            await asyncio.sleep(0.1)
            is_disabled = await page.is_disabled('#add-character-button')
            assert is_disabled, "Button should be disabled, preventing duplicate clicks"
            print("✓ Button disabled, preventing duplicate clicks")
            
            # Wait for operation to complete
            await asyncio.sleep(1.5)
            
            # Try to add same character again (should show error)
            await page.select_option('#character-select', TEST_CHARACTER)
            await page.click('#add-character-button')
            await asyncio.sleep(0.5)
            
            # Check for duplicate prevention message
            messages = await page.text_content('#messages')
            assert "already" in messages.lower(), "Should show duplicate prevention message"
            print("✓ Duplicate prevention message shown")
            
            # Verify only one instance in character list
            char_elements = await page.query_selector_all(f'.character-name:has-text("{TEST_CHARACTER}")')
            assert len(char_elements) == 1, f"Expected 1 character, found {len(char_elements)}"
            print("✓ Only one instance of character in list")
            
            print("\n✓ Duplicate prevention test passed")
            return True
            
        except Exception as e:
            print(f"✗ Duplicate prevention test failed: {e}")
            await page.screenshot(path="test-failure-duplicate-prevention.png")
            return False
        finally:
            await browser.close()


async def test_status_display_updates():
    """Test that status display updates correctly during operations"""
    print("\n=== Testing Status Display Updates ===")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # Navigate and connect
            await page.goto(BASE_URL)
            await page.wait_for_load_state("networkidle")
            await page.wait_for_selector('#connection-status:has-text("Connected")', timeout=5000)
            print("✓ Page loaded and connected")
            
            # Check initial status
            await page.wait_for_selector('#character-select option:not([value=""])', timeout=5000)
            status = await page.text_content('#status-display')
            assert "loaded" in status.lower() or "ready" in status.lower(), f"Expected ready status, got '{status}'"
            print(f"✓ Initial status: '{status}'")
            
            # Select and add character
            await page.select_option('#character-select', TEST_CHARACTER)
            await page.click('#add-character-button')
            
            # Check status during operation
            await asyncio.sleep(0.2)
            loading_status = await page.text_content('#status-display')
            assert "adding" in loading_status.lower() or TEST_CHARACTER in loading_status, f"Expected loading status, got '{loading_status}'"
            print(f"✓ Loading status: '{loading_status}'")
            
            # Wait for completion
            await asyncio.sleep(1.5)
            
            # Check final status
            final_status = await page.text_content('#status-display')
            assert "ready" in final_status.lower(), f"Expected ready status, got '{final_status}'"
            print(f"✓ Final status: '{final_status}'")
            
            print("\n✓ Status display updates test passed")
            return True
            
        except Exception as e:
            print(f"✗ Status display updates test failed: {e}")
            await page.screenshot(path="test-failure-status-display.png")
            return False
        finally:
            await browser.close()


async def run_all_tests():
    """Run all loading state tests"""
    print("=" * 60)
    print("LOADING STATES - TEST SUITE")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(await test_add_character_loading_state())
    results.append(await test_duplicate_prevention_during_loading())
    results.append(await test_status_display_updates())
    
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
