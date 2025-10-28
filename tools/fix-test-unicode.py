#!/usr/bin/env python3
"""
Fix Unicode characters in test files for Windows compatibility
Replaces ✓ and ✗ with ASCII equivalents
"""

import os
import re

# Test files to fix
test_files = [
    'tests/test-all-crud-operations.py',
    'tests/test-comprehensive-crud.py',
    'tests/test-schema-fixes.py',
    'tests/test-spell-force-display.py',
    'tests/test-cast-spell-learned-force.py',
    'tests/test-spellcasting-mcp.py',
]

def fix_unicode_in_file(filepath):
    """Replace Unicode checkmarks with ASCII equivalents"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace Unicode characters
        original = content
        content = content.replace('\u2713', '[PASS]')  # ✓
        content = content.replace('\u2717', '[FAIL]')  # ✗
        content = content.replace('\u274c', '[FAIL]')  # ❌
        
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed: {filepath}")
            return True
        else:
            print(f"No changes needed: {filepath}")
            return False
            
    except Exception as e:
        print(f"Error fixing {filepath}: {e}")
        return False

def main():
    """Fix all test files"""
    print("Fixing Unicode characters in test files...")
    print("="*70)
    
    fixed_count = 0
    for filepath in test_files:
        if os.path.exists(filepath):
            if fix_unicode_in_file(filepath):
                fixed_count += 1
        else:
            print(f"Not found: {filepath}")
    
    print("="*70)
    print(f"Fixed {fixed_count} file(s)")

if __name__ == "__main__":
    main()
