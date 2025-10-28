#!/usr/bin/env python3
"""
Test Character Sheet Viewing Functionality
Tests the /api/character/{name} endpoint and modal display
"""

import asyncio
import os
from dotenv import load_dotenv
from playwright.async_api import async_playwright, expect

load_dotenv()

# Test configuration
BASE_URL = "http://localhost:8001"
TEST_CHARACTER = "Platinum"  # Known character in database

async def test_character_sheet_endpoint():
    """Test that character sheet API endpoint returns correct data"""
    print("\n=== Testing Character Sheet API Endpoint ===")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # Test API endpoint directly
            print(f"Testing GET /api/character/{TEST_CHARACTER}")
            response = await page.request.get(f"{BASE_URL}/api/character/{TEST_CHARACTER}")
            
            assert response.status == 200, f"Expected 200, got {response.status}"
            print("✓ API returns 200 OK")
            
            data = await response.json()
            
            # Verify response structure
            assert "id" in data, "Response missing 'id' field"
            assert "name" in data, "Response missing 'name' field"
            assert "attributes" in data, "Response missing 'attributes' field"
            assert "skills" in data, "Response missing 'skills' field"
            assert "weapons" in data, "Response missing 'weapons' field"
            assert "armor" in data, "Response missing 'armor' field"
            assert "equipment" in data, "Response missing 'equipment' field"
            print("✓ Response has correct structure")
            
            # Verify attributes
            attributes = data["attributes"]
            assert isinstance(attributes, dict), "Attributes should be a dict"
            print(f"✓ Attributes: {list(attributes.keys())}")
            
            # Verify skills
            skills = data["skills"]
            assert isinstance(skills, dict), "Skills should be a dict"
            if "active" in skills:
                print(f"✓ Active skills count: {len(skills['active'])}")
            if "knowledge" in skills:
                print(f"✓ Knowledge skills count: {len(skills['knowledge'])}")
            if "language" in skills:
                print(f"✓ Language skills count: {len(skills['language'])}")
            
            # Verify gear
            weapons = data["weapons"]
            assert isinstance(weapons, list), "Weapons should be a list"
            print(f"✓ Weapons count: {len(weapons)}")
            
            armor = data["armor"]
            assert isinstance(armor, list), "Armor should be a list"
            print(f"✓ Armor count: {len(armor)}")
            
            equipment = data["equipment"]
            assert isinstance(equipment, list), "Equipment should be a list"
            print(f"✓ Equipment count: {len(equipment)}")
            
            print(f"\n✓ Character sheet API test passed for {TEST_CHARACTER}")
            return True
            
        except Exception as e:
            print(f"✗ Character sheet API test failed: {e}")
            return False
        finally:
            await browser.close()


async def test_character_sheet_modal():
    """Test that clicking character name opens modal with correct data"""
    print("\n=== Testing Character Sheet Modal Display ===")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # Navigate to page
            await page.goto(BASE_URL)
            await page.wait_for_load_state("networkidle")
            print("✓ Page loaded")
            
            # Wait for WebSocket connection
            await page.wait_for_selector('#connection-status:has-text("Connected")', timeout=5000)
            print("✓ WebSocket connected")
            
            # Wait for characters to load
            await page.wait_for_selector('#character-select option:not([value=""])', timeout=5000)
            print("✓ Characters loaded")
            
            # Add test character
            await page.select_option('#character-select', TEST_CHARACTER)
            await page.click('#add-character-button')
            await asyncio.sleep(1.5)  # Wait for character to be added
            print(f"✓ Added {TEST_CHARACTER} to session")
            
            # Verify character appears in list
            character_name = await page.wait_for_selector(f'.character-name:has-text("{TEST_CHARACTER}")', timeout=3000)
            assert character_name is not None, f"Character {TEST_CHARACTER} not found in list"
            print(f"✓ {TEST_CHARACTER} appears in character list")
            
            # Click character name to open modal
            await character_name.click()
            await asyncio.sleep(0.5)
            print("✓ Clicked character name")
            
            # Verify modal is visible
            modal = await page.wait_for_selector('#character-sheet-modal.active', timeout=3000)
            assert modal is not None, "Modal did not open"
            print("✓ Modal opened")
            
            # Verify modal content
            modal_content = await page.text_content('#character-sheet-content')
            assert TEST_CHARACTER in modal_content or "Platinum" in modal_content, "Character name not in modal"
            print("✓ Modal contains character name")
            
            # Check for attributes section
            attributes_heading = await page.query_selector('#character-sheet-content h3:has-text("Attributes")')
            assert attributes_heading is not None, "Attributes section not found"
            print("✓ Attributes section present")
            
            # Check for stat grid
            stat_grid = await page.query_selector('.stat-grid')
            assert stat_grid is not None, "Stat grid not found"
            print("✓ Stat grid present")
            
            # Check for skills section (if character has skills)
            skills_heading = await page.query_selector('#character-sheet-content h3:has-text("Skills")')
            if skills_heading:
                print("✓ Skills section present")
            
            # Close modal by clicking close button
            await page.click('#modal-close-button')
            await asyncio.sleep(0.3)
            print("✓ Clicked close button")
            
            # Verify modal is closed
            modal_closed = await page.query_selector('#character-sheet-modal:not(.active)')
            assert modal_closed is not None, "Modal did not close"
            print("✓ Modal closed")
            
            print(f"\n✓ Character sheet modal test passed")
            return True
            
        except Exception as e:
            print(f"✗ Character sheet modal test failed: {e}")
            # Take screenshot on failure
            await page.screenshot(path="test-failure-character-sheet.png")
            print("Screenshot saved to test-failure-character-sheet.png")
            return False
        finally:
            await browser.close()


async def test_character_sheet_error_handling():
    """Test that non-existent character returns proper error"""
    print("\n=== Testing Character Sheet Error Handling ===")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # Test with non-existent character
            fake_character = "NonExistentCharacter123"
            print(f"Testing GET /api/character/{fake_character}")
            response = await page.request.get(f"{BASE_URL}/api/character/{fake_character}")
            
            assert response.status == 404, f"Expected 404 for non-existent character, got {response.status}"
            print("✓ Returns 404 for non-existent character")
            
            data = await response.json()
            assert "detail" in data, "Error response should have 'detail' field"
            print(f"✓ Error message: {data['detail']}")
            
            print(f"\n✓ Error handling test passed")
            return True
            
        except Exception as e:
            print(f"✗ Error handling test failed: {e}")
            return False
        finally:
            await browser.close()


async def run_all_tests():
    """Run all character sheet tests"""
    print("=" * 60)
    print("CHARACTER SHEET VIEWING - TEST SUITE")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(await test_character_sheet_endpoint())
    results.append(await test_character_sheet_modal())
    results.append(await test_character_sheet_error_handling())
    
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
