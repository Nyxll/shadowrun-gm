#!/usr/bin/env python3
import re

content = open('characters/Manticore.md', 'r', encoding='utf-8').read()

# Test the parse_markdown_section function
pattern = r'##\s+Cyberware/Bioware.*?\n(.*?)(?=\n##|\Z)'
match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)

print("Match found:", match is not None)
if match:
    section = match.group(1)
    print(f"Section length: {len(section)}")
    print(f"Has '### Bioware': {'### Bioware' in section}")
    print(f"\nSection content:\n{section}")
