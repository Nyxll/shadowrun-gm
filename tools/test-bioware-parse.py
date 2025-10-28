#!/usr/bin/env python3
"""Test bioware parsing"""
import re

content = open('characters/Manticore.md', 'r', encoding='utf-8').read()

# Get Cyberware/Bioware section
pattern = r'##\s+Cyberware/Bioware.*?\n(.*?)(?=\n##|\Z)'
section_match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)

if not section_match:
    print("NO CYBERWARE/BIOWARE SECTION FOUND")
    exit(1)

section = section_match.group(1)
print(f"Section length: {len(section)}")
print("=" * 70)
print("Full section content:")
print(section)
print("=" * 70)

# Get Bioware subsection
bio_match = re.search(r'###\s+Bioware(.*?)(?=###|\Z)', section, re.DOTALL | re.IGNORECASE)

if not bio_match:
    print("NO BIOWARE SUBSECTION FOUND")
    print("\nTrying alternate regex...")
    bio_match = re.search(r'###\s+Bioware(.*?)(?=\n###|\n##|\Z)', section, re.DOTALL | re.IGNORECASE)
    if bio_match:
        print("FOUND with alternate regex!")
    else:
        exit(1)

bio_section = bio_match.group(1)
print(f"Bioware section length: {len(bio_section)}")
print("=" * 70)
print("Bioware section content:")
print(bio_section[:500])
print("=" * 70)

# Parse items
items = re.split(r'\n-\s+\*\*', bio_section)
print(f"\nFound {len(items)} items (including empty first split)")

for i, item in enumerate(items):
    if i == 0:
        continue  # Skip first empty split
    
    print(f"\n--- Item {i} ---")
    lines = item.split('\n')
    first_line = lines[0]
    print(f"First line: {first_line}")
    
    # Try Body Index format
    name_match = re.match(r'(.+?)\*\*\s*\(([\d.]+)\s+Body Index\)', first_line)
    if name_match:
        print(f"  Matched Body Index: {name_match.group(1)} = {name_match.group(2)}")
    else:
        # Try Essence format
        name_match = re.match(r'(.+?)\*\*\s*\(([\d.]+)\s+Essence\)', first_line)
        if name_match:
            print(f"  Matched Essence: {name_match.group(1)} = {name_match.group(2)}")
        else:
            print(f"  NO MATCH!")
