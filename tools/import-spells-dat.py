#!/usr/bin/env python3
"""
Import spells from SPELLS.DAT into master_spells table
"""
import os
import re
from dotenv import load_dotenv
import psycopg2

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=os.getenv('POSTGRES_PORT'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    dbname=os.getenv('POSTGRES_DB')
)

cur = conn.cursor()

# Read the DAT file
dat_path = r'G:\My Drive\SR-ai\DataTables\SPELLS.DAT'

print(f"Reading spells from {dat_path}...")

spells_imported = 0
spells_skipped = 0
current_category = None

with open(dat_path, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        
        # Skip comments and empty lines
        if not line or line.startswith('!'):
            continue
        
        # Check for category headers
        if line.startswith('#'):
            # Extract category from line like "#Combat spells/C"
            match = re.match(r'#(.+?)\s+spells/([CDHIM])', line)
            if match:
                category_name = match.group(1).strip()
                category_code = match.group(2)
                
                category_map = {
                    'C': 'Combat',
                    'D': 'Detection', 
                    'H': 'Health',
                    'I': 'Illusion',
                    'M': 'Manipulation'
                }
                current_category = category_map.get(category_code, category_name)
            continue
        
        # Parse spell line (fixed-width format)
        # Format: Book-Page Name Drain Type Dur Class
        if len(line) < 50:
            continue
        
        try:
            # Extract fields (approximate positions based on format)
            book_page = line[0:10].strip()
            spell_name = line[10:39].strip()
            drain = line[39:59].strip()
            spell_type = line[59:63].strip()  # M or P
            duration = line[63:67].strip()  # I, S, or P
            spell_class = line[67:].strip()  # C, D, H, I, M
            
            if not spell_name or not spell_type:
                continue
            
            # Use current category if available
            if current_category:
                category = current_category
            else:
                # Fallback to class mapping
                class_to_category = {
                    'C': 'Combat',
                    'D': 'Detection',
                    'H': 'Health',
                    'I': 'Illusion',
                    'M': 'Manipulation'
                }
                category = class_to_category.get(spell_class, 'Unknown')
            
            # Check if spell already exists
            cur.execute("""
                SELECT id FROM master_spells 
                WHERE LOWER(spell_name) = LOWER(%s)
            """, (spell_name,))
            
            if cur.fetchone():
                spells_skipped += 1
                continue
            
            # Insert the spell
            cur.execute("""
                INSERT INTO master_spells (
                    spell_name, spell_class, spell_type, 
                    duration, drain_formula
                ) VALUES (%s, %s, %s, %s, %s)
            """, (
                spell_name,
                category,
                spell_type,
                duration,
                drain
            ))
            
            spells_imported += 1
            
        except Exception as e:
            print(f"Error parsing line: {line[:50]}... - {e}")
            continue

conn.commit()
cur.close()
conn.close()

print(f"\n✓ Imported {spells_imported} new spells")
print(f"✓ Skipped {spells_skipped} duplicates")
print(f"✓ Total: {spells_imported + spells_skipped} spells processed")
