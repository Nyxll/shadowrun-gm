#!/usr/bin/env python3
"""
Test to find ALL modifier lines that don't match any parser pattern
This will reveal what patterns are missing from the import parser
"""
import os
import re
from typing import List, Tuple

CHARACTERS_DIR = "characters"

def extract_modifier_lines(filepath: str) -> List[Tuple[str, str, int]]:
    """Extract all modifier lines from cyberware/bioware sections"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    modifier_lines = []
    
    # Find cyberware/bioware section
    section_match = re.search(r'##\s+Cyberware/Bioware.*?\n(.*?)(?=\n##|\Z)', content, re.DOTALL | re.IGNORECASE)
    if not section_match:
        return modifier_lines
    
    section = section_match.group(1)
    lines = section.split('\n')
    
    current_item = None
    line_num = 0
    
    for line in lines:
        line_num += 1
        stripped = line.strip()
        
        # Track current item
        if re.match(r'-\s+\*\*(.+?)\*\*\s*\(([\d.]+)\s+(Essence|Body Index)\)', stripped):
            current_item = re.match(r'-\s+\*\*(.+?)\*\*', stripped).group(1)
            continue
        
        # Check if this is a modifier line (starts with -)
        if stripped.startswith('- ') and current_item:
            modifier_text = stripped[2:].strip()
            # Skip empty lines
            if modifier_text:
                modifier_lines.append((current_item, modifier_text, line_num))
    
    return modifier_lines


def test_pattern(line: str) -> bool:
    """Test if a line matches any known pattern - COPY FROM PARSER"""
    
    # Pattern 1: +XDY Initiative
    if re.match(r'([+-])(\d+)D(\d+)\s+Initiative', line, re.IGNORECASE):
        return True
    
    # Pattern 2: +X ATTRIBUTE(S)
    if re.match(r'([+-]\d+)\s+((?:Body|Quickness|Strength|Charisma|Intelligence|Willpower|Reaction|Essence|Magic)(?:(?:/|,\s*)(?:Body|Quickness|Strength|Charisma|Intelligence|Willpower|Reaction|Essence|Magic))*)', line, re.IGNORECASE):
        return True
    
    # Pattern 3: +X die/dice to physical skills
    if re.match(r'([+-]\d+)\s+(?:die|dice)\s+to\s+physical\s+skills?', line, re.IGNORECASE):
        return True
    
    # Pattern 4: +X die/dice to Knowledge/Language skills
    if re.match(r'([+-]\d+)\s+(?:die|dice)\s+to\s+Knowledge/Language\s+skills?', line, re.IGNORECASE):
        return True
    
    # Pattern 5: +X SPECIFIC_SKILL
    if re.match(r'([+-]\d+)\s+([A-Za-z\s]+?)(?:\s|$)', line):
        return True
    
    # Pattern 6: -X TN
    if re.match(r'([+-]\d+)\s+TN', line, re.IGNORECASE):
        return True
    
    # Pattern 7: Vision enhancements
    if any(keyword in line.lower() for keyword in ['thermographic', 'low-light', 'low light', 'optical magnification', 'flare compensation']):
        return True
    
    # Pattern 8: Task Pool
    if re.match(r'([+-]\d+)\s+Task Pool', line, re.IGNORECASE):
        return True
    
    # Pattern 9: Hacking Pool
    if re.match(r'([+-]\d+)\s+(?:dice?\s+)?for\s+Hacking\s+pool', line, re.IGNORECASE):
        return True
    
    # Pattern 10: Conditional skill bonuses
    if re.match(r'([+-]\d+)\s+(?:dice?\s+)?for\s+(\w+)\s+tests?\s+involving\s+(.+)', line, re.IGNORECASE):
        return True
    
    # Pattern 11: Technical skills
    if re.match(r'([+-]\d+)\s+(?:dice?\s+)?for\s+technical(?:\s+and\s+technical\s+B/R)?\s+skills?', line, re.IGNORECASE):
        return True
    
    # Pattern 12: "Increases ATTRIBUTE by X"
    if re.match(r'Increases?\s+(\w+)\s+by\s+([+-]?\d+)', line, re.IGNORECASE):
        return True
    
    # Pattern 13: Matrix Initiative
    if re.match(r'([+-])(\d+)D(\d+)\s+Matrix\s+Initiative', line, re.IGNORECASE):
        return True
    
    # Pattern 14: Matrix performance
    if 'boosts matrix performance' in line.lower() or 'matrix performance' in line.lower():
        return True
    
    # Pattern 15: Social dice
    if re.match(r'([+-]\d+)\s+social\s+dice?', line, re.IGNORECASE):
        return True
    
    # Pattern 16: Fractional effects
    if re.match(r'(\d+)/(\d+)\s+effect', line, re.IGNORECASE):
        return True
    
    # Pattern 17: Grade/Level descriptors (not actual modifiers)
    if re.match(r'Level\s+\d+|Grade', line, re.IGNORECASE):
        return True
    
    # Pattern 18: Vision Magnification
    if re.match(r'Vision\s+Magnification\s+\d+', line, re.IGNORECASE):
        return True
    
    # Pattern 19: Enhanced with software (in parentheses)
    if re.search(r'Enhanced\s+with.*\(([^)]+)\)', line, re.IGNORECASE):
        return True
    
    return False


def main():
    """Find all unparsed modifier lines"""
    char_files = [f for f in os.listdir(CHARACTERS_DIR) 
                 if f.endswith('.md') and f != 'README.md']
    
    print("="*70)
    print("UNPARSED MODIFIER LINES TEST")
    print("="*70)
    print("Finding all modifier lines that don't match any parser pattern\n")
    
    total_modifiers = 0
    unparsed_modifiers = 0
    unparsed_by_file = {}
    
    for filename in char_files:
        filepath = os.path.join(CHARACTERS_DIR, filename)
        modifier_lines = extract_modifier_lines(filepath)
        
        if not modifier_lines:
            continue
        
        unparsed_in_file = []
        
        for item_name, modifier_text, line_num in modifier_lines:
            total_modifiers += 1
            
            if not test_pattern(modifier_text):
                unparsed_modifiers += 1
                unparsed_in_file.append((item_name, modifier_text, line_num))
        
        if unparsed_in_file:
            unparsed_by_file[filename] = unparsed_in_file
    
    # Report results
    if unparsed_modifiers == 0:
        print("✓ ALL MODIFIERS MATCH A PATTERN!")
        print(f"  Total modifiers checked: {total_modifiers}")
    else:
        print(f"✗ FOUND {unparsed_modifiers} UNPARSED MODIFIERS (out of {total_modifiers} total)")
        print()
        
        for filename, unparsed_list in unparsed_by_file.items():
            print(f"\n{filename}:")
            print("-" * 70)
            for item_name, modifier_text, line_num in unparsed_list:
                print(f"  Line {line_num}: {item_name}")
                print(f"    ❌ {modifier_text}")
    
    print("\n" + "="*70)
    print(f"SUMMARY: {unparsed_modifiers}/{total_modifiers} modifiers need new patterns")
    print("="*70)
    
    return unparsed_modifiers == 0


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
