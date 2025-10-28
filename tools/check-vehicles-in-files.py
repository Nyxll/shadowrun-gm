#!/usr/bin/env python3
"""Check which character files have vehicles sections"""
import os
import re

char_files = ['Platinum.md', 'Manticore.md', 'Block.md', 'Axel.md', 'Oak.md']

print("Checking for Vehicles sections in character files:")
print("=" * 60)

for filename in char_files:
    filepath = os.path.join('characters', filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    has_vehicles = bool(re.search(r'### Vehicles', content))
    
    if has_vehicles:
        # Extract the vehicles section
        vehicles_match = re.search(r'### Vehicles\s*\n(.*?)(?:\n###|\n---|\Z)', content, re.DOTALL)
        if vehicles_match:
            vehicles_text = vehicles_match.group(1).strip()
            # Count items (lines starting with "- **")
            items = re.findall(r'^- \*\*([^*]+)\*\*', vehicles_text, re.MULTILINE)
            print(f"\n{filename}: HAS VEHICLES ({len(items)} items)")
            for item in items:
                print(f"  - {item}")
        else:
            print(f"\n{filename}: HAS VEHICLES (but couldn't parse)")
    else:
        print(f"\n{filename}: no vehicles")

print("\n" + "=" * 60)
