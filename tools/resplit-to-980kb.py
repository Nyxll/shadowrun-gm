#!/usr/bin/env python3
"""
Resplit SQL data files to be under 980KB each
Organizes INSERT statements by table order and splits into manageable chunks
"""

import os
import re

print('Resplitting files to be under 980KB...\n')

MAX_SIZE = 980 * 1024  # 980KB

# Get the path to the SQL file
script_dir = os.path.dirname(os.path.abspath(__file__))
sql_file_path = os.path.join(script_dir, '..', 'supabase-data-fixed.sql')

# Read the fixed data
with open(sql_file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Reorganize by table order
table_order = [
    'metatypes', 'powers', 'spells', 'totems', 'gear', 'rules_content',
    'campaigns', 'sr_characters', 'character_history', 'character_skills',
    'character_spells', 'character_powers', 'character_contacts', 'character_gear',
    'character_modifiers', 'house_rules', 'rule_application_log',
    'gear_chunk_links', 'query_logs'
]

table_data = {table: [] for table in table_order}

lines = content.split('\n')
current_insert = ''

for line in lines:
    if line.strip().startswith('INSERT INTO'):
        if current_insert:
            for table in table_order:
                if f'INSERT INTO {table}' in current_insert:
                    table_data[table].append(current_insert)
                    break
        current_insert = line
    elif current_insert:
        current_insert += '\n' + line
        if line.strip().endswith(';'):
            for table in table_order:
                if f'INSERT INTO {table}' in current_insert:
                    table_data[table].append(current_insert)
                    break
            current_insert = ''

print('Creating files under 980KB...\n')

current_chunk = []
current_size = 0
chunk_number = 1

for table in table_order:
    for insert in table_data[table]:
        insert_size = len((insert + '\n').encode('utf-8'))
        
        if current_size + insert_size > MAX_SIZE and len(current_chunk) > 0:
            filename = f'data-load-final-{chunk_number}.sql'
            chunk_content = '\n\n'.join(current_chunk)
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(chunk_content)
            
            actual_size = len(chunk_content.encode('utf-8'))
            print(f'✅ {filename:<30} {actual_size/1024:>7.1f}KB')
            
            current_chunk = []
            current_size = 0
            chunk_number += 1
        
        current_chunk.append(insert)
        current_size += insert_size

if len(current_chunk) > 0:
    filename = f'data-load-final-{chunk_number}.sql'
    chunk_content = '\n\n'.join(current_chunk)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(chunk_content)
    
    actual_size = len(chunk_content.encode('utf-8'))
    print(f'✅ {filename:<30} {actual_size/1024:>7.1f}KB')

print(f'\n✅ Created {chunk_number} files, all under 980KB')
