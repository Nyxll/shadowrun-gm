#!/usr/bin/env python3
"""
Extract WebSocket endpoint from game-server.py to lib/server/websocket_handler.py
"""

# Read game-server.py
with open('game-server.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the WebSocket endpoint function
start_marker = '# WebSocket endpoint for live game sessions'
end_marker = '\n\nif __name__ == "__main__":'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx == -1 or end_idx == -1:
    print("ERROR: Could not find WebSocket endpoint boundaries")
    exit(1)

# Extract the function (including the comment)
ws_code = content[start_idx:end_idx]

# Create the new module with proper imports
module_content = '''"""
WebSocket Handler - Live Game Session Management
Handles WebSocket connections for real-time game sessions
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict
import json
import logging

from lib.server.session_manager import SessionManager
from lib.server.mcp_client import MCPClient

logger = logging.getLogger(__name__)


def create_websocket_endpoint(app, session_manager: SessionManager, mcp_client: MCPClient):
    """
    Create and register the WebSocket endpoint with the FastAPI app
    
    Args:
        app: FastAPI application instance
        session_manager: Session manager instance
        mcp_client: MCP client instance for tool routing
    """
    
    ''' + ws_code.replace('# WebSocket endpoint for live game sessions\n', '') + '''
    
    return websocket_endpoint
'''

# Write to new file
with open('lib/server/websocket_handler.py', 'w', encoding='utf-8') as f:
    f.write(module_content)

print("✅ Successfully extracted WebSocket handler")
print(f"   Handler size: {len(ws_code)} characters")
print(f"   Approximately {len(ws_code.split(chr(10)))} lines")
