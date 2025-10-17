#!/usr/bin/env python3
"""
Load Shadowrun 2E DAT files (gear.dat, bioware.dat) into the gear table
"""

import psycopg2
import psycopg2.extras
import re
import json
from pathlib import Path
import logging
from typing import Dict, List, Optional, Tuple
import os
import sys
from dotenv import load_dotenv

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

# Database configuration
db_config = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', 5432)),
    'database': os.getenv('POSTGRES_DB', 'postgres'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', '')
}

# Type definitions from gear.dat
TYPE_DEFINITIONS = {
    '0-1': {'name': 'Edged weapon', 'fields': ['Concealability', 'Reach', 'Damage', 'Weight', 'Availability', '$Cost', 'Street Index']},
    '0-2': {'name': 'Bow and crossbow', 'fields': ['Concealability', 'Str.Min.', 'Damage', 'Weight', 'Availability', '$Cost', 'Street Index']},
    '0-3': {'name': 'Firearms', 'fields': ['Concealability', 'Ammunition', 'Mode', 'Damage', 'Weight', 'Availability', '$Cost', 'Street Index', 'Accessories']},
    '0-4': {'name': 'Rockets and Missiles', 'fields': ['Intelligence', 'Damage', 'Weight', 'Availability', '$Cost', 'Street Index']},
    '0-5': {'name': 'Ammunition', 'fields': ['Concealability', 'Damage', 'Weight', 'Availability', '$Cost', 'Street Index']},
    '0-6': {'name': 'Firearms Accessories', 'fields': ['Mount', 'Concealability', 'Rating', 'Weight', 'Availability', '$Cost', 'Street Index']},
    '0-7': {'name': 'Explosives', 'fields': ['Concealability', 'Rating', 'Weight', 'Availability', '$Cost', 'Street Index']},
    '0-8': {'name': 'Clothing and Armor', 'fields': ['Concealability', 'Ballistic', 'Impact', 'Weight', 'Availability', '$Cost', 'Street Index']},
    '0-9': {'name': 'S+S Vision Enhancers', 'fields': ['Concealability', 'Magnification', 'Weight', 'Availability', '$Cost', 'Street Index']},
    '0-10': {'name': 'Surveillance and Security', 'fields': ['Concealability', 'Weight', 'Availability', '$Cost', 'Street Index']},
    '0-11': {'name': 'Cyberdecks', 'fields': ['Persona', 'Hardening', 'Memory', 'Storage', 'Load', 'I/O', 'Availability', '$Cost', 'Street Index']},
    '0-12': {'name': 'Cyberdeck Other', 'fields': ['Availability', '$Cost', 'Street Index']},
    '0-13': {'name': 'Biotech', 'fields': ['Rating', 'Availability', 'Weight', '$Cost', 'Street Index']},
    '0-14': {'name': 'Lifestyle', 'fields': ['Concealability', 'Weight', 'Availability', '$Cost', 'Street Index']},
    '0-15': {'name': 'Magical Equipment', 'fields': ['Availability', '$Cost', 'Street Index']},
    '0-16': {'name': 'Extras', 'fields': ['$Cost']},
    '0-17': {'name': 'Cars', 'fields': ['Handling', 'Speed', 'Body', 'Armor', 'Sig', 'Apilot', 'Availability', '$Cost', 'Street Index']},
    '0-18': {'name': 'Vehiclegear', 'fields': ['Availability', '$Cost', 'Street Index']},
    '0-19': {'name': 'VehicleFire', 'fields': ['Type', 'Ammunition', 'Mode', 'Damage', 'Weight', 'Availability', '$Cost', 'Street Index']},
    '0-20': {'name': 'Chips', 'fields': ['Type', 'Rating', 'Memory', 'Availability', '$Cost', 'Street Index']},
    '0-21': {'name': 'Stuff With Ratings', 'fields': ['Concealability', 'Rating', 'Weight', 'Availability', '$Cost', 'Street Index']},
    '0-22': {'name': 'Drugs', 'fields': ['Addiction', 'Tolerance', 'Strength', 'Availability', '$Cost', 'Street Index']},
    '0-23': {'name': 'Vehicle modifications', 'fields': ['$Cost', 'Equipment', 'CF']},
}

