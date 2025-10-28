#!/usr/bin/env python3
"""Find where bioware section is"""
with open('characters/Platinum.md', 'r', encoding='utf-8') as f:
    content = f.read()

import re

# Find all section headers
sections = re.findall(r'^(##+ .+)$', content, re.MULTILINE)
print("All sections in Platinum.md:")
for i, section in enumerate(sections):
    print(f"{i}: {section}")

# Check if Bioware is a subsection
bioware_match = re.search(r'### Bioware', content)
print(f"\n'### Bioware' found: {bool(bioware_match)}")

if bioware_match:
    # Show context around it
    start = max(0, bioware_match.start() - 100)
    end = min(len(content), bioware_match.end() + 300)
    print("\nContext around Bioware:")
    print(content[start:end])
