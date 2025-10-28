#!/usr/bin/env python3
"""
Test the calculate_ranged_attack MCP tool
"""
import sys
import os
import asyncio

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import using importlib for hyphenated filename
import importlib.util
game_server_path = os.path.join(os.path.dirname(__file__), '..', 'game-server.py')
spec = importlib.util.spec_from_file_location("game_server", game_server_path)
game_server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(game_server)
MCPClient = game_server.MCPClient

async def test_platinum_rat_shot():
    """Test Platinum shooting at rat in darkness"""
    
    client = MCPClient()
    
    print("=" * 70)
    print("TEST: Platinum vs Rat with MCP Tool")
    print("=" * 70)
    print()
    
    result = await client.call_tool('calculate_ranged_attack', {
        'character_name': 'Platinum',
        'weapon_name': 'Morrissey Alta',
        'target_distance': 55,
        'target_description': 'rat',
        'environment': 'complete darkness',
        'combat_pool': 6
    })
    
    print("RESULT:")
    print(f"  Character: {result['character']}")
    print(f"  Weapon: {result['weapon']} ({result['weapon_type']})")
    print(f"  Actual Distance: {result['target_distance']}m")
    print(f"  Vision Magnification: ×{result['vision_magnification']}")
    
    # Explain magnification effect on range category
    print(f"  Range Category: {result['range_category']}")
    if result['vision_magnification'] > 0:
        print(f"    (Magnification ×{result['vision_magnification']} shifts range category down {result['vision_magnification']} level(s))")
        print(f"    (Each mag level: extreme→long→medium→short)")
    
    print(f"  Environment: {result['environment']}")
    print(f"  Light Level: {result['light_level']}")
    print()
    
    print("VISION ENHANCEMENTS:")
    for key, value in result['vision_enhancements'].items():
        print(f"  {key}: {value}")
    print()
    
    print("COMBAT MODIFIERS:")
    if result['combat_modifiers']:
        for mod in result['combat_modifiers']:
            print(f"  {mod['source']} ({mod['type']}): {mod['value']:+d}")
    print()
    
    print("TARGET NUMBER CALCULATION:")
    print(f"  Base TN ({result['range_category']} range): {result['base_tn']}")
    
    if result['modifiers']:
        print("  Modifiers:")
        for mod in result['modifiers']:
            sign = '+' if mod['value'] > 0 else ''
            print(f"    {mod['type']}: {sign}{mod['value']}")
            if 'explanation' in mod:
                print(f"      ({mod['explanation']})")
    
    print(f"  Combat Bonus: {result['combat_bonus']:+d}")
    print(f"  Total Modifier: {result['total_modifier']:+d}")
    print(f"  FINAL TN: {result['final_tn']}")
    print()
    
    if result['roll']:
        print("DICE ROLL:")
        print(f"  Combat Pool: {result['combat_pool']} dice")
        print(f"  Rolls: {result['roll']['rolls']}")
        print(f"  Successes: {result['roll']['successes']}")
        
        if result['roll']['all_ones']:
            print("  Result: CRITICAL GLITCH!")
        elif result['roll']['successes'] == 0:
            print("  Result: MISS")
        elif result['roll']['successes'] == 1:
            print("  Result: Marginal hit (1 success)")
        else:
            print(f"  Result: SOLID HIT ({result['roll']['successes']} successes)!")
    
    print()
    print("=" * 70)
    
    # Verify correct calculation
    # Base TN 4 (short range) + 2 (darkness) + 2 (small target) - 3 (smartlink) = 5
    expected_tn = 5
    if result['final_tn'] == expected_tn:
        print(f"✓ PASS: TN calculation correct (TN {expected_tn})")
    else:
        print(f"✗ FAIL: Expected TN {expected_tn}, got {result['final_tn']}")
    
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_platinum_rat_shot())
