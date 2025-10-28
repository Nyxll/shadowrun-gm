#!/usr/bin/env python3
"""
Update character_modifiers to store original description text from character files
This allows the UI to display the exact text from the markdown files
"""
import os
import re
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor, Json

load_dotenv()

def parse_cyberware_bioware_with_descriptions(filepath: str):
    """Parse character file and extract cyberware/bioware with original modifier text"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Get character name
    name_match = re.search(r'\*\*Name\*\*:\s*(.+)', content)
    if not name_match:
        return None
    
    char_name = name_match.group(1).strip()
    
    # Find cyberware/bioware section
    section_match = re.search(r'##\s+Cyberware/Bioware.*?\n(.*?)(?=\n##|\Z)', content, re.DOTALL | re.IGNORECASE)
    if not section_match:
        return {'name': char_name, 'cyberware': [], 'bioware': []}
    
    section = section_match.group(1)
    
    cyberware = []
    bioware = []
    
    # Parse Cyberware
    cyber_match = re.search(r'###\s+Cyberware(.*?)(?=###|\Z)', section, re.DOTALL | re.IGNORECASE)
    if cyber_match:
        items = re.split(r'\n-\s+\*\*', cyber_match.group(1))
        for item in items[1:]:
            lines = item.split('\n')
            if not lines:
                continue
            
            # Get item name
            name_match = re.match(r'(.+?)\*\*', lines[0])
            if name_match:
                item_name = name_match.group(1).strip()
                
                # Skip "None" entries
                if item_name.upper() in ('NONE', 'N/A', 'NA'):
                    continue
                
                # Collect modifier descriptions (lines starting with "- ")
                descriptions = []
                for line in lines[1:]:
                    line = line.strip()
                    if line.startswith('- '):
                        desc = line[2:].strip()
                        descriptions.append(desc)
                
                cyberware.append({
                    'name': item_name,
                    'descriptions': descriptions
                })
    
    # Parse Bioware
    bio_match = re.search(r'###\s+Bioware(.*?)(?=\n###|\n---|\Z)', section, re.DOTALL | re.IGNORECASE)
    if bio_match:
        items = re.split(r'\n-\s+\*\*', bio_match.group(1))
        for item in items[1:]:
            lines = item.split('\n')
            if not lines:
                continue
            
            # Get item name
            name_match = re.match(r'(.+?)\*\*', lines[0])
            if name_match:
                item_name = name_match.group(1).strip()
                
                # Collect modifier descriptions
                descriptions = []
                for line in lines[1:]:
                    line = line.strip()
                    if line.startswith('- '):
                        desc = line[2:].strip()
                        descriptions.append(desc)
                
                bioware.append({
                    'name': item_name,
                    'descriptions': descriptions
                })
    
    return {
        'name': char_name,
        'cyberware': cyberware,
        'bioware': bioware
    }

def update_character_modifiers(conn, char_data):
    """Update modifier_data with original descriptions"""
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Get character ID
    cur.execute("SELECT id FROM characters WHERE name = %s LIMIT 1", (char_data['name'],))
    char_row = cur.fetchone()
    if not char_row:
        print(f"  ✗ Character '{char_data['name']}' not found in database")
        return
    
    char_id = char_row['id']
    print(f"\n  Updating {char_data['name']} (ID: {char_id})")
    
    # Update cyberware modifiers
    for cyber in char_data['cyberware']:
        # Get the parent modifier for this cyberware
        cur.execute("""
            SELECT id FROM character_modifiers
            WHERE character_id = %s
              AND source = %s
              AND source_type = 'cyberware'
              AND parent_modifier_id IS NULL
            LIMIT 1
        """, (char_id, cyber['name']))
        
        parent_row = cur.fetchone()
        if not parent_row:
            print(f"    ⚠ Cyberware '{cyber['name']}' not found")
            continue
        
        parent_id = parent_row['id']
        
        # Get child modifiers for this cyberware
        cur.execute("""
            SELECT id, modifier_type, target_name, modifier_value
            FROM character_modifiers
            WHERE parent_modifier_id = %s
            ORDER BY id
        """, (parent_id,))
        
        child_rows = cur.fetchall()
        
        # Match descriptions to child modifiers
        # This is tricky because we need to match parsed modifiers to original text
        # For now, just store all descriptions in order
        for i, child in enumerate(child_rows):
            if i < len(cyber['descriptions']):
                description = cyber['descriptions'][i]
                
                # Update modifier_data with description
                cur.execute("""
                    UPDATE character_modifiers
                    SET modifier_data = COALESCE(modifier_data, '{}'::jsonb) || %s::jsonb
                    WHERE id = %s
                """, (Json({'description': description}), child['id']))
                
                print(f"    ✓ {cyber['name']}: '{description}'")
    
    # Update bioware modifiers
    for bio in char_data['bioware']:
        # Get the parent modifier for this bioware
        cur.execute("""
            SELECT id FROM character_modifiers
            WHERE character_id = %s
              AND source = %s
              AND source_type = 'bioware'
              AND parent_modifier_id IS NULL
            LIMIT 1
        """, (char_id, bio['name']))
        
        parent_row = cur.fetchone()
        if not parent_row:
            print(f"    ⚠ Bioware '{bio['name']}' not found")
            continue
        
        parent_id = parent_row['id']
        
        # Get child modifiers for this bioware
        cur.execute("""
            SELECT id, modifier_type, target_name, modifier_value
            FROM character_modifiers
            WHERE parent_modifier_id = %s
            ORDER BY id
        """, (parent_id,))
        
        child_rows = cur.fetchall()
        
        # Match descriptions to child modifiers
        for i, child in enumerate(child_rows):
            if i < len(bio['descriptions']):
                description = bio['descriptions'][i]
                
                # Update modifier_data with description
                cur.execute("""
                    UPDATE character_modifiers
                    SET modifier_data = COALESCE(modifier_data, '{}'::jsonb) || %s::jsonb
                    WHERE id = %s
                """, (Json({'description': description}), child['id']))
                
                print(f"    ✓ {bio['name']}: '{description}'")
    
    conn.commit()
    cur.close()

def main():
    """Update all characters"""
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB')
    )
    
    char_dir = 'characters'
    files = [f for f in os.listdir(char_dir) if f.endswith('.md') and f != 'README.md']
    
    print("="*70)
    print("UPDATING MODIFIER DESCRIPTIONS")
    print("="*70)
    print(f"Processing {len(files)} character files\n")
    
    for filename in files:
        filepath = os.path.join(char_dir, filename)
        try:
            char_data = parse_cyberware_bioware_with_descriptions(filepath)
            if char_data:
                update_character_modifiers(conn, char_data)
        except Exception as e:
            print(f"  ✗ Error processing {filename}: {e}")
            import traceback
            traceback.print_exc()
    
    conn.close()
    
    print("\n" + "="*70)
    print("UPDATE COMPLETE")
    print("="*70)

if __name__ == "__main__":
    main()
