#!/usr/bin/env python3
"""
Test spellcasting functionality
"""
import os
import sys
import asyncio
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment
load_dotenv()

# Import after path is set
import importlib.util
spec = importlib.util.spec_from_file_location("game_server", "game-server.py")
game_server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(game_server)
MCPClient = game_server.MCPClient

async def test_spellcasting():
    """Test the cast_spell tool"""
    
    client = MCPClient()
    
    print("=" * 60)
    print("Testing Spellcasting Tool")
    print("=" * 60)
    
    # Test 1: Block casts Levitate at Force 4
    print("\n1. Block casts Levitate on Platinum at Force 4")
    print("-" * 60)
    
    result = await client.call_tool("cast_spell", {
        "caster_name": "Block",
        "spell_name": "Levitate",
        "force": 4,
        "target_name": "Platinum",
        "spell_pool": 0
    })
    
    if "error" in result:
        print(f"❌ ERROR: {result['error']}")
    else:
        print(f"✅ Caster: {result['caster']}")
        print(f"✅ Spell: {result['spell']} (Force {result['force']})")
        print(f"✅ Target: {result['target']}")
        print(f"✅ Sorcery Skill: {result['sorcery_skill']}")
        print(f"✅ Dice Pool: {result['dice_pool']}d6")
        print(f"✅ Target Number: {result['target_number']}")
        print(f"✅ Rolls: {result['spell_roll']['rolls']}")
        print(f"✅ Successes: {result['spell_roll']['successes']}")
        print(f"✅ Result: {result['spell_roll']['result']}")
        print(f"✅ Drain: {result['drain']['level']}{result['drain']['code']}")
        print(f"✅ Resist with: {result['drain']['resist_with']} ({result['drain']['willpower_rating']})")
        print(f"\n📝 Summary: {result['summary']}")
    
    # Test 2: Higher force spell
    print("\n\n2. Block casts Fireball at Force 8 (with 2 spell pool)")
    print("-" * 60)
    
    result = await client.call_tool("cast_spell", {
        "caster_name": "Block",
        "spell_name": "Fireball",
        "force": 8,
        "target_name": None,
        "spell_pool": 2
    })
    
    if "error" in result:
        print(f"❌ ERROR: {result['error']}")
    else:
        print(f"✅ Spell: {result['spell']} (Force {result['force']})")
        print(f"✅ Dice Pool: {result['dice_pool']}d6 (Sorcery {result['sorcery_skill']} + Spell Pool {result['spell_pool_used']})")
        print(f"✅ Target Number: {result['target_number']}")
        print(f"✅ Rolls: {result['spell_roll']['rolls']}")
        print(f"✅ Successes: {result['spell_roll']['successes']}")
        print(f"✅ Drain: {result['drain']['level']}{result['drain']['code']} (Serious drain!)")
        print(f"\n📝 Summary: {result['summary']}")
    
    # Test 3: Character without magic
    print("\n\n3. Platinum tries to cast (should fail - no magic)")
    print("-" * 60)
    
    result = await client.call_tool("cast_spell", {
        "caster_name": "Platinum",
        "spell_name": "Heal",
        "force": 3,
        "target_name": "Platinum",
        "spell_pool": 0
    })
    
    if "error" in result:
        print(f"✅ Expected error: {result['error']}")
    else:
        print(f"❌ Should have failed - Platinum has no magic!")
    
    # Test 4: Non-existent character
    print("\n\n4. Non-existent character (should fail)")
    print("-" * 60)
    
    result = await client.call_tool("cast_spell", {
        "caster_name": "NotARealCharacter",
        "spell_name": "Levitate",
        "force": 4,
        "target_name": None,
        "spell_pool": 0
    })
    
    if "error" in result:
        print(f"✅ Expected error: {result['error']}")
    else:
        print(f"❌ Should have failed - character doesn't exist!")
    
    print("\n" + "=" * 60)
    print("Spellcasting Tests Complete!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_spellcasting())
