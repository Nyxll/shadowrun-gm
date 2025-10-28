#!/usr/bin/env python3
"""
Test Manticore's sniper shot using the MCP server's calculate_ranged_attack tool
Scenario: Manticore fires sniper rifle at running ork, 120m, walking, scope mag 2, daytime with fog
"""
import os
import sys
import asyncio

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Now import from parent directory
import importlib.util
spec = importlib.util.spec_from_file_location("game_server", os.path.join(parent_dir, "game-server.py"))
game_server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(game_server)

MCPClient = game_server.MCPClient

from dotenv import load_dotenv

load_dotenv()

async def main():
    print("=" * 70)
    print("MANTICORE'S SNIPER SHOT - MCP SERVER TEST")
    print("=" * 70)
    print("\nScenario:")
    print("  Character: Manticore")
    print("  Weapon: Sniper rifle with Mag 2 scope")
    print("  Target: Running ork")
    print("  Range: 120 meters")
    print("  Attacker: Walking")
    print("  Environment: Daytime with fog")
    print()
    
    # Initialize MCP client
    mcp = MCPClient()
    
    # Note: calculate_ranged_attack checks both name and street_name
    # so we can use "Manticore" directly
    print("Testing with character: Manticore (Edom Pentathor)")
    print()
    
    # Call the calculate_ranged_attack tool
    # Note: We need to manually account for attacker movement and defender movement
    # as these are situational modifiers not stored in the database
    result = await mcp.call_tool("calculate_ranged_attack", {
        "character_name": "Manticore",
        "weapon_name": "sniper",  # Will match any weapon with "sniper" in name
        "target_distance": 120,
        "target_description": "ork",
        "environment": "daytime with fog",
        "combat_pool": 0
    })
    
    if result.get('error'):
        print(f"ERROR: {result['error']}")
        sys.exit(1)
    
    print("CALCULATION BREAKDOWN:")
    print("-" * 70)
    print(f"Weapon Type: {result['weapon_type']}")
    print(f"Target Distance: {result['target_distance']}m")
    print(f"Vision Magnification: {result['vision_magnification']}")
    print(f"Effective Range Category: {result['range_category']}")
    print()
    
    print(f"Vision Enhancements:")
    for key, value in result['vision_enhancements'].items():
        print(f"  {key}: {value}")
    print()
    
    print(f"Light Level: {result['light_level']}")
    
    # Show combat modifiers
    if result.get('combat_modifiers'):
        print(f"\nCombat Modifiers from character_modifiers table:")
        for mod in result['combat_modifiers']:
            print(f"  {mod['source']} ({mod['type']}): {mod['value']}")
    print()
    
    print(f"Base TN (from range): {result['base_tn']}")
    print(f"\nModifiers Applied:")
    
    if result['modifiers']:
        for mod in result['modifiers']:
            sign = '+' if mod['value'] > 0 else ''
            print(f"  {mod['type']:.<50} {sign}{mod['value']}")
    else:
        print("  No modifiers")
    
    combat_bonus = result.get('combat_bonus', 0)
    if combat_bonus != 0:
        sign = '+' if combat_bonus > 0 else ''
        print(f"  {'Total Combat Modifiers':.<50} {sign}{combat_bonus}")
    
    print()
    print(f"{'CALCULATED TARGET NUMBER':.<50} {result['final_tn']}")
    print()
    
    # Now we need to add situational modifiers that aren't in the database
    print("ADDITIONAL SITUATIONAL MODIFIERS (not in database):")
    print("-" * 70)
    attacker_movement = 1  # Walking = +1 TN
    defender_movement = 2  # Running = +2 TN
    
    print(f"  Attacker walking:............................ +{attacker_movement}")
    print(f"  Defender running:............................ +{defender_movement}")
    
    final_tn_with_situational = result['final_tn'] + attacker_movement + defender_movement
    print()
    print(f"{'FINAL TARGET NUMBER':.<50} {final_tn_with_situational}")
    print("=" * 70)
    
    print("\nEXPLANATION:")
    print("-" * 70)
    print(f"1. Base TN from {result['range_category']} range: {result['base_tn']}")
    
    if result['vision_magnification'] > 0:
        print(f"2. Optical Magnification {result['vision_magnification']} shifts range:")
        print(f"   - 120m becomes {result['range_category']} range")
    
    # Find visibility modifier
    vis_mod = next((m for m in result['modifiers'] if 'Visibility' in m['type']), None)
    if vis_mod:
        print(f"3. Visibility (fog): {vis_mod['value']:+d} TN")
    
    # Find target modifier
    target_mod = next((m for m in result['modifiers'] if 'Target' in m['type'] or 'Situational' in m['type']), None)
    if target_mod:
        print(f"4. Target size: {target_mod['value']:+d} TN")
    
    # Show combat modifiers
    if result.get('combat_modifiers'):
        print(f"5. Combat modifiers:")
        for mod in result['combat_modifiers']:
            print(f"   - {mod['source']}: {mod['value']:+d} TN")
    
    print(f"6. Attacker walking: +{attacker_movement} TN")
    print(f"7. Defender running: +{defender_movement} TN")
    
    print()
    total_mod = result.get('total_modifier', 0) + attacker_movement + defender_movement
    print(f"Final: {result['base_tn']} (base) {total_mod:+d} (modifiers) = {final_tn_with_situational}")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
