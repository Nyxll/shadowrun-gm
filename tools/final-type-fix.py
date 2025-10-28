#!/usr/bin/env python3
"""
Final comprehensive type fix - handles mixed TEXT[]/JSONB columns in same table
"""

import os
import re
import glob

print('Applying final type fixes...\n')

def fix_gear_table(content):
    """Fix gear table which has both TEXT[] and JSONB columns"""
    # Gear table column order (from schema):
    # base_stats (JSONB), modifiers (JSONB), requirements (JSONB), tags (TEXT[]), 
    # ..., loaded_from (TEXT[])
    
    # Pattern: Find gear INSERTs and fix the tags column specifically
    # tags comes after requirements and before description
    # Pattern: requirements, tags, description
    # We need to replace '[]'::jsonb that appears between two other values where
    # the first is JSONB and we're looking for the tags position
    
    pattern = r"(INSERT INTO gear\s*\([^)]+\)\s*VALUES\s*\([^;]+?'\{\}'::jsonb,\s*)('\[\]'::jsonb)(,\s*(?:NULL|'[^']*'),)"
    content = re.sub(pattern, r"\1ARRAY[]::text[]\3", content, flags=re.DOTALL)
    
    return content

def fix_all_files(filepath):
    """Fix a single SQL file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Fix gear table
    content = fix_gear_table(content)
    
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    return False

# Process all SQL files
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.join(script_dir, '..')

# Fix all split files
sql_files = glob.glob(os.path.join(parent_dir, 'data-load-final-*.sql'))
sql_files.sort()

print(f'Fixing {len(sql_files)} split files...\n')

total_fixed = 0
for sql_file in sql_files:
    filename = os.path.basename(sql_file)
    if fix_all_files(sql_file):
        total_fixed += 1
        print(f'✓ {filename}')

print(f'\n✅ Fixed {total_fixed} files')
