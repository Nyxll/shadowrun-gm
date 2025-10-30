#!/usr/bin/env python3
"""Fix null bytes in mcp_operations.py"""

# Read and clean the file
with open('lib/mcp_operations.py', 'rb') as f:
    content = f.read()

# Remove null bytes
cleaned = content.replace(b'\x00', b'')

# Write back
with open('lib/mcp_operations.py', 'wb') as f:
    f.write(cleaned)

print("Fixed null bytes in lib/mcp_operations.py")
print(f"Original size: {len(content)} bytes")
print(f"Cleaned size: {len(cleaned)} bytes")
print(f"Removed {len(content) - len(cleaned)} null bytes")