# Category mapping
CATEGORY_MAP = {
    'Edged weapon': 'weapon',
    'Bow and crossbow': 'weapon',
    'Firearms': 'weapon',
    'Rockets and Missiles': 'weapon',
    'Ammunition': 'weapon',
    'Firearms Accessories': 'weapon',
    'Explosives': 'weapon',
    'Clothing and Armor': 'armor',
    'S+S Vision Enhancers': 'magical',
    'Surveillance and Security': 'magical',
    'Cyberdecks': 'cyberware',
    'Cyberdeck Other': 'cyberware',
    'Biotech': 'bioware',
    'Lifestyle': 'magical',
    'Magical Equipment': 'magical',
    'Extras': 'magical',
    'Cars': 'vehicle',
    'Vehiclegear': 'vehicle',
    'VehicleFire': 'weapon',
    'Chips': 'cyberware',
    'Stuff With Ratings': 'magical',
    'Drugs': 'drug',
    'Vehicle modifications': 'vehicle',
}

SUBCATEGORY_MAP = {
    'Edged weapon': 'melee',
    'Bow and crossbow': 'bow',
    'Firearms': 'firearm',
    'Sniper rifles': 'sniper_rifle',
    'Assault rifles': 'assault_rifle',
    'Sport rifles': 'sport_rifle',
    'Heavy Pistols': 'heavy_pistol',
    'Light Pistols': 'light_pistol',
    'Shotguns': 'shotgun',
    'Submachine Guns': 'smg',
}


def parse_dat_file(filepath: Path) -> List[Dict]:
    """Parse a DAT file and return list of items"""
    items = []
    current_type = None
    current_category = None
    current_subcategory = None
    hierarchy = []  # Track category hierarchy
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        for line_num, line in enumerate(f, 1):
            line = line.rstrip('\n\r')
            
            # Skip comments and empty lines
            if not line or line.startswith('!'):
                continue
            
            # Type definition line (0-1|Name|...)
            if line.startswith('0-'):
                match = re.match(r'(0-\d+)\|([^|]+)\|', line)
                if match:
                    type_id = match.group(1)
                    type_name = match.group(2)
                    current_type = type_id
                    logger.debug(f"Found type definition: {type_id} = {type_name}")
                continue
            
            # Category/hierarchy lines (1-5 prefix without *)
            level_match = re.match(r'^(\d+)-([^*].*)$', line)
            if level_match:
                level = int(level_match.group(1))
                name = level_match.group(2).strip()
                
                # Update hierarchy
                hierarchy = hierarchy[:level-1] + [name]
                
                if level == 1:
                    current_category = name
                    current_subcategory = None
                elif level >= 2:
                    current_subcategory = name
                
                logger.debug(f"Hierarchy level {level}: {' > '.join(hierarchy)}")
                continue
            
            # Item line: "4-* Ares Monosword                 1|3|1|(STR+3)M|2|4/24hrs|1000|1|"
            # Format: LEVEL-* NAME  TYPE|STATS
            item_match = re.match(r'^[45]-\*\s+(.+?)\s+(\d+)\|(.+)$', line)
            if item_match:
                name = item_match.group(1).strip()
                type_id = '0-' + item_match.group(2)
                stats_str = item_match.group(3)
                
                if type_id not in TYPE_DEFINITIONS:
                    logger.warning(f"Unknown type {type_id} for item {name}")
                    continue
                
                type_def = TYPE_DEFINITIONS[type_id]
                stats = stats_str.split('|')
                
                # Parse stats into dict
                base_stats = {}
                for i, field in enumerate(type_def['fields']):
                    if i < len(stats):
                        value = stats[i].strip()
                        if value and value != '-':
                            # Clean field name
                            clean_field = field.replace('$', '').replace('.', '').lower().replace(' ', '_')
                            base_stats[clean_field] = value
                
                # Determine category and subcategory
                category = CATEGORY_MAP.get(type_def['name'], 'magical')
                subcategory = current_subcategory or type_def['name']
                
                # Map subcategory
                if subcategory in SUBCATEGORY_MAP:
                    subcategory = SUBCATEGORY_MAP[subcategory]
                else:
                    subcategory = subcategory.lower().replace(' ', '_')
                
                # Extract cost, availability, street_index
                cost = None
                availability = None
                street_index = None
                
                if 'cost' in base_stats:
                    try:
                        cost = int(base_stats['cost'].replace(',', ''))
                        del base_stats['cost']
                    except:
                        pass
                
                if 'availability' in base_stats:
                    availability = base_stats['availability']
                    del base_stats['availability']
                
                if 'street_index' in base_stats:
                    try:
                        street_index = float(base_stats['street_index'])
                        del base_stats['street_index']
                    except:
                        pass
                
                item = {
                    'name': name,
                    'category': category,
                    'subcategory': subcategory,
                    'base_stats': base_stats,
                    'cost': cost,
                    'availability': availability,
                    'street_index': street_index,
                    'source': filepath.name,
                    'hierarchy': ' > '.join(hierarchy),
                }
                
                items.append(item)
                logger.debug(f"Parsed item: {name} ({category}/{subcategory})")
    
    return items


