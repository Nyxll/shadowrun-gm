#!/usr/bin/env python3
"""
Generate SQL INSERT statements for all totems from TOTEMS.csv
Version 2: Includes opposed categories (negative dice modifiers)
"""
import csv
import re

def parse_advantages(advantages_text):
    """Parse advantages text to extract spell categories and bonuses"""
    favored = []
    
    # Common patterns for spell bonuses
    if 'health spell' in advantages_text.lower():
        favored.append('Health')
    if 'combat spell' in advantages_text.lower():
        favored.append('Combat')
    if 'detection spell' in advantages_text.lower():
        favored.append('Detection')
    if 'illusion spell' in advantages_text.lower():
        favored.append('Illusion')
    if 'manipulation spell' in advantages_text.lower():
        favored.append('Manipulation')
    
    return favored

def parse_disadvantages(disadvantages_text):
    """Parse disadvantages text to extract opposed spell categories"""
    opposed = []
    
    # Look for negative dice modifiers for spell categories
    text_lower = disadvantages_text.lower()
    
    # Pattern: "-X dice for/when casting/resisting [category] spells"
    if re.search(r'-\d+\s+dic?e?.*(for|when).*(casting|resist).*combat\s+spell', text_lower):
        opposed.append('Combat')
    if re.search(r'-\d+\s+dic?e?.*(for|when).*(casting|resist).*health\s+spell', text_lower):
        opposed.append('Health')
    if re.search(r'-\d+\s+dic?e?.*(for|when).*(casting|resist).*detection\s+spell', text_lower):
        opposed.append('Detection')
    if re.search(r'-\d+\s+dic?e?.*(for|when).*(casting|resist).*illusion\s+spell', text_lower):
        opposed.append('Illusion')
    if re.search(r'-\d+\s+dic?e?.*(for|when).*(casting|resist).*manipulation\s+spell', text_lower):
        opposed.append('Manipulation')
    
    return opposed

def parse_spirit_type(domains_text, advantages_text):
    """Determine spirit type from domains and advantages"""
    combined = (domains_text + ' ' + advantages_text).lower()
    
    if 'forest' in combined or 'woods' in combined:
        return 'Forest'
    elif 'urban' in combined or 'city' in combined:
        return 'City'
    elif 'mountain' in combined:
        return 'Mountain'
    elif 'sea' in combined or 'ocean' in combined or 'saltwater' in combined:
        return 'Sea'
    elif 'desert' in combined:
        return 'Desert'
    elif 'prairie' in combined or 'field' in combined:
        return 'Prairie'
    elif 'sky' in combined or 'wind' in combined or 'air' in combined:
        return 'Sky'
    elif 'swamp' in combined or 'river' in combined or 'water' in combined:
        return 'Water'
    else:
        return 'Any'

def main():
    """Generate SQL INSERT statements"""
    
    with open('train/DataTables/TOTEMS.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        print("-- All Shadowrun 2nd Edition Totems with Advantages AND Disadvantages")
        print("INSERT INTO totems (totem_name, favored_categories, opposed_categories, bonus_dice, spirit_type, description) VALUES")
        
        inserts = []
        for row in reader:
            name = row['name'].strip()
            domains = row['domains'].strip()
            advantages = row['advantages'].strip()
            disadvantages = row['disadvantages'].strip()
            
            # Parse favored categories (positive bonuses)
            favored = parse_advantages(advantages)
            
            # Parse opposed categories (negative penalties)
            opposed = parse_disadvantages(disadvantages)
            
            # Determine spirit type
            spirit_type = parse_spirit_type(domains, advantages)
            
            # Build description from advantages
            description = f"{advantages[:200]}..." if len(advantages) > 200 else advantages
            
            # Format arrays
            if favored:
                favored_str = "ARRAY[" + ", ".join(f"'{cat}'" for cat in favored) + "]"
            else:
                favored_str = "ARRAY[]::TEXT[]"
            
            if opposed:
                opposed_str = "ARRAY[" + ", ".join(f"'{cat}'" for cat in opposed) + "]"
            else:
                opposed_str = "NULL"
            
            # Build INSERT (escape single quotes in description)
            desc_escaped = description.replace("'", "''")
            insert = f"    ('{name}', {favored_str}, {opposed_str}, 2, '{spirit_type}', '{desc_escaped}'),"
            inserts.append(insert)
        
        # Print all inserts
        for i, insert in enumerate(inserts):
            if i < len(inserts) - 1:
                print(insert)
            else:
                # Last one without comma
                print(insert.rstrip(','))
        
        print("ON CONFLICT (totem_name) DO NOTHING;")
        total = len(inserts)
        print(f"\n-- Total: {total} totems")
        
        # Print summary of opposed categories found
        print("\n-- Totems with opposed categories:")
        with open('train/DataTables/TOTEMS.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                opposed = parse_disadvantages(row['disadvantages'])
                if opposed:
                    print(f"--   {row['name']}: {', '.join(opposed)}")

if __name__ == "__main__":
    main()
