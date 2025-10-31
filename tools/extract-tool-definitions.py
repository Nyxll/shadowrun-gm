#!/usr/bin/env python3
"""
Extract tool definitions from game-server.py to lib/server/tool_definitions.py
"""

# Read game-server.py
with open('game-server.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the start and end of get_mcp_tool_definitions function
start_marker = 'def get_mcp_tool_definitions() -> List[Dict]:'
end_marker = '\n\n# WebSocket endpoint for live game sessions'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx == -1 or end_idx == -1:
    print("ERROR: Could not find function boundaries")
    exit(1)

# Extract the function
function_code = content[start_idx:end_idx]

# Create the new module
module_content = '''"""
MCP Tool Definitions for Grok Function Calling
All 60+ tool definitions organized by phase
"""

from typing import List, Dict


''' + function_code

# Write to new file
with open('lib/server/tool_definitions.py', 'w', encoding='utf-8') as f:
    f.write(module_content)

print("✅ Successfully extracted tool definitions")
print(f"   Function size: {len(function_code)} characters")
print(f"   Approximately {len(function_code.split(chr(10)))} lines")
