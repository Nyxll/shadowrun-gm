#!/usr/bin/env python3
"""
Audit all operations across the system
"""
import re
from pathlib import Path

def extract_async_methods(filepath):
    """Extract async method names from a Python file"""
    methods = []
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        # Find all async def methods
        pattern = r'async def (\w+)\('
        matches = re.findall(pattern, content)
        methods = [m for m in matches if not m.startswith('_')]
    return methods

def extract_crud_methods(filepath):
    """Extract public method names from ComprehensiveCRUD class"""
    methods = []
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        # Find all def methods (not async, not private)
        pattern = r'^\s{4}def (\w+)\('
        matches = re.findall(pattern, content, re.MULTILINE)
        methods = [m for m in matches if not m.startswith('_')]
    return methods

def extract_mcp_tools(filepath):
    """Extract MCP tool definitions from game-server.py"""
    tools = []
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        # Find tool definitions in the tools list
        pattern = r'"name":\s*"(\w+)"'
        matches = re.findall(pattern, content)
        tools = list(set(matches))  # Remove duplicates
    return sorted(tools)

def count_documented_tools(filepath):
    """Count documented tools in MCP-TOOLS-REFERENCE.md"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        # Count ### N. patterns
        pattern = r'^### \d+\.'
        matches = re.findall(pattern, content, re.MULTILINE)
    return len(matches)

print("=" * 80)
print("OPERATIONS AUDIT")
print("=" * 80)

# Audit comprehensive_crud.py
print("\n1. COMPREHENSIVE_CRUD.PY")
crud_methods = extract_crud_methods('lib/comprehensive_crud.py')
print(f"   Total public methods: {len(crud_methods)}")
print(f"   Methods: {', '.join(crud_methods[:10])}...")

# Audit mcp_operations.py
print("\n2. MCP_OPERATIONS.PY")
mcp_methods = extract_async_methods('lib/mcp_operations.py')
print(f"   Total async methods: {len(mcp_methods)}")
print(f"   Methods: {', '.join(mcp_methods)}")

# Audit game-server.py
print("\n3. GAME-SERVER.PY")
game_tools = extract_mcp_tools('game-server.py')
print(f"   Total MCP tools: {len(game_tools)}")
print(f"   Tools: {', '.join(game_tools)}")

# Audit documentation
print("\n4. MCP-TOOLS-REFERENCE.MD")
doc_count = count_documented_tools('docs/MCP-TOOLS-REFERENCE.md')
print(f"   Documented tools: {doc_count}")

# Calculate gaps
print("\n" + "=" * 80)
print("GAP ANALYSIS")
print("=" * 80)
print(f"CRUD operations available: {len(crud_methods)}")
print(f"MCP operations exposed: {len(mcp_methods)}")
print(f"Game server tools: {len(game_tools)}")
print(f"Documented tools: {doc_count}")
print(f"\nGap (CRUD → MCP): {len(crud_methods) - len(mcp_methods)} operations")
print(f"Gap (MCP → Game Server): {len(mcp_methods) - len(game_tools)} operations")
print(f"Gap (Game Server → Docs): {len(game_tools) - doc_count} tools")

# Show what's in MCP but not in game server
mcp_set = set(mcp_methods)
game_set = set(game_tools)
missing_in_game = mcp_set - game_set
if missing_in_game:
    print(f"\nIn MCP but NOT in game-server: {', '.join(sorted(missing_in_game))}")

# Show what's in game server but not in MCP
missing_in_mcp = game_set - mcp_set
if missing_in_mcp:
    print(f"\nIn game-server but NOT in MCP: {', '.join(sorted(missing_in_mcp))}")

print("\n" + "=" * 80)
