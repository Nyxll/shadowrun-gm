#!/usr/bin/env python3
"""Debug bioware parsing"""
import re

content = open('characters/Platinum.md', 'r', encoding='utf-8').read()

# Try format 1: Combined section
cyber_section = re.search(r'## Cyberware/Bioware\s*\n(.*?)(?:\n##|$)', content, re.DOTALL | re.IGNORECASE)
print("Format 1 (combined) found:", cyber_section is not None)

# Try format 2: Separate sections
bio_section = re.search(r'## Bioware\s*\n(.*?)(?:\n##|$)', content, re.DOTALL | re.IGNORECASE)
print("Format 2 (separate bioware) found:", bio_section is not None)

if bio_section:
    print("\nParsing bioware section...")
    bioware = []
    current_item = None
    
    for i, line in enumerate(bio_section.group(1).split('\n')):
        print(f"Line {i}: {repr(line[:80])}")
        
        if line.strip() == '---':
            print("  -> Hit separator, breaking")
            break
            
        if line.strip().startswith('- **'):
            print(f"  -> Item line detected")
            if current_item:
                print(f"  -> Saving previous item: {current_item['name']}")
                bioware.append(current_item)
                
            item_match = re.match(r'-\s*\*\*([^*]+)\*\*\s*(?:\(([0-9.]+)\s+(Essence|Body Index)\))?', line)
            if item_match:
                print(f"  -> Matched: {item_match.groups()}")
                current_item = {
                    'name': item_match.group(1).strip(),
                    'essence_cost': float(item_match.group(2)) if item_match.group(3) == 'Essence' and item_match.group(2) else 0.0,
                    'body_index_cost': float(item_match.group(2)) if item_match.group(3) == 'Body Index' and item_match.group(2) else 0.0,
                    'modifiers': []
                }
            else:
                print(f"  -> NO MATCH!")
        elif line.strip().startswith('- ') and current_item:
            print(f"  -> Modifier line for {current_item['name']}")
            current_item['modifiers'].append(line.strip()[2:].strip())
    
    if current_item:
        print(f"  -> Saving final item: {current_item['name']}")
        bioware.append(current_item)
    
    print(f"\n\nTotal bioware items parsed: {len(bioware)}")
    for item in bioware:
        print(f"  - {item['name']}: {item['body_index_cost']} Body Index")