def load_items_to_db(items: List[Dict], source_file: str, data_quality: int = 7):
    """Load items into database"""
    conn = psycopg2.connect(**db_config)
    conn.autocommit = True  # Auto-commit each item individually
    
    inserted = 0
    updated = 0
    skipped = 0
    errors = []
    
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            for item in items:
                try:
                    # Check if item exists
                    cur.execute("""
                        SELECT id, data_quality FROM gear 
                        WHERE LOWER(TRIM(name)) = LOWER(TRIM(%s)) 
                        AND category = %s
                    """, (item['name'], item['category']))
                    
                    existing = cur.fetchone()
                    
                    if existing:
                        if data_quality > existing['data_quality']:
                            # Update with better quality data
                            cur.execute("""
                                UPDATE gear SET
                                    subcategory = %s,
                                    base_stats = %s,
                                    cost = %s,
                                    availability = %s,
                                    street_index = %s,
                                    source_file = %s,
                                    data_quality = %s,
                                    updated_at = NOW()
                                WHERE id = %s
                            """, (
                                item['subcategory'],
                                json.dumps(item['base_stats']),
                                item['cost'],
                                item['availability'],
                                item['street_index'],
                                source_file,
                                data_quality,
                                existing['id']
                            ))
                            updated += 1
                            logger.info(f"* Updated: {item['name']}")
                        else:
                            skipped += 1
                            logger.debug(f"- Skipped: {item['name']} (existing quality >= new)")
                    else:
                        # Insert new item
                        cur.execute("""
                            INSERT INTO gear (
                                name, category, subcategory, base_stats,
                                cost, availability, street_index,
                                data_source, source_file, loaded_from, data_quality,
                                modifiers, requirements, tags
                            ) VALUES (
                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                            )
                        """, (
                            item['name'],
                            item['category'],
                            item['subcategory'],
                            json.dumps(item['base_stats']),
                            item['cost'],
                            item['availability'],
                            item['street_index'],
                            'dat',
                            source_file,
                            [source_file],
                            data_quality,
                            json.dumps({}),
                            json.dumps({}),
                            []
                        ))
                        inserted += 1
                        logger.info(f"+ Inserted: {item['name']}")
                
                except Exception as e:
                    errors.append(f"{item['name']}: {str(e)}")
                    logger.error(f"Error loading {item['name']}: {e}")
                    # Continue with next item since autocommit is on
        
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise
    finally:
        conn.close()
    
    # Print report
    print("\n" + "=" * 60)
    print(f"LOADED {source_file}")
    print("=" * 60)
    print(f"+ Inserted:  {inserted} new items")
    print(f"* Updated:   {updated} items")
    print(f"- Skipped:   {skipped} duplicates")
    if errors:
        print(f"\nX Errors: {len(errors)}")
        for error in errors[:10]:
            print(f"  {error}")
    print("=" * 60)
    
    return inserted, updated, skipped


def main():
    """Main entry point"""
    data_dir = Path(r'G:\My Drive\SR-ai\DataTables')
    
    # Files to load
    files_to_load = [
        ('gear.dat', 7),      # Quality 7 for DAT files
        ('bioware.dat', 7),
    ]
    
    total_inserted = 0
    total_updated = 0
    total_skipped = 0
    
    for filename, quality in files_to_load:
        filepath = data_dir / filename
        
        if not filepath.exists():
            logger.warning(f"File not found: {filepath}")
            continue
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing {filename}...")
        logger.info(f"{'='*60}")
        
        # Parse file
        items = parse_dat_file(filepath)
        logger.info(f"Parsed {len(items)} items from {filename}")
        
        # Load to database
        inserted, updated, skipped = load_items_to_db(items, filename, quality)
        
        total_inserted += inserted
        total_updated += updated
        total_skipped += skipped
    
    # Final summary
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    print(f"Total Inserted:  {total_inserted}")
    print(f"Total Updated:   {total_updated}")
    print(f"Total Skipped:   {total_skipped}")
    print(f"Total Processed: {total_inserted + total_updated + total_skipped}")
    print("=" * 60)


if __name__ == '__main__':
    main()
