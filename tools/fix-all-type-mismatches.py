#!/usr/bin/env python3
"""
Comprehensive fix for ALL type mismatches in SQL files
Based on schema analysis:
- TEXT[] columns getting '[]'::jsonb → convert to ARRAY[]::text[]
- JSONB columns getting ARRAY[]::text[] → convert to '[]'::jsonb
"""

import os
import re
import glob

print('Fixing ALL type mismatches comprehensively...\n')

# Define which columns should be which type based on schema
TEXT_ARRAY_COLUMNS = {
    'metatypes': ['special_abilities', 'loaded_from'],
    'powers': ['loaded_from'],
    'spells': ['loaded_from'],
    'totems': ['loaded_from'],
    'gear': ['tags', 'loaded_from'],
    'rules_content': ['tags'],
    'query_logs': ['data_sources', 'tables_queried'],
}

JSONB_COLUMNS = {
    'metatypes': ['racial_traits'],
    'powers': ['game_effects', 'levels'],
    'gear': ['base_stats', 'modifiers', 'requirements'],
    'sr_characters': ['attributes', 'skills_data', 'qualities_taken', 'gear_owned', 
                      'cyberware_installed', 'spells_known', 'powers_active', 
                      'contacts_list', 'biography'],
    'character_modifiers': ['modifier_data'],
    'house_rules': ['rule_config'],
    'rule_application_log': ['rule_config_snapshot', 'application_context'],
    'query_logs': ['classification', 'dice_rolls'],
}

def fix_file(filepath):
    """Fix a single SQL file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Strategy: Process each table's INSERT statements
    # First pass: Fix TEXT[] columns (convert '[]'::jsonb to ARRAY[]::text[])
    # Second pass: Fix JSONB columns (convert ARRAY[]::text[] to '[]'::jsonb)
    
    # PASS 1: Fix TEXT[] columns - these should have ARRAY[]::text[], not '[]'::jsonb
    for table in TEXT_ARRAY_COLUMNS.keys():
        pattern = rf'INSERT INTO {table}\s*\([^)]+\)\s*VALUES\s*\([^;]+\);'
        
        def fix_text_arrays(match):
            insert_stmt = match.group(0)
            # Replace '[]'::jsonb with ARRAY[]::text[]
            insert_stmt = re.sub(r"'\[\]'::jsonb", "ARRAY[]::text[]", insert_stmt)
            return insert_stmt
        
        content = re.sub(pattern, fix_text_arrays, content, flags=re.DOTALL)
    
    # PASS 2: Fix JSONB columns - these should have '[]'::jsonb, not ARRAY[]::text[]
    for table in JSONB_COLUMNS.keys():
        pattern = rf'INSERT INTO {table}\s*\([^)]+\)\s*VALUES\s*\([^;]+\);'
        
        def fix_jsonb_arrays(match):
            insert_stmt = match.group(0)
            # Replace ARRAY[]::text[] with '[]'::jsonb
            insert_stmt = re.sub(r"ARRAY\[\]::text\[\]", "'[]'::jsonb", insert_stmt)
            return insert_stmt
        
        content = re.sub(pattern, fix_jsonb_arrays, content, flags=re.DOTALL)
    
    fixes_applied = 0
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        # Count the number of changes
        fixes_applied = len(re.findall(r"ARRAY\[\]::text\[\]", content)) + len(re.findall(r"'\[\]'::jsonb", content))
    
    return fixes_applied

# Process all SQL files
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.join(script_dir, '..')

# Fix the main file
main_file = os.path.join(parent_dir, 'supabase-data-fixed.sql')
if os.path.exists(main_file):
    print('Fixing supabase-data-fixed.sql...')
    fixes = fix_file(main_file)
    print(f'  Applied {fixes} fixes\n')

# Fix all split files
sql_files = glob.glob(os.path.join(parent_dir, 'data-load-final-*.sql'))
sql_files.sort()

print(f'Fixing {len(sql_files)} split files...\n')

total_fixes = 0
for sql_file in sql_files:
    filename = os.path.basename(sql_file)
    fixes = fix_file(sql_file)
    total_fixes += fixes
    if fixes > 0:
        print(f'✓ {filename:<30} {fixes} fixes')

print(f'\n✅ Total fixes applied across all files: {total_fixes}')
