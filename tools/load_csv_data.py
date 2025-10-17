#!/usr/bin/env python3
"""
Load reference data from CSV files in G:\My Drive\SR-ai\DataTables

This tool loads comprehensive reference data from CSV files:
- SPELLS.csv - All spells with drain, type, duration, class
- TOTEMS.csv - All totems and loa with advantages/disadvantages
- POWERS.csv - All adept powers with costs
"""

import csv
import os
import re
from pathlib import Path
from typing import List, Dict, Any
import psycopg2
from psycopg2.extras import Json
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

CSV_PATH = Path("G:/My Drive/SR-ai/DataTables")

class CSVDataLoader:
    def __init__(self, csv_path: Path):
        self.csv_path = csv_path
        self.conn = None
        
    def connect(self):
        """Connect to PostgreSQL database"""
        self.conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST'),
            port=os.getenv('POSTGRES_PORT'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            database=os.getenv('POSTGRES_DB')
        )
        self.conn.autocommit = True  # Use autocommit to avoid transaction issues with duplicates
        print(f"Connected to {os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}")
        
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def parse_spell_category(self, class_code: str) -> str:
        """Parse spell class code to category"""
        mapping = {
            'C': 'Combat',
            'D': 'Detection',
            'H': 'Health',
            'I': 'Illusion',
            'M': 'Manipulation'
        }
        return mapping.get(class_code, 'Unknown')
    
    def parse_spell_type(self, type_code: str) -> str:
        """Parse spell type code"""
        mapping = {
            'P': 'Physical',
            'M': 'Mana'
        }
        return mapping.get(type_code, 'Unknown')
    
    def parse_duration(self, duration_code: str) -> str:
        """Parse duration code"""
        mapping = {
            'I': 'Instant',
            'S': 'Sustained',
            'P': 'Permanent'
        }
        return mapping.get(duration_code, 'Unknown')
    
    def load_spells(self):
        """Load spells from SPELLS.csv"""
        print("\n=== Loading Spells from CSV ===")
        
        csv_file = self.csv_path / "SPELLS.csv"
        if not csv_file.exists():
            print(f"Error: {csv_file} not found")
            return
        
        cursor = self.conn.cursor()
        loaded = 0
        skipped = 0
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    # Parse the data
                    name = row['Name'].strip()
                    category = self.parse_spell_category(row['Class'])
                    spell_type = self.parse_spell_type(row['Type'])
                    duration = self.parse_duration(row['Duration'])
                    drain_code = row['Drain'].strip()
                    
                    # Extract target type from drain code if present
                    # Most spells use LOS, some use touch, etc.
                    target_type = "LOS"  # Default
                    
                    cursor.execute("""
                        INSERT INTO spells (name, category, spell_type, target_type, duration, drain_code, page_reference)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (name, category, spell_type, target_type, duration, drain_code, row['Book-Page']))
                    
                    loaded += 1
                    if loaded % 20 == 0:
                        print(f"  Loaded {loaded} spells...")
                        
                except psycopg2.IntegrityError as e:
                    # Duplicate - just skip it, don't rollback
                    skipped += 1
                except Exception as e:
                    print(f"  ERROR loading {row.get('Name', 'unknown')}: {type(e).__name__}: {e}")
                    import traceback
                    traceback.print_exc()
                    raise  # Re-raise to stop processing
        
        print(f"Loaded {loaded} spells ({skipped} skipped as duplicates)")
    
    def load_totems(self):
        """Load totems from TOTEMS.csv"""
        print("\n=== Loading Totems from CSV ===")
        
        csv_file = self.csv_path / "TOTEMS.csv"
        if not csv_file.exists():
            print(f"Error: {csv_file} not found")
            return
        
        cursor = self.conn.cursor()
        loaded = 0
        skipped = 0
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    name = row['name'].strip()
                    advantages = row['advantages'].strip()
                    disadvantages = row['disadvantages'].strip()
                    description = row['domains'].strip() if row['domains'].strip() else f"Totem: {name}"
                    
                    cursor.execute("""
                        INSERT INTO totems (name, description, advantages, disadvantages, page_reference)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (name, description, advantages, disadvantages, row['source']))
                    
                    loaded += 1
                    if loaded % 10 == 0:
                        print(f"  Loaded {loaded} totems...")
                        
                except psycopg2.IntegrityError:
                    # Duplicate - just skip it, don't rollback
                    skipped += 1
                except Exception as e:
                    print(f"  Error loading {row.get('name', 'unknown')}: {e}")
                    raise  # Re-raise to stop processing
        
        print(f"Loaded {loaded} totems ({skipped} skipped as duplicates)")
    
    def load_powers(self):
        """Load adept powers from POWERS.csv"""
        print("\n=== Loading Adept Powers from CSV ===")
        
        csv_file = self.csv_path / "POWERS.csv"
        if not csv_file.exists():
            print(f"Error: {csv_file} not found")
            return
        
        cursor = self.conn.cursor()
        loaded = 0
        skipped = 0
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    name = row['Description'].strip()
                    cost = float(row['Cost'])
                    modifiers = row['Modifiers'].strip() if row['Modifiers'].strip() else None
                    
                    # Build description from modifiers if present
                    description = modifiers if modifiers else f"Adept power: {name}"
                    
                    cursor.execute("""
                        INSERT INTO powers (name, power_type, power_point_cost, description, page_reference)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (name, "adept", cost, description, row['Book-Page']))
                    
                    loaded += 1
                    if loaded % 20 == 0:
                        print(f"  Loaded {loaded} powers...")
                        
                except psycopg2.IntegrityError:
                    # Duplicate - just skip it, don't rollback
                    skipped += 1
                except Exception as e:
                    print(f"  Error loading {row.get('Description', 'unknown')}: {e}")
                    raise  # Re-raise to stop processing
        
        print(f"Loaded {loaded} adept powers ({skipped} skipped as duplicates)")
    
    def run(self):
        """Run the CSV data loading process"""
        print("=" * 60)
        print("SHADOWRUN CSV DATA LOADER")
        print("=" * 60)
        print(f"Loading from: {self.csv_path}")
        
        try:
            self.connect()
            
            # Load all CSV data
            self.load_spells()
            self.load_totems()
            self.load_powers()
            
            print("\n" + "=" * 60)
            print("CSV DATA LOADING COMPLETE!")
            print("=" * 60)
            
        finally:
            self.close()


if __name__ == "__main__":
    loader = CSVDataLoader(CSV_PATH)
    loader.run()
