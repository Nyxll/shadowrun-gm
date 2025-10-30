#!/usr/bin/env python3
"""
Import master spell data from SPELLS.csv into master_spells table
"""
import os
import csv
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_values

# Load environment variables
load_dotenv()

# Spell class mapping from CSV to database
CLASS_MAP = {
    'C': 'combat',
    'D': 'detection',
    'H': 'health',
    'I': 'illusion',
    'M': 'manipulation'
}

# Type mapping
TYPE_MAP = {
    'M': 'mana',
    'P': 'physical'
}

# Duration mapping
DURATION_MAP = {
    'I': 'instant',
    'S': 'sustained',
    'P': 'permanent'
}

def parse_spell_csv(csv_path):
    """Parse SPELLS.csv and return list of spell dictionaries"""
    spells = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Skip incomplete rows
            if not row.get('Name') or not row.get('Drain'):
                continue
                
            spell = {
                'spell_name': row['Name'].strip(),
                'spell_class': CLASS_MAP.get(row['Class'], 'combat'),
                'spell_type': TYPE_MAP.get(row['Type'], 'mana'),
                'duration': DURATION_MAP.get(row['Duration'], 'instant'),
                'drain_formula': row['Drain'].strip(),
                'book_reference': row.get('Book-Page', '').strip() or None,
                'is_house_rule': False
            }
            spells.append(spell)
    
    return spells

def import_spells(conn, spells):
    """Import spells into master_spells table"""
    cursor = conn.cursor()
    
    # Prepare data for bulk insert
    values = [
        (
            s['spell_name'],
            s['spell_class'],
            s['spell_type'],
            s['duration'],
            s['drain_formula'],
            s['book_reference'],
            s['is_house_rule']
        )
        for s in spells
    ]
    
    # Use ON CONFLICT to handle duplicates
    insert_query = """
        INSERT INTO master_spells 
            (spell_name, spell_class, spell_type, duration, drain_formula, book_reference, is_house_rule)
        VALUES %s
        ON CONFLICT (spell_name) DO UPDATE SET
            spell_class = EXCLUDED.spell_class,
            spell_type = EXCLUDED.spell_type,
            duration = EXCLUDED.duration,
            drain_formula = EXCLUDED.drain_formula,
            book_reference = EXCLUDED.book_reference,
            updated_at = NOW()
    """
    
    execute_values(cursor, insert_query, values)
    conn.commit()
    
    print(f"✓ Imported {len(spells)} spells into master_spells table")
    cursor.close()

def main():
    """Main import function"""
    # Path to SPELLS.csv
    csv_path = r'G:\My Drive\SR-ai\DataTables\SPELLS.csv'
    
    if not os.path.exists(csv_path):
        print(f"ERROR: SPELLS.csv not found at {csv_path}")
        return
    
    print(f"Reading spells from {csv_path}...")
    spells = parse_spell_csv(csv_path)
    print(f"Found {len(spells)} spells")
    
    # Connect to database
    try:
        conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST'),
            port=os.getenv('POSTGRES_PORT'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            dbname=os.getenv('POSTGRES_DB')
        )
        
        print("Importing spells...")
        import_spells(conn, spells)
        
        # Verify import
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM master_spells WHERE is_house_rule = FALSE")
        count = cursor.fetchone()[0]
        print(f"✓ Total canonical spells in database: {count}")
        
        cursor.close()
        conn.close()
        
        print("\n✓ Import complete!")
        
    except Exception as e:
        print(f"ERROR: {e}")
        raise

if __name__ == "__main__":
    main()
