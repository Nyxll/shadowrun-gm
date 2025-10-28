#!/usr/bin/env python3
import re

with open('data-load-final-1.sql', 'r', encoding='utf-8') as f:
    content = f.read()

# Test different patterns
patterns = [
    r"'\\[\\]'::jsonb,\s*'\\{\\}'::jsonb",
    r"'\[\]'::jsonb,\s*'\{\}'::jsonb",
    r"'\[\]'::jsonb, '\{\}'::jsonb",
]

for i, pattern in enumerate(patterns, 1):
    matches = re.findall(pattern, content)
    print(f"Pattern {i}: {len(matches)} matches")
    if matches:
        print(f"  First match: {matches[0]}")

# Show the actual metatype line
metatype = re.search(r'INSERT INTO metatypes.*?;', content, re.DOTALL)
if metatype:
    line = metatype.group(0)
    # Find the special_abilities and racial_traits part
    abilities_part = re.search(r"special_abilities.*?racial_traits.*?description", line, re.DOTALL)
    if abilities_part:
        print(f"\nActual text around special_abilities:")
        print(abilities_part.group(0)[:200])
