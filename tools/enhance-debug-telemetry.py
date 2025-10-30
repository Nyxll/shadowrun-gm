#!/usr/bin/env python3
"""
Add enhanced telemetry to game-server.py for comprehensive debug window
This script adds helper functions and additional telemetry events
"""

import os
import sys

# Read the current game-server.py
with open('game-server.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Define the helper function to add after the SessionManager class
helper_functions = '''

async def send_telemetry(websocket: WebSocket, event: str, data: dict = None, level: str = "INFO"):
    """
    Helper function to send telemetry events to the UI
    
    Args:
        websocket: WebSocket connection
        event: Event type (e.g., 'database_query', 'mcp_operation_start')
        data: Event-specific data
        level: Log level (INFO, WARNING, ERROR, DEBUG)
    """
    await websocket.send_json({
        "type": "telemetry",
        "event": event,
        "level": level,
        "data": data or {},
        "timestamp": datetime.now().isoformat()
    })


async def send_mcp_telemetry(websocket: WebSocket, operation: str, phase: str, data: dict = None):
    """
    Send MCP operation telemetry
    
    Args:
        operation: Operation name (e.g., 'get_character', 'cast_spell')
        phase: 'start' or 'complete'
        data: Operation-specific data (arguments, results, timing)
    """
    event = f"mcp_operation_{phase}"
    telemetry_data = {"operation": operation}
    if data:
        telemetry_data.update(data)
    
    await send_telemetry(websocket, event, telemetry_data)


async def send_database_telemetry(websocket: WebSocket, query_type: str, table: str = None, duration_ms: float = None):
    """
    Send database operation telemetry
    
    Args:
        query_type: Type of query (SELECT, INSERT, UPDATE, DELETE)
        table: Table name
        duration_ms: Query duration in milliseconds
    """
    data = {"query_type": query_type}
    if table:
        data["table"] = table
    if duration_ms is not None:
        data["duration_ms"] = round(duration_ms, 2)
    
    await send_telemetry(websocket, "database_query", data)


async def send_api_telemetry(websocket: WebSocket, endpoint: str, method: str, status_code: int = None, duration_ms: float = None):
    """
    Send API operation telemetry
    
    Args:
        endpoint: API endpoint path
        method: HTTP method (GET, POST, etc.)
        status_code: Response status code
        duration_ms: Request duration in milliseconds
    """
    data = {
        "endpoint": endpoint,
        "method": method
    }
    if status_code:
        data["status_code"] = status_code
    if duration_ms is not None:
        data["duration_ms"] = round(duration_ms, 2)
    
    event = "api_request" if status_code is None else "api_response"
    await send_telemetry(websocket, event, data)


async def send_error_telemetry(websocket: WebSocket, error: Exception, context: str = None):
    """
    Send error telemetry with full context
    
    Args:
        error: Exception object
        context: Additional context about where the error occurred
    """
    import traceback
    
    data = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "stack_trace": traceback.format_exc()
    }
    if context:
        data["context"] = context
    
    await send_telemetry(websocket, "error_occurred", data, level="ERROR")


async def send_ui_telemetry(websocket: WebSocket, action: str, component: str = None, data: dict = None):
    """
    Send UI interaction telemetry
    
    Args:
        action: UI action (e.g., 'character_selected', 'sheet_opened')
        component: UI component name
        data: Action-specific data
    """
    telemetry_data = {"action": action}
    if component:
        telemetry_data["component"] = component
    if data:
        telemetry_data.update(data)
    
    await send_telemetry(websocket, "ui_interaction", telemetry_data)
'''

# Find where to insert the helper functions (after SessionManager class)
session_manager_end = content.find('# Global session manager')
if session_manager_end == -1:
    print("ERROR: Could not find insertion point for helper functions")
    sys.exit(1)

# Insert helper functions
enhanced_content = (
    content[:session_manager_end] +
    helper_functions + '\n\n' +
    content[session_manager_end:]
)

# Write the enhanced version
with open('game-server.py', 'w', encoding='utf-8') as f:
    f.write(enhanced_content)

print("✓ Added telemetry helper functions to game-server.py")
print("\nNext steps:")
print("1. Add telemetry calls throughout the WebSocket handler")
print("2. Add telemetry to MCP tool execution")
print("3. Add telemetry to database operations")
print("4. Update UI to display all event types")
