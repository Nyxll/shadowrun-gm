#!/usr/bin/env python3
import glob
import re

files = glob.glob('data-load-final-*.sql')
files.sort()

total_fixed = 0

for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    original = content
    
    # Fix gear.loaded_from: should be ARRAY[]::text[], not '[]'::jsonb
    # loaded_from comes after source_file and before data_quality
    # Pattern: source_file, loaded_from, data_quality
    content = re.sub(
        r"(INSERT INTO gear[^;]*?source_file, loaded_from[^;]*?), '?\[\]'::jsonb,",
        r"\1, ARRAY[]::text[],",
        content
    )
    
    # Also fix any other tables with loaded_from column
    for table in ['powers', 'spells', 'totems', 'metatypes']:
        content = re.sub(
            rf"(INSERT INTO {table}[^;]*?), '?\[\]'::jsonb,(\s*(?:NULL|\d+|'[^']*'|\"[^\"]*\"),\s*(?:FALSE|TRUE|NULL),)",
            r"\1, ARRAY[]::text[],\2",
            content
        )
    
    if content != original:
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)
        total_fixed += 1
        print(f'Fixed {f}')

print(f'\nDone! Fixed {total_fixed} files')
