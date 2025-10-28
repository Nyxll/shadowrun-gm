#!/usr/bin/env python3
import re

content = open('characters/Platinum.md', 'r', encoding='utf-8').read()

# Check for Armor and Equipment sections
print("Checking for sections:")
print(f"  ### Armor exists: {'### Armor' in content}")
print(f"  ### Equipment exists: {'### Equipment' in content}")

# Find all ### headers in Gear section
gear_section = re.search(r'## Gear\s*\n(.*?)(?:\n##|$)', content, re.DOTALL)
if gear_section:
    section_text = gear_section.group(1)
    headers = re.findall(r'### (.+)', section_text)
    print("\nGear subsections found:")
    for h in headers:
        print(f"  - {h}")
    
    # Count items in each section
    for header in headers:
        pattern = f'### {re.escape(header)}(.*?)(?:###|$)'
        subsection = re.search(pattern, section_text, re.DOTALL)
        if subsection:
            items = re.findall(r'- \*\*([^*]+)\*\*', subsection.group(1))
            print(f"\n{header}: {len(items)} items")
            for item in items[:5]:  # Show first 5
                print(f"  - {item}")
            if len(items) > 5:
                print(f"  ... and {len(items) - 5} more")
    
    # Show length of gear section
    print(f"\nGear section length: {len(section_text)} characters")
    print(f"Last 200 chars of gear section:")
    print(section_text[-200:])
else:
    print("No Gear section found")
