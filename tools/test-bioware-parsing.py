#!/usr/bin/env python3
"""Test bioware parsing"""
import re

# Sample from Platinum.md
test_text = """## Cyberware/Bioware
### Cyberware
- **Wired Reflexes 3 (Beta-Grade)** (2.4 Essence) 
  - +6 Reaction 
  - +3D6 Initiative 

- **Cybereyes** (0.2 Essence) 
  - Thermographic 

### Bioware
- **Enhanced Articulation** (0.3 Body Index) 
  - +1 die to physical skills 
  - +1 Reaction 

- **Cerebral Booster 3** (0.4 Body Index) 
  - +3 Intelligence 
"""

cyber_section = re.search(r'## Cyberware/Bioware\s*\n(.*?)(?:\n##|$)', test_text, re.DOTALL)
if cyber_section:
    print("Found Cyberware/Bioware section")
    print("=" * 70)
    
    current_type = None
    items_found = []
    
    for line in cyber_section.group(1).split('\n'):
        print(f"Line: {repr(line)}")
        
        # Check for subsection headers
        if line.strip().startswith('### Cyberware'):
            current_type = 'cyberware'
            print(f"  -> Set type to: {current_type}")
            continue
        elif line.strip().startswith('### Bioware'):
            current_type = 'bioware'
            print(f"  -> Set type to: {current_type}")
            continue
        
        # Parse items
        if line.strip().startswith('- **') and current_type:
            item_match = re.match(r'-\s*\*\*([^*]+)\*\*\s*(?:\(([^)]+)\s+(?:Essence|Body Index)\))?', line)
            if item_match:
                item_name = item_match.group(1).strip()
                cost = item_match.group(2) if item_match.group(2) else None
                print(f"  -> Found {current_type}: {item_name} (cost: {cost})")
                items_found.append((current_type, item_name, cost))
            else:
                print(f"  -> NO MATCH for item line")
    
    print("\n" + "=" * 70)
    print(f"Total items found: {len(items_found)}")
    for item_type, name, cost in items_found:
        print(f"  {item_type}: {name} ({cost})")
else:
    print("Cyberware/Bioware section NOT FOUND")
