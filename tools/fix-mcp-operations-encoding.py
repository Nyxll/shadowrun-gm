#!/usr/bin/env python3
"""Fix encoding issues in mcp_operations.py"""

# Read and clean the file
with open('lib/mcp_operations.py', 'rb') as f:
    content = f.read()

# Remove BOM and null bytes
cleaned = content.replace(b'\xff\xfe', b'').replace(b'\x00', b'')

# Write back as UTF-8
with open('lib/mcp_operations.py', 'w', encoding='utf-8') as f:
    f.write(cleaned.decode('utf-8', errors='ignore'))

print("Fixed encoding in lib/mcp_operations.py")
