#!/usr/bin/env python3
"""Check Platinum's weapons"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.mcp_operations import MCPOperations

async def main():
    ops = MCPOperations()
    result = await ops.get_gear('Platinum', 'weapon')
    print("\nPlatinum's Weapons:")
    for weapon in result['gear']:
        print(f"  - {weapon['gear_name']}")

if __name__ == "__main__":
    asyncio.run(main())
