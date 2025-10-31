#!/usr/bin/env python3
"""
Remove the old get_mcp_tool_definitions function from game-server.py
since it's now imported from lib/server/tool_definitions.py
"""

# Read game-server.py
with open('game-server.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the function to remove
start_marker = '\n\ndef get_mcp_tool_definitions() -> List[Dict]:'
end_marker = '\n\n# WebSocket endpoint for live game sessions'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx == -1 or end_idx == -1:
    print("ERROR: Could not find function boundaries")
    exit(1)

# Remove the function (keep the WebSocket comment)
new_content = content[:start_idx] + content[end_idx:]

# Write back
with open('game-server.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

# Calculate reduction
old_lines = len(content.split('\n'))
new_lines = len(new_content.split('\n'))
removed_lines = old_lines - new_lines

print(f"✅ Successfully removed old function definition")
print(f"   Old file: {old_lines} lines")
print(f"   New file: {new_lines} lines")
print(f"   Removed: {removed_lines} lines")
