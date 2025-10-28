#!/usr/bin/env python3
import re

with open('characters/Platinum.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Try the OLD regex
gear_old = re.search(r'## Gear\s*\n(.*?)(?:\n##|$)', content, re.DOTALL)
if gear_old:
    matched = gear_old.group(1)
    print("OLD REGEX:")
    print(f"  Matched {len(matched)} characters")
    print(f"  '### Armor' in matched: {'### Armor' in matched}")
    print(f"  '### Equipment' in matched: {'### Equipment' in matched}")
    print(f"  '### Vehicles' in matched: {'### Vehicles' in matched}")

# Try the NEW regex with negative lookahead
gear_new = re.search(r'## Gear\s*\n(.*?)(?:\n## (?!#)|$)', content, re.DOTALL)
if gear_new:
    matched = gear_new.group(1)
    print("\nNEW REGEX (with negative lookahead):")
    print(f"  Matched {len(matched)} characters")
    print(f"  '### Armor' in matched: {'### Armor' in matched}")
    print(f"  '### Equipment' in matched: {'### Equipment' in matched}")
    print(f"  '### Vehicles' in matched: {'### Vehicles' in matched}")
