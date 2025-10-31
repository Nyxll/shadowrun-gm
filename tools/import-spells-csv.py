#!/usr/bin/env python3
"""
Import spells from spells.csv into master_spells table
"""
import os
import csv
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

# Read the CSV file
csv_path = r'G:\My Drive\SR-ai\DataTables\spells.csv'

print(f"Reading spells from {csv_path}...")

spells_imported = 0
spells_skipped = 0

with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    
    for row in reader:
        # Skip rows with missing data
        if not row.get('Name') or not row.get('Type'):
            continue
            
        spell_name = row['Name'].strip()
        drain = row.get('Drain', '').strip()
        spell_type = row['Type'].strip()  # M or P
        duration = row.get('Duration', 'I').strip()  # I or S
        spell_class = row.get('Class', 'M').strip()  # C, D, H, I, M
        
        # Map class to category
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
        try:
            cur.execute("""
                INSERT INTO master_spells (
                    spell_name, spell_category, spell_type, 
                    target, duration, drain_code
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                spell_name,
                category,
                spell_type,
                'LOS',  # Default target
                duration,
                drain
            ))
            
            spells_imported += 1
            
        except Exception as e:
            print(f"Error importing '{spell_name}': {e}")
            conn.rollback()
            continue

conn.commit()
cur.close()
conn.close()

print(f"\n✓ Imported {spells_imported} spells")
print(f"✓ Skipped {spells_skipped} duplicates")
print(f"✓ Total: {spells_imported + spells_skipped} spells processed")
