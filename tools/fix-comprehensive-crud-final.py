#!/usr/bin/env python3
"""
Final fix for comprehensive_crud.py:
1. Filter out 'cyberware', 'bioware', 'description_only' from effects
2. Convert essence_cost from Decimal string to float
"""
import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Read the file
with open('lib/comprehensive_crud.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Filter cyberware effects - add description_only to exclusion list
old_cyber_filter = "if row.get('target_name') and row.get('target_name') != 'cyberware':"
new_cyber_filter = "if row.get('target_name') and row.get('target_name') not in ['cyberware', 'description_only']:"
content = content.replace(old_cyber_filter, new_cyber_filter)

# Fix 2: Filter bioware effects - add description_only to exclusion list  
old_bio_filter = "if row.get('target_name') and row.get('target_name') != 'bioware':"
new_bio_filter = "if row.get('target_name') and row.get('target_name') not in ['bioware', 'description_only']:"
content = content.replace(old_bio_filter, new_bio_filter)

# Fix 3: Convert essence_cost to float in cyberware
old_cyber_cost = """                grouped[source]['essence_cost'] = essence_cost
                grouped[source]['modifier_data'] = row.get('modifier_data') or {}"""
new_cyber_cost = """                # Convert to float if it's a Decimal string
                if essence_cost is not None and isinstance(essence_cost, str):
                    try:
                        essence_cost = float(essence_cost)
                    except (ValueError, TypeError):
                        pass
                grouped[source]['essence_cost'] = essence_cost
                grouped[source]['modifier_data'] = row.get('modifier_data') or {}"""
content = content.replace(old_cyber_cost, new_cyber_cost)

# Write the fixed file
with open('lib/comprehensive_crud.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed comprehensive_crud.py:")
print("  - Filter out 'cyberware', 'bioware', 'description_only' from effects")
print("  - Convert essence_cost from Decimal string to float")
print("\nChanges applied successfully!")
