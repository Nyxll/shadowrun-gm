#!/usr/bin/env python3
"""
Verify all fixes are present in game-server.py
"""

import re

print("Verifying game-server.py fixes...\n")

with open('game-server.py', 'r', encoding='utf-8') as f:
    content = f.read()

checks = {
    "Grok model (grok-4-fast-non-reasoning)": 'grok-4-fast-non-reasoning' in content,
    "Error telemetry (grok_api_error)": 'grok_api_error' in content,
    "Cache-busting (NoCacheStaticFiles)": 'NoCacheStaticFiles' in content,
    "Model in telemetry data": bool(re.search(r'"model".*grok-4-fast-non-reasoning', content)),
    "Error type in telemetry": '"error_type"' in content,
    "WebSocket add_character handler": "elif message_type == 'add_character':" in content,
    "WebSocket remove_character handler": "elif message_type == 'remove_character':" in content,
    "WebSocket get_session_info handler": "elif message_type == 'get_session_info':" in content,
    "Try/except for Grok API": 'except Exception as grok_error:' in content,
    "Telemetry streaming start": 'grok_streaming_start' in content,
}

all_passed = True
for check_name, passed in checks.items():
    status = "✅" if passed else "❌"
    print(f"{status} {check_name}")
    if not passed:
        all_passed = False

print()
if all_passed:
    print("✅ ALL CHECKS PASSED - File is properly fixed!")
else:
    print("❌ SOME CHECKS FAILED - File may have issues")
    
# Count lines
lines = content.split('\n')
print(f"\nFile statistics:")
print(f"  Total lines: {len(lines)}")
print(f"  File size: {len(content)} bytes")

# Check for syntax errors
try:
    compile(content, 'game-server.py', 'exec')
    print(f"  ✅ Python syntax: VALID")
except SyntaxError as e:
    print(f"  ❌ Python syntax: INVALID - {e}")
    all_passed = False

exit(0 if all_passed else 1)
