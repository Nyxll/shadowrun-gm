#!/usr/bin/env python3
"""
Quick test to verify cyberware/bioware display is working
"""
import asyncio
import sys
sys.path.insert(0, '.')

from lib.mcp_operations import MCPOperations

async def test_character_cyberware():
    """Test that cyberware/bioware is properly formatted"""
    mcp = MCPOperations()
    
    try:
        # Test with Platinum (has extensive cyberware)
        print("Testing Platinum's cyberware/bioware display...")
        character = await mcp.get_character("Platinum")
        
        if 'error' in character:
            print(f"❌ Error: {character['error']}")
            return False
        
        print(f"\n✓ Character loaded: {character.get('name')} ({character.get('street_name')})")
        
        # Check cyberware
        cyberware = character.get('cyberware', [])
        print(f"\n📡 Cyberware ({len(cyberware)} items):")
        for item in cyberware:
            print(f"  • {item['name']}")
            print(f"    Essence: {item['essence_cost']}")
            if item['effects']:
                for effect in item['effects']:
                    print(f"    - {effect}")
        
        # Check bioware
        bioware = character.get('bioware', [])
        print(f"\n🧬 Bioware ({len(bioware)} items):")
        for item in bioware:
            print(f"  • {item['name']}")
            print(f"    Body Index: {item['body_index_cost']}")
            if item['effects']:
                for effect in item['effects']:
                    print(f"    - {effect}")
        
        if not cyberware and not bioware:
            print("\n⚠️  No cyberware or bioware found!")
            return False
        
        print("\n✅ Cyberware/bioware display is working!")
        return True
        
    finally:
        mcp.close()

if __name__ == "__main__":
    result = asyncio.run(test_character_cyberware())
    sys.exit(0 if result else 1)
