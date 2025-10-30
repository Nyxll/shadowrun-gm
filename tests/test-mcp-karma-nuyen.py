#!/usr/bin/env python3
"""
Test MCP karma and nuyen operations
"""
import os
import sys
import asyncio
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib.mcp_operations import MCPOperations

load_dotenv()

async def test_mcp_karma_nuyen():
    """Test MCP karma and nuyen operations"""
    print("Testing MCP Karma & Nuyen Operations")
    print("=" * 60)
    
    mcp = MCPOperations()
    
    try:
        # Test with Oak character
        character_name = "Oak"
        
        print(f"\n1. Testing add_karma for {character_name}...")
        result = await mcp.add_karma(character_name, 5, "Test karma award via MCP")
        if "error" in result:
            print(f"   ✗ Error: {result['error']}")
        else:
            print(f"   ✓ {result['summary']}")
            print(f"   Total: {result['karma_total']}, Available: {result['karma_available']}")
        
        print(f"\n2. Testing spend_karma for {character_name}...")
        result = await mcp.spend_karma(character_name, 2, "Test karma spend via MCP")
        if "error" in result:
            print(f"   ✗ Error: {result['error']}")
        else:
            print(f"   ✓ {result['summary']}")
        
        print(f"\n3. Testing update_karma_pool for {character_name}...")
        result = await mcp.update_karma_pool(character_name, 15, "Test karma pool update via MCP")
        if "error" in result:
            print(f"   ✗ Error: {result['error']}")
        else:
            print(f"   ✓ {result['summary']}")
            print(f"   Karma pool: {result['karma_pool']}")
        
        print(f"\n4. Testing add_nuyen for {character_name}...")
        result = await mcp.add_nuyen(character_name, 2000, "Test nuyen award via MCP")
        if "error" in result:
            print(f"   ✗ Error: {result['error']}")
        else:
            print(f"   ✓ {result['summary']}")
        
        print(f"\n5. Testing spend_nuyen for {character_name}...")
        result = await mcp.spend_nuyen(character_name, 1000, "Test nuyen spend via MCP")
        if "error" in result:
            print(f"   ✗ Error: {result['error']}")
        else:
            print(f"   ✓ {result['summary']}")
        
        # Test error handling
        print(f"\n6. Testing error handling (insufficient karma)...")
        result = await mcp.spend_karma(character_name, 999999, "Should fail")
        if "error" in result:
            print(f"   ✓ Correctly raised error: {result['error']}")
        else:
            print(f"   ✗ Should have raised error!")
        
        print(f"\n7. Testing error handling (insufficient nuyen)...")
        result = await mcp.spend_nuyen(character_name, 999999, "Should fail")
        if "error" in result:
            print(f"   ✓ Correctly raised error: {result['error']}")
        else:
            print(f"   ✗ Should have raised error!")
        
        print("\n" + "=" * 60)
        print("✅ All MCP karma & nuyen tests passed!")
        print("=" * 60)
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        mcp.close()

if __name__ == "__main__":
    asyncio.run(test_mcp_karma_nuyen())
