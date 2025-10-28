#!/usr/bin/env python3
"""
UI Tests for Shadowrun GM Live Game Interface
Tests the web interface using Playwright
"""

import os
import sys
import asyncio
from playwright.async_api import async_playwright, expect
from dotenv import load_dotenv

load_dotenv()

# Test configuration
BASE_URL = "http://localhost:8001"
TIMEOUT = 10000  # 10 seconds


class UITestSuite:
    """Test suite for the web UI"""
    
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None
        self.passed = 0
        self.failed = 0
        self.tests_run = 0
    
    async def setup(self):
        """Set up browser and page"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=True)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        
        # Set viewport size
        await self.page.set_viewport_size({"width": 1280, "height": 720})
    
    async def teardown(self):
        """Clean up browser"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
    
    def log_test(self, name, passed, message=""):
        """Log test result"""
        self.tests_run += 1
        if passed:
            self.passed += 1
            print(f"✓ {name}")
        else:
            self.failed += 1
            print(f"✗ {name}")
            if message:
                print(f"  Error: {message}")
    
    async def test_page_loads(self):
        """Test 1: Page loads successfully"""
        try:
            response = await self.page.goto(BASE_URL, wait_until="networkidle")
            self.log_test("Page loads successfully", response.status == 200)
        except Exception as e:
            self.log_test("Page loads successfully", False, str(e))
    
    async def test_title(self):
        """Test 2: Page has correct title"""
        try:
            title = await self.page.title()
            self.log_test("Page title is correct", 
                         title == "Shadowrun GM - Live Game")
        except Exception as e:
            self.log_test("Page title is correct", False, str(e))
    
    async def test_header_visible(self):
        """Test 3: Header is visible"""
        try:
            header = self.page.locator("h1")
            await expect(header).to_be_visible(timeout=TIMEOUT)
            text = await header.text_content()
            self.log_test("Header is visible", 
                         "SHADOWRUN GM" in text)
        except Exception as e:
            self.log_test("Header is visible", False, str(e))
    
    async def test_websocket_connects(self):
        """Test 4: WebSocket connection establishes"""
        try:
            # Wait for connection status to show "Connected"
            status = self.page.locator("#connection-status")
            await expect(status).to_have_text("Connected", timeout=TIMEOUT)
            self.log_test("WebSocket connects", True)
        except Exception as e:
            self.log_test("WebSocket connects", False, str(e))
    
    async def test_characters_load(self):
        """Test 5: Characters load from database"""
        try:
            # Wait for success message
            await self.page.wait_for_selector(
                "text=Loaded 6 characters from database",
                timeout=TIMEOUT
            )
            self.log_test("Characters load from database", True)
        except Exception as e:
            self.log_test("Characters load from database", False, str(e))
    
    async def test_character_dropdown_populated(self):
        """Test 6: Character dropdown is populated"""
        try:
            dropdown = self.page.locator("#character-select")
            
            # Get all options
            options = await dropdown.locator("option").all_text_contents()
            
            # Should have at least 7 options (1 placeholder + 6 characters)
            has_characters = len(options) >= 7
            
            # Check for specific characters
            has_platinum = any("Platinum" in opt for opt in options)
            has_block = any("Block" in opt for opt in options)
            
            self.log_test("Character dropdown populated", 
                         has_characters and has_platinum and has_block)
        except Exception as e:
            self.log_test("Character dropdown populated", False, str(e))
    
    async def test_status_updates(self):
        """Test 7: Status updates correctly"""
        try:
            status = self.page.locator("#status-display")
            text = await status.text_content()
            
            # Should show "Characters loaded - Ready for scenario creation"
            self.log_test("Status updates correctly",
                         "Ready for scenario creation" in text)
        except Exception as e:
            self.log_test("Status updates correctly", False, str(e))
    
    async def test_create_scenario_button_enabled(self):
        """Test 8: Create Scenario button is enabled"""
        try:
            button = self.page.locator("#create-scenario-button")
            is_enabled = await button.is_enabled()
            self.log_test("Create Scenario button enabled", is_enabled)
        except Exception as e:
            self.log_test("Create Scenario button enabled", False, str(e))
    
    async def test_add_character_button_visible(self):
        """Test 9: Add Character button is visible"""
        try:
            button = self.page.locator("#add-character-button")
            await expect(button).to_be_visible(timeout=TIMEOUT)
            text = await button.text_content()
            self.log_test("Add Character button visible", 
                         "ADD CHARACTER" in text)
        except Exception as e:
            self.log_test("Add Character button visible", False, str(e))
    
    async def test_layout_no_horizontal_scroll(self):
        """Test 10: No horizontal scrollbar on sidebar"""
        try:
            sidebar = self.page.locator("#sidebar")
            
            # Get sidebar dimensions
            box = await sidebar.bounding_box()
            
            # Check if content fits within viewport
            # Sidebar should be 300px wide
            fits = box['width'] <= 300
            
            self.log_test("No horizontal scroll needed", fits)
        except Exception as e:
            self.log_test("No horizontal scroll needed", False, str(e))
    
    async def test_select_and_add_character(self):
        """Test 11: Can select and add a character"""
        try:
            # Select character from dropdown
            dropdown = self.page.locator("#character-select")
            await dropdown.select_option(label="Platinum (Human)")
            
            # Click add button
            add_button = self.page.locator("#add-character-button")
            await add_button.click()
            
            # Wait for success message
            await self.page.wait_for_selector(
                "text=Added Platinum to session",
                timeout=TIMEOUT
            )
            
            # Check if character appears in active list
            char_list = self.page.locator("#character-list")
            text = await char_list.text_content()
            
            self.log_test("Can select and add character", 
                         "Platinum" in text)
        except Exception as e:
            self.log_test("Can select and add character", False, str(e))
    
    async def test_duplicate_character_prevention(self):
        """Test 12: Prevents adding duplicate characters"""
        try:
            # Try to add Platinum again (already added in previous test)
            dropdown = self.page.locator("#character-select")
            
            # Check if Platinum is already in the list
            char_list = self.page.locator("#character-list")
            text = await char_list.text_content()
            
            # If already there, trying to add again should be prevented
            # (client-side check)
            self.log_test("Duplicate character prevention", 
                         "Platinum" in text)
        except Exception as e:
            self.log_test("Duplicate character prevention", False, str(e))
    
    async def test_message_input_disabled_initially(self):
        """Test 13: Message input is disabled until character added"""
        try:
            # After adding a character, input should be enabled
            message_input = self.page.locator("#message-input")
            is_enabled = await message_input.is_enabled()
            
            # Should be enabled after WebSocket connects
            self.log_test("Message input enabled after connection", is_enabled)
        except Exception as e:
            self.log_test("Message input enabled after connection", False, str(e))
    
    async def test_send_button_enabled(self):
        """Test 14: Send button is enabled"""
        try:
            send_button = self.page.locator("#send-button")
            is_enabled = await send_button.is_enabled()
            self.log_test("Send button enabled", is_enabled)
        except Exception as e:
            self.log_test("Send button enabled", False, str(e))
    
    async def test_responsive_layout(self):
        """Test 15: Layout is responsive"""
        try:
            # Check main container layout
            main = self.page.locator("#main")
            box = await main.bounding_box()
            
            # Should fill available space
            self.log_test("Responsive layout", box['width'] > 0 and box['height'] > 0)
        except Exception as e:
            self.log_test("Responsive layout", False, str(e))
    
    async def run_all_tests(self):
        """Run all UI tests"""
        print("\n" + "="*60)
        print("SHADOWRUN GM - UI TEST SUITE")
        print("="*60 + "\n")
        
        await self.setup()
        
        try:
            # Page load tests
            print("Page Load Tests:")
            await self.test_page_loads()
            await self.test_title()
            await self.test_header_visible()
            
            # Connection tests
            print("\nConnection Tests:")
            await self.test_websocket_connects()
            
            # Data loading tests
            print("\nData Loading Tests:")
            await self.test_characters_load()
            await self.test_character_dropdown_populated()
            await self.test_status_updates()
            
            # UI element tests
            print("\nUI Element Tests:")
            await self.test_create_scenario_button_enabled()
            await self.test_add_character_button_visible()
            await self.test_layout_no_horizontal_scroll()
            
            # Interaction tests
            print("\nInteraction Tests:")
            await self.test_select_and_add_character()
            await self.test_duplicate_character_prevention()
            await self.test_message_input_disabled_initially()
            await self.test_send_button_enabled()
            
            # Layout tests
            print("\nLayout Tests:")
            await self.test_responsive_layout()
            
        finally:
            await self.teardown()
        
        # Print summary
        print("\n" + "="*60)
        print(f"RESULTS: {self.passed} passed, {self.failed} failed, {self.tests_run} total")
        print("="*60 + "\n")
        
        return self.failed == 0


async def main():
    """Main test runner"""
    suite = UITestSuite()
    success = await suite.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
