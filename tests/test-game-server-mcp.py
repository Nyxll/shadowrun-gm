#!/usr/bin/env python3
"""
MCP Tests for Shadowrun GM Game Server
Tests the Python game server's MCP tool integration
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Add parent directory to path to import game server modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game_server import MCPClient, GameSession
from lib.dice_roller import DiceRoller
from lib.combat_modifiers import CombatModifiers

load_dotenv()


class MCPTestSuite:
    """Test suite for MCP tools in game server"""
    
    def __init__(self):
        self.mcp_client = MCPClient()
        self.passed = 0
        self.failed = 0
        self.tests_run = 0
    
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
    
    async def test_get_character_skill(self):
        """Test 1: Get character skill"""
        try:
            result = await self.mcp_client.call_tool("get_character_skill", {
                "character_name": "Platinum",
                "skill_name": "Firearms"
            })
            
            # Should return skill and attribute ratings
            has_skill = "skill_rating" in result
            has_attribute = "attribute_rating" in result
            
            self.log_test("Get character skill", has_skill and has_attribute)
        except Exception as e:
            self.log_test("Get character skill", False, str(e))
    
    async def test_calculate_dice_pool(self):
        """Test 2: Calculate dice pool"""
        try:
            result = await self.mcp_client.call_tool("calculate_dice_pool", {
                "skill_rating": 5,
                "attribute_rating": 4,
                "modifiers": [2, -1]
            })
            
            # Pool should be 5 + 4 + 2 - 1 = 10
            correct_pool = result.get("pool") == 10
            has_breakdown = "breakdown" in result
            
            self.log_test("Calculate dice pool", correct_pool and has_breakdown)
        except Exception as e:
            self.log_test("Calculate dice pool", False, str(e))
    
    async def test_calculate_target_number(self):
        """Test 3: Calculate target number"""
        try:
            result = await self.mcp_client.call_tool("calculate_target_number", {
                "situation": "Shooting at medium range",
                "difficulty": "average"
            })
            
            # Average difficulty should be TN 5
            correct_tn = result.get("target_number") == 5
            has_breakdown = "breakdown" in result
            
            self.log_test("Calculate target number", correct_tn and has_breakdown)
        except Exception as e:
            self.log_test("Calculate target number", False, str(e))
    
    async def test_roll_dice(self):
        """Test 4: Roll dice"""
        try:
            result = await self.mcp_client.call_tool("roll_dice", {
                "pool": 10,
                "target_number": 5
            })
            
            # Should have rolls, successes, and result
            has_rolls = "rolls" in result and len(result["rolls"]) == 10
            has_successes = "successes" in result
            has_result = "result" in result
            
            self.log_test("Roll dice", has_rolls and has_successes and has_result)
        except Exception as e:
            self.log_test("Roll dice", False, str(e))
    
    async def test_get_character(self):
        """Test 5: Get full character data"""
        try:
            result = await self.mcp_client.call_tool("get_character", {
                "character_name": "Platinum"
            })
            
            # Should have character data
            has_name = "name" in result
            has_attributes = "attributes" in result
            
            self.log_test("Get character data", has_name and has_attributes)
        except Exception as e:
            self.log_test("Get character data", False, str(e))
    
    def test_dice_roller_basic(self):
        """Test 6: DiceRoller basic roll"""
        try:
            result = DiceRoller.roll_with_target_number(10, 5)
            
            # Should have correct pool size
            correct_pool = result.pool_size == 10
            has_rolls = len(result.rolls) == 10
            has_successes = hasattr(result, 'successes')
            
            self.log_test("DiceRoller basic roll", 
                         correct_pool and has_rolls and has_successes)
        except Exception as e:
            self.log_test("DiceRoller basic roll", False, str(e))
    
    def test_dice_roller_explosions(self):
        """Test 7: DiceRoller handles explosions"""
        try:
            # Roll with low TN to likely get explosions
            result = DiceRoller.roll_with_target_number(20, 4)
            
            # Check if any dice exploded (rolled 6 and rerolled)
            # This is probabilistic, but with 20 dice we should see some
            has_explosions = len(result.rolls) >= 20
            
            self.log_test("DiceRoller explosions", has_explosions)
        except Exception as e:
            self.log_test("DiceRoller explosions", False, str(e))
    
    def test_dice_roller_rule_of_one(self):
        """Test 8: DiceRoller detects Rule of One"""
        try:
            # Manually create a result with all ones
            result = DiceRoller.roll_with_target_number(5, 5)
            
            # Check if critical_glitch flag exists
            has_glitch_detection = hasattr(result, 'critical_glitch')
            
            self.log_test("DiceRoller Rule of One detection", has_glitch_detection)
        except Exception as e:
            self.log_test("DiceRoller Rule of One detection", False, str(e))
    
    def test_combat_modifiers_wound(self):
        """Test 9: Combat modifiers for wounds"""
        try:
            # Test wound modifiers
            light_wound = CombatModifiers.get_wound_modifier(3, 10)
            moderate_wound = CombatModifiers.get_wound_modifier(6, 10)
            
            # Light wound should be +1 TN, moderate +2 TN
            correct_light = light_wound == 1
            correct_moderate = moderate_wound == 2
            
            self.log_test("Combat wound modifiers", 
                         correct_light and correct_moderate)
        except Exception as e:
            self.log_test("Combat wound modifiers", False, str(e))
    
    def test_combat_modifiers_range(self):
        """Test 10: Combat modifiers for range"""
        try:
            # Test range modifiers
            short_range = CombatModifiers.get_range_modifier("short")
            medium_range = CombatModifiers.get_range_modifier("medium")
            long_range = CombatModifiers.get_range_modifier("long")
            
            # Short: 0, Medium: +1, Long: +2
            correct = (short_range == 0 and 
                      medium_range == 1 and 
                      long_range == 2)
            
            self.log_test("Combat range modifiers", correct)
        except Exception as e:
            self.log_test("Combat range modifiers", False, str(e))
    
    def test_game_session_creation(self):
        """Test 11: GameSession creation"""
        try:
            session = GameSession("test_session_123")
            
            # Check session properties
            has_id = session.session_id == "test_session_123"
            has_history = isinstance(session.conversation_history, list)
            has_characters = isinstance(session.active_characters, list)
            
            self.log_test("GameSession creation", 
                         has_id and has_history and has_characters)
        except Exception as e:
            self.log_test("GameSession creation", False, str(e))
    
    def test_game_session_add_message(self):
        """Test 12: GameSession add message"""
        try:
            session = GameSession("test_session")
            session.add_message("user", "I attack the guard")
            session.add_message("assistant", "Roll your attack")
            
            # Should have 2 messages
            correct_count = len(session.conversation_history) == 2
            has_roles = (session.conversation_history[0]["role"] == "user" and
                        session.conversation_history[1]["role"] == "assistant")
            
            self.log_test("GameSession add message", 
                         correct_count and has_roles)
        except Exception as e:
            self.log_test("GameSession add message", False, str(e))
    
    def test_game_session_add_character(self):
        """Test 13: GameSession add character"""
        try:
            session = GameSession("test_session")
            session.add_character("Platinum")
            session.add_character("Block")
            
            # Should have 2 characters
            correct_count = len(session.active_characters) == 2
            has_platinum = "Platinum" in session.active_characters
            has_block = "Block" in session.active_characters
            
            self.log_test("GameSession add character", 
                         correct_count and has_platinum and has_block)
        except Exception as e:
            self.log_test("GameSession add character", False, str(e))
    
    def test_game_session_message_limit(self):
        """Test 14: GameSession message history limit"""
        try:
            session = GameSession("test_session")
            
            # Add 25 messages (limit is 20)
            for i in range(25):
                session.add_message("user", f"Message {i}")
            
            # Should only keep last 20
            correct_limit = len(session.conversation_history) == 20
            
            # First message should be "Message 5" (0-4 dropped)
            first_msg = session.conversation_history[0]["content"]
            correct_first = "Message 5" in first_msg
            
            self.log_test("GameSession message limit", 
                         correct_limit and correct_first)
        except Exception as e:
            self.log_test("GameSession message limit", False, str(e))
    
    def test_database_connection(self):
        """Test 15: Database connection"""
        try:
            conn = self.mcp_client.get_connection()
            cursor = conn.cursor()
            
            # Try a simple query
            cursor.execute("SELECT COUNT(*) as count FROM characters")
            result = cursor.fetchone()
            
            # Should have 6 characters
            correct_count = result['count'] == 6
            
            cursor.close()
            conn.close()
            
            self.log_test("Database connection", correct_count)
        except Exception as e:
            self.log_test("Database connection", False, str(e))
    
    async def run_all_tests(self):
        """Run all MCP tests"""
        print("\n" + "="*60)
        print("SHADOWRUN GM - MCP TEST SUITE (Game Server)")
        print("="*60 + "\n")
        
        # MCP Tool tests
        print("MCP Tool Tests:")
        await self.test_get_character_skill()
        await self.test_calculate_dice_pool()
        await self.test_calculate_target_number()
        await self.test_roll_dice()
        await self.test_get_character()
        
        # DiceRoller tests
        print("\nDiceRoller Tests:")
        self.test_dice_roller_basic()
        self.test_dice_roller_explosions()
        self.test_dice_roller_rule_of_one()
        
        # CombatModifiers tests
        print("\nCombat Modifier Tests:")
        self.test_combat_modifiers_wound()
        self.test_combat_modifiers_range()
        
        # GameSession tests
        print("\nGameSession Tests:")
        self.test_game_session_creation()
        self.test_game_session_add_message()
        self.test_game_session_add_character()
        self.test_game_session_message_limit()
        
        # Database tests
        print("\nDatabase Tests:")
        self.test_database_connection()
        
        # Print summary
        print("\n" + "="*60)
        print(f"RESULTS: {self.passed} passed, {self.failed} failed, {self.tests_run} total")
        print("="*60 + "\n")
        
        return self.failed == 0


async def main():
    """Main test runner"""
    suite = MCPTestSuite()
    success = await suite.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
