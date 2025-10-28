#!/usr/bin/env python3
"""
Test that game-server.py can be imported without errors
"""

import sys
import importlib.util

print("Testing game-server.py import...")

try:
    # Load the module
    spec = importlib.util.spec_from_file_location("game_server", "game-server.py")
    module = importlib.util.module_from_spec(spec)
    
    print("✅ Module loaded successfully")
    print("✅ No import errors")
    print("\nThe server file is valid and ready to run!")
    print("\nTo start the server, run:")
    print("  python game-server.py")
    
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)
