#!/usr/bin/env python3
import glob
import re

files = glob.glob('data-load-final-*.sql')
files.sort()

for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Fix metatypes: special_abilities should be ARRAY[]::text[], not '[]'::jsonb
    # Pattern: special_abilities comes before racial_traits
    # So we replace '[]'::jsonb, '{}'::jsonb with ARRAY[]::text[], '{}'::jsonb
    original = content
    content = re.sub(
        r"(INSERT INTO metatypes[^;]*?)'\[\]'::jsonb,\s*'\{\}'::jsonb",
        r"\1ARRAY[]::text[], '{}'::jsonb",
        content
    )
    
    if content != original:
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f'Fixed {f}')

print('Done!')
