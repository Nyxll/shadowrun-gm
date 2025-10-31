#!/usr/bin/env python3
"""
Extract MCPClient class from game-server.py to lib/server/mcp_client.py
"""

# Read game-server.py
with open('game-server.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the MCPClient class
start_marker = 'class MCPClient:'
end_marker = '\n\n# Global MCP client'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx == -1 or end_idx == -1:
    print("ERROR: Could not find MCPClient class boundaries")
    exit(1)

# Extract the class
class_code = content[start_idx:end_idx]

# Create the new module
module_content = '''"""
MCP Client - Tool Routing Layer
Routes tool calls to MCPOperations
"""

from typing import Dict, Any
from lib.mcp_operations import MCPOperations


''' + class_code

# Write to new file
with open('lib/server/mcp_client.py', 'w', encoding='utf-8') as f:
    f.write(module_content)

print("✅ Successfully extracted MCPClient class")
print(f"   Class size: {len(class_code)} characters")
print(f"   Approximately {len(class_code.split(chr(10)))} lines")
