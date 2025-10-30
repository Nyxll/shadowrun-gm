#!/usr/bin/env python3
"""
Fix ALL schema mismatches in comprehensive_crud.py systematically
This script fixes SQL to match actual schema columns
"""
import re

# Read the current CRUD file
with open('lib/comprehensive_crud.py', 'r', encoding='utf-8') as f:
    content = f.read()

print("Fixing schema mismatches in comprehensive_crud.py...")
print("=" * 70)

# Fix 1: character_spirits - Remove audit columns from SQL
print("\n1. Fixing character_spirits (removing non-existent audit columns)...")
content = re.sub(
    r'INSERT INTO character_spirits \([^)]+\) VALUES \([^)]+\) RETURNING \*',
    lambda m: m.group(0).replace(', created_by', '').replace(', %s', '', 1) if 'created_by' in m.group(0) else m.group(0),
    content
)
content = re.sub(
    r'UPDATE character_spirits SET[^W]+WHERE',
    lambda m: m.group(0).replace('modified_by = %s, ', '').replace('modified_at = CURRENT_TIMESTAMP, ', ''),
    content
)
content = re.sub(
    r'deleted_at = CURRENT_TIMESTAMP, deleted_by = %s',
    'deleted_at = CURRENT_TIMESTAMP',
    content
)
print("   ✓ Removed created_by, modified_by, modified_at, deleted_by from spirits SQL")

# Fix 2: character_foci - Remove audit columns
print("\n2. Fixing character_foci (removing non-existent audit columns)...")
content = re.sub(
    r'INSERT INTO character_foci \([^)]+\) VALUES \([^)]+\) RETURNING \*',
    lambda m: m.group(0).replace(', created_by', '').replace(', %s', '', 1) if 'created_by' in m.group(0) else m.group(0),
    content
)
content = re.sub(
    r'UPDATE character_foci SET[^W]+WHERE',
    lambda m: m.group(0).replace('modified_by = %s, ', '').replace('modified_at = CURRENT_TIMESTAMP, ', ''),
    content
)
print("   ✓ Removed audit columns from foci SQL")

# Fix 3: character_contacts - Remove audit columns
print("\n3. Fixing character_contacts (removing non-existent audit columns)...")
content = re.sub(
    r'INSERT INTO character_contacts \([^)]+\) VALUES \([^)]+\) RETURNING \*',
    lambda m: m.group(0).replace(', created_by', '').replace(', %s', '', 1) if 'created_by' in m.group(0) else m.group(0),
    content
)
content = re.sub(
    r'UPDATE character_contacts SET[^W]+WHERE',
    lambda m: m.group(0).replace('modified_by = %s, ', '').replace('modified_at = CURRENT_TIMESTAMP, ', ''),
    content
)
print("   ✓ Removed audit columns from contacts SQL")

# Fix 4: character_vehicles - Change autopilot to pilot, remove sensor
print("\n4. Fixing character_vehicles (autopilot -> pilot, remove sensor)...")
content = content.replace('autopilot', 'pilot')
content = re.sub(r', sensor = %s', '', content)
content = re.sub(r'sensor,\s*', '', content)
print("   ✓ Changed autopilot to pilot, removed sensor field")

# Fix 5: character_cyberdecks - Fix field names
print("\n5. Fixing character_cyberdecks (field name corrections)...")
content = content.replace('active_memory', 'memory')
content = content.replace('storage_memory', 'storage')
content = content.replace('reaction_increase', 'response_increase')
# Note: programs might map to persona_programs, utilities, or ai_companions
# We'll need to handle this more carefully in the actual operations
print("   ✓ Fixed cyberdeck field names")

# Fix 6: character_edges_flaws - Remove cost field
print("\n6. Fixing character_edges_flaws (removing cost field)...")
content = re.sub(r', cost', '', content)
content = re.sub(r'cost = %s,\s*', '', content)
print("   ✓ Removed cost field from edges_flaws")

# Fix 7: character_modifiers - Use source instead of source_name, is_permanent instead of is_temporary
print("\n7. Fixing character_modifiers (source_name -> source, is_temporary -> is_permanent)...")
content = content.replace('source_name', 'source')
# is_temporary logic needs to be inverted to is_permanent
content = re.sub(
    r'is_temporary = %s',
    'is_permanent = NOT %s',  # Invert the boolean
    content
)
print("   ✓ Fixed modifier field names and boolean logic")

# Fix 8: character_relationships - Restructure to use correct fields
print("\n8. Fixing character_relationships (restructure to schema)...")
# This is complex - relationship_type, relationship_name, data (JSONB)
# entity_name -> relationship_name
# status, notes -> data JSONB
content = content.replace('entity_name', 'relationship_name')
# We'll need to handle the JSONB restructuring in the actual operations
print("   ✓ Mapped entity_name to relationship_name")

# Fix 9: character_active_effects - Restructure to match schema
print("\n9. Fixing character_active_effects (restructure to schema)...")
# This needs careful mapping:
# source -> effect_name
# The schema has many specific fields we need to map to
print("   ✓ Noted active_effects needs manual restructuring")

# Write the fixed file
with open('lib/comprehensive_crud_fixed.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n" + "=" * 70)
print("✓ Created lib/comprehensive_crud_fixed.py with schema fixes")
print("\nNext steps:")
print("1. Review the fixed file")
print("2. Handle complex JSONB mappings manually")
print("3. Test each operation")
print("4. Replace comprehensive_crud.py when verified")
