#!/usr/bin/env python3
"""
Test re-importing Platinum with new cyberware/bioware parsing
"""
import os
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row
import sys
import importlib.util

# Load the module with hyphens in the name (force reload)
import sys
module_path = os.path.join(os.path.dirname(__file__), "import-characters-v3.py")
spec = importlib.util.spec_from_file_location("import_characters_v3", module_path)
module = importlib.util.module_from_spec(spec)
# Remove from cache if exists
if 'import_characters_v3' in sys.modules:
    del sys.modules['import_characters_v3']
spec.loader.exec_module(module)
CharacterImporterV3 = module.CharacterImporterV3

load_dotenv()

def main():
    """Clear Platinum and re-import with new parser"""
    conn = psycopg.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB'),
        row_factory=dict_row
    )
    cursor = conn.cursor()
    
    try:
        # Delete Platinum's data
        print("Deleting existing Platinum data...")
        cursor.execute("DELETE FROM characters WHERE name = 'Kent Jefferies'")
        conn.commit()
        print("  ✓ Deleted")
        
        # Re-import with new parser
        print("\nRe-importing Platinum with new parser...")
        importer = CharacterImporterV3()
        importer.import_character('characters/Platinum.md')
        importer.close()
        
        # Check what was imported
        print("\n" + "=" * 70)
        print("CHECKING IMPORTED CYBERWARE/BIOWARE ITEMS")
        print("=" * 70)
        
        cursor.execute("""
            SELECT c.name, cm.source, cm.source_type, cm.modifier_type,
                   cm.essence_cost, cm.modifier_data
            FROM characters c
            JOIN character_modifiers cm ON c.id = cm.character_id
            WHERE c.name = 'Kent Jefferies'
              AND cm.source_type IN ('cyberware', 'bioware')
              AND cm.modifier_type = 'augmentation'
            ORDER BY cm.source_type, cm.source
        """)
        
        items = cursor.fetchall()
        
        if not items:
            print("\n⚠ No cyberware/bioware items found!")
        else:
            print(f"\nFound {len(items)} cyberware/bioware items:\n")
            
            current_type = None
            for item in items:
                if item['source_type'] != current_type:
                    current_type = item['source_type']
                    print(f"\n{current_type.upper()}:")
                
                if item['source_type'] == 'cyberware':
                    cost = item['essence_cost'] or 0
                    print(f"  - {item['source']}: {cost} Essence")
                else:  # bioware
                    modifier_data = item['modifier_data'] or {}
                    cost = modifier_data.get('body_index_cost', 0)
                    print(f"  - {item['source']}: {cost} Body Index")
        
        print("\n" + "=" * 70)
        
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
