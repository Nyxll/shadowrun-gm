#!/usr/bin/env python3
"""
Debug test to see actual response from calculate_ranged_attack
"""
import sys
import os
import asyncio
import json

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import using importlib for hyphenated filename
import importlib.util
game_server_path = os.path.join(os.path.dirname(__file__), '..', 'game-server.py')
spec = importlib.util.spec_from_file_location("game_server", game_server_path)
game_server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(game_server)
MCPClient = game_server.MCPClient

async def debug_response():
    """See what the actual response looks like"""
    
    client = MCPClient()
    
    print("=" * 70)
    print("DEBUG: calculate_ranged_attack Response")
    print("=" * 70)
    print()
    
    try:
        result = await client.call_tool('calculate_ranged_attack', {
            'character_name': 'Platinum',
            'weapon_name': 'Morrissey Alta',
            'target_distance': 55,
            'target_description': 'rat',
            'environment': 'complete darkness',
            'combat_pool': 6
        })
        
        print("FULL RESPONSE:")
        print(json.dumps(result, indent=2))
        print()
        print("=" * 70)
        print("AVAILABLE KEYS:")
        for key in result.keys():
            print(f"  - {key}: {type(result[key]).__name__}")
        print("=" * 70)
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_response())
