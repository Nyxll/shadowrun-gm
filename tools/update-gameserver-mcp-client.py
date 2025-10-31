#!/usr/bin/env python3
"""
Update game-server.py to import MCPClient from lib.server.mcp_client
and remove the old class definition
"""

# Read game-server.py
with open('game-server.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Step 1: Add import after other lib.server imports
import_marker = 'from lib.server.tool_definitions import get_mcp_tool_definitions'
new_import = 'from lib.server.mcp_client import MCPClient'

if new_import not in content:
    content = content.replace(
        import_marker,
        f"{import_marker}\n{new_import}"
    )
    print("✅ Added MCPClient import")
else:
    print("⚠️  Import already exists")

# Step 2: Remove the old MCPClient class
start_marker = '\n\nclass MCPClient:'
end_marker = '\n\n# Global MCP client'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx != -1 and end_idx != -1:
    # Calculate lines removed
    removed_content = content[start_idx:end_idx]
    removed_lines = len(removed_content.split('\n'))
    
    # Remove the class (keep the Global MCP client comment)
    content = content[:start_idx] + content[end_idx:]
    
    print(f"✅ Removed old MCPClient class ({removed_lines} lines)")
else:
    print("⚠️  MCPClient class not found or already removed")
    removed_lines = 0

# Write back
with open('game-server.py', 'w', encoding='utf-8') as f:
    f.write(content)

# Calculate final stats
final_lines = len(content.split('\n'))
print(f"\n📊 Final Stats:")
print(f"   game-server.py: {final_lines} lines")
print(f"   Removed: {removed_lines} lines")
