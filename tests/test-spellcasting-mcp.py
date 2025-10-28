#!/usr/bin/env python3
"""
Spellcasting MCP Tests for Shadowrun GM
Tests the cast_spell MCP tool
"""

import os
import sys
import asyncio
from dotenv import load_dotenv
import importlib.util

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import using importlib for hyphenated filename
game_server_path = os.path.join(os.path.dirname(__file__), '..', 'game-server.py')
spec = importlib.util.spec_from_file_location("game_server", game_server_path)
game_server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(game_server)
MCPClient = game_server.MCPClient

load_dotenv()


class SpellcastingTests:
    """Test suite for cast_spell MCP tool"""
    
    def __init__(self):
        self.mcp_client = MCPClient()
        self.passed = 0
        self.failed = 0
    
    def log(self, name, passed, msg="", result=None):
        """Log test result"""
        if passed:
            self.passed += 1
            print(f"[PASS] {name}")
        else:
            self.failed += 1
            print(f"[FAIL] {name}: {msg}")
            if result:
                print(f"  Result: {result}")
    
    async def test_basic_cast(self):
        """Test basic spellcasting"""
        try:
            result = await self.mcp_client.call_tool("cast_spell", {
                "caster_name": "Test Leviathan",
                "spell_name": "Manabolt",
                "force": 3,
                "target_name": "enemy",
                "spell_pool_dice": 2,
                "drain_pool_dice": 2
            })
            self.log("Basic spellcasting", "spell_roll" in result and "drain" in result, result=result)
        except Exception as e:
            self.log("Basic spellcasting", False, str(e))
    
    async def test_magic_pool_limit(self):
        """Test Magic Pool validation"""
        try:
            result = await self.mcp_client.call_tool("cast_spell", {
                "caster_name": "Test Leviathan",
                "spell_name": "Manabolt",
                "force": 3,
                "target_name": "enemy",
                "spell_pool_dice": 15,  # Too many (Leviathan has Magic 6)
                "drain_pool_dice": 15
            })
            self.log("Magic Pool validation", "error" in result and "Magic Pool exceeded" in result.get("error", ""))
        except Exception as e:
            self.log("Magic Pool validation", False, str(e))
    
    async def test_cast_at_learned_force(self):
        """Test casting at learned force (Force 6)"""
        try:
            result = await self.mcp_client.call_tool("cast_spell", {
                "caster_name": "Test Leviathan",
                "spell_name": "Manabolt",
                "force": 6,  # Leviathan knows Manabolt at Force 6
                "target_name": "enemy",
                "spell_pool_dice": 2,
                "drain_pool_dice": 2
            })
            # Should succeed
            success = "spell_roll" in result and "drain" in result
            self.log("Cast at learned force (6)", success, result=result)
        except Exception as e:
            self.log("Cast at learned force (6)", False, str(e))
    
    async def test_learned_force_limit(self):
        """Test learned force validation - cannot cast above learned force"""
        try:
            result = await self.mcp_client.call_tool("cast_spell", {
                "caster_name": "Test Leviathan",
                "spell_name": "Manabolt",
                "force": 8,  # Leviathan knows Manabolt at Force 6, cannot cast at 8
                "target_name": "enemy",
                "spell_pool_dice": 2,
                "drain_pool_dice": 2
            })
            # Should get error about exceeding learned force
            has_error = "error" in result and "Cannot cast" in result.get("error", "")
            self.log("Cannot cast above learned force (8 > 6)", has_error, result=result)
        except Exception as e:
            self.log("Cannot cast above learned force (8 > 6)", False, str(e))
    
    async def test_totem_penalty_favored(self):
        """Test totem bonus on favored spell (Leviathan + Combat)"""
        try:
            result = await self.mcp_client.call_tool("cast_spell", {
                "caster_name": "Test Leviathan",
                "spell_name": "Manabolt",  # Combat spell, Leviathan favors Combat
                "force": 4,
                "target_name": "enemy",
                "spell_pool_dice": 2,
                "drain_pool_dice": 2
            })
            has_bonus = result.get("totem_bonus") == 2
            self.log("Totem bonus on favored spell", has_bonus, result=result)
        except Exception as e:
            self.log("Totem bonus on favored spell", False, str(e))
    
    async def test_totem_penalty_opposed(self):
        """Test totem penalty on opposed spell (Leviathan + Illusion)"""
        try:
            result = await self.mcp_client.call_tool("cast_spell", {
                "caster_name": "Test Leviathan",
                "spell_name": "Invisibility",  # Illusion spell, Leviathan opposes Illusion
                "force": 4,
                "target_name": "self",
                "spell_pool_dice": 2,
                "drain_pool_dice": 2
            })
            has_penalty = result.get("totem_penalty") == -2
            self.log("Totem penalty on opposed spell", has_penalty, result=result)
        except Exception as e:
            self.log("Totem penalty on opposed spell", False, str(e))
    
    async def run_all(self):
        """Run all tests"""
        print("\n" + "="*60)
        print("SPELLCASTING MCP TESTS")
        print("="*60 + "\n")
        
        await self.test_basic_cast()
        await self.test_magic_pool_limit()
        await self.test_cast_at_learned_force()
        await self.test_learned_force_limit()
        await self.test_totem_penalty_favored()
        await self.test_totem_penalty_opposed()
        
        print("\n" + "="*60)
        print(f"RESULTS: {self.passed} passed, {self.failed} failed")
        print("="*60 + "\n")
        
        return self.failed == 0


async def main():
    """Main test runner"""
    suite = SpellcastingTests()
    success = await suite.run_all()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
