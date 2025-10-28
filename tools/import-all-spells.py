#!/usr/bin/env python3
"""Quick script to import spells for all magic users"""
import os
import sys

# Character file to database name mapping
characters = [
    ('Block.md', 'Kent Jefferies'),
    ('Oak.md', "Riley O'Connor"),
    ('Platinum.md', 'Edom Pentathor'),
]

for filename, db_name in characters:
    filepath = os.path.join('characters', filename)
    if os.path.exists(filepath):
        print(f"\n{'='*60}")
        print(f"Importing spells for {db_name} from {filename}")
        print('='*60)
        os.system(f'python tools/import-characters-v9.py --character "{filename[:-3]}" --section spells')
    else:
        print(f"✗ File not found: {filepath}")

print("\n" + "="*60)
print("Spell import complete!")
print("="*60)
