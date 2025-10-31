#!/usr/bin/env python3
"""
Update game-server.py to use the extracted WebSocket handler
and remove the old endpoint definition
"""

# Read game-server.py
with open('game-server.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Step 1: Add import after other lib.server imports
import_marker = 'from lib.server.mcp_client import MCPClient'
new_import = 'from lib.server.websocket_handler import create_websocket_endpoint'

if new_import not in content:
    content = content.replace(
        import_marker,
        f"{import_marker}\n{new_import}"
    )
    print("✅ Added websocket_handler import")
else:
    print("⚠️  Import already exists")

# Step 2: Remove the old WebSocket endpoint
start_marker = '\n\n# WebSocket endpoint for live game sessions'
end_marker = '\n\nif __name__ == "__main__":'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx != -1 and end_idx != -1:
    # Calculate lines removed
    removed_content = content[start_idx:end_idx]
    removed_lines = len(removed_content.split('\n'))
    
    # Remove the endpoint (keep the if __name__ section)
    content = content[:start_idx] + content[end_idx:]
    
    print(f"✅ Removed old WebSocket endpoint ({removed_lines} lines)")
else:
    print("⚠️  WebSocket endpoint not found or already removed")
    removed_lines = 0

# Step 3: Add the WebSocket endpoint registration before if __name__
# Find where to insert (right before if __name__)
insert_marker = '\nif __name__ == "__main__":'
insert_idx = content.find(insert_marker)

if insert_idx != -1:
    registration_code = '''
# Register WebSocket endpoint
create_websocket_endpoint(app, session_manager, mcp_client)

'''
    content = content[:insert_idx] + registration_code + content[insert_idx:]
    print("✅ Added WebSocket endpoint registration")
else:
    print("⚠️  Could not find insertion point")

# Write back
with open('game-server.py', 'w', encoding='utf-8') as f:
    f.write(content)

# Calculate final stats
final_lines = len(content.split('\n'))
print(f"\n📊 Final Stats:")
print(f"   game-server.py: {final_lines} lines")
print(f"   Removed: {removed_lines} lines")
