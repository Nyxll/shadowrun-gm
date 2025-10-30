#!/usr/bin/env python3
"""Check if MCP operations do proper character name → UUID lookups"""

from pathlib import Path
import re

def check_mcp_operations():
    mcp_file = Path("lib/mcp_operations.py")
    content = mcp_file.read_text()
    
    # Find all async def methods
    methods = re.findall(r'async def (\w+)\(self.*?\).*?(?=\n    async def |\n    def |\nclass |\Z)', content, re.DOTALL)
    
    print("Checking MCP Operations for character name → UUID lookups...\n")
    print("="*80)
    
    for i, method_match in enumerate(re.finditer(r'async def (\w+)\(self.*?\).*?(?=\n    async def |\n    def |\nclass |\Z)', content, re.DOTALL), 1):
        method_name = method_match.group(1)
        method_body = method_match.group(0)
        
        # Check if method takes character_name parameter
        if 'character_name' in method_body[:200]:  # Check in signature
            print(f"\n{i}. Method: {method_name}")
            print("-" * 80)
            
            # Check if it does lookup
            has_lookup = 'get_character_id' in method_body or 'SELECT id FROM characters WHERE name' in method_body
            
            if has_lookup:
                print("   ✓ Has character name → UUID lookup")
            else:
                print("   ✗ MISSING character name → UUID lookup")
                # Show first 10 lines of method
                lines = method_body.split('\n')[:10]
                for line in lines:
                    print(f"      {line}")

if __name__ == "__main__":
    check_mcp_operations()
