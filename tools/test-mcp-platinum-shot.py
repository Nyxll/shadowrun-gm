#!/usr/bin/env python3
"""
Test Platinum's shot using the MCP server's calculate_ranged_attack tool
This tests the complete integration including cyberware vision enhancements
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
    print("PLATINUM'S SHOT - MCP SERVER TEST (MODIFIER-BASED)")
    print("=" * 70)
    print("\nScenario:")
    print("  Character: Platinum (Kent Jefferies)")
    print("  Weapon: Morrissey Alta (heavy pistol)")
    print("  Target: Rat (small)")
    print("  Range: 55 meters")
    print("  Visibility: Complete darkness (sewer)")
    print()
    
    # Initialize MCP client
    mcp = MCPClient()
    
    # Call the calculate_ranged_attack tool
    result = await mcp.call_tool("calculate_ranged_attack", {
        "character_name": "Platinum",
        "weapon_name": "Morrissey Alta",
        "target_distance": 55,
        "target_description": "rat",
        "environment": "complete darkness",
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
    print(f"{'FINAL TARGET NUMBER':.<50} {result['final_tn']}")
    print("=" * 70)
    
    print("\nEXPLANATION:")
    print("-" * 70)
    print(f"1. Base TN from {result['range_category']} range: {result['base_tn']}")
    print(f"2. Optical Magnification {result['vision_magnification']} shifts range:")
    print(f"   - 55m at extreme range becomes {result['range_category']} range")
    
    # Find visibility modifier
    vis_mod = next((m for m in result['modifiers'] if 'Visibility' in m['type']), None)
    if vis_mod:
        print(f"3. Thermographic vision in darkness: {vis_mod['value']:+d} TN (cybernetic)")
    
    # Find target modifier
    target_mod = next((m for m in result['modifiers'] if 'Target' in m['type'] or 'Situational' in m['type']), None)
    if target_mod:
        print(f"4. Small target (rat): {target_mod['value']:+d} TN")
    
    # Show combat modifiers
    if result.get('combat_modifiers'):
        print(f"5. Combat modifiers:")
        for mod in result['combat_modifiers']:
            print(f"   - {mod['source']}: {mod['value']:+d} TN")
    
    print()
    total_mod = result.get('total_modifier', 0)
    print(f"Final calculation: {result['base_tn']} (base) {total_mod:+d} (modifiers) = {result['final_tn']}")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
