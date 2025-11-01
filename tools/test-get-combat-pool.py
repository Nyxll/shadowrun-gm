#!/usr/bin/env python3
"""
Test the new get_combat_pool tool
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.mcp_operations import MCPOperations

async def test_get_combat_pool():
    """Test get_combat_pool for Platinum"""
    ops = MCPOperations()
    
    try:
        print("Testing get_combat_pool for Platinum...")
        result = await ops.get_combat_pool("Platinum")
        
        print("\n=== RESULT ===")
        print(f"Character: {result.get('character')}")
        print(f"Combat Pool: {result.get('combat_pool')}")
        print(f"Magic Pool: {result.get('magic_pool')}")
        print(f"Summary: {result.get('summary')}")
        
        # Verify the value
        if result.get('combat_pool') == 18:
            print("\n✓ SUCCESS: Combat pool is correct (18)")
        else:
            print(f"\n✗ FAIL: Combat pool is {result.get('combat_pool')}, expected 18")
        
    finally:
        ops.close()

if __name__ == "__main__":
    asyncio.run(test_get_combat_pool())
