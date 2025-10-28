#!/usr/bin/env python3
"""
Enrich character data by looking up missing information from RAG database
Fills in details for gear, weapons, armor, vehicles, edges, flaws, and spells
"""
import os
import re
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row

load_dotenv()

def search_gear(cursor, item_name):
    """Search gear tables for item information"""
    # Try gear table first
    cursor.execute("""
        SELECT * FROM gear
        WHERE LOWER(name) = LOWER(%s)
        OR LOWER(name) LIKE LOWER(%s)
        LIMIT 1
    """, (item_name, f'%{item_name}%'))
    
    result = cursor.fetchone()
    if result:
        return result
    
    # Try gear_items table
    cursor.execute("""
        SELECT * FROM gear_items
        WHERE LOWER(name) = LOWER(%s)
        OR LOWER(name) LIKE LOWER(%s)
        LIMIT 1
    """, (item_name, f'%{item_name}%'))
    
    return cursor.fetchone()

def search_quality(cursor, quality_name):
    """Search qualities table for edge/flaw information"""
    cursor.execute("""
        SELECT * FROM qualities
        WHERE LOWER(name) = LOWER(%s)
        OR LOWER(name) LIKE LOWER(%s)
        LIMIT 1
    """, (quality_name, f'%{quality_name}%'))
    
    return cursor.fetchone()

def search_spell(cursor, spell_name):
    """Search spells table for spell information"""
    cursor.execute("""
        SELECT * FROM spells
        WHERE LOWER(name) = LOWER(%s)
        OR LOWER(name) LIKE LOWER(%s)
        LIMIT 1
    """, (spell_name, f'%{spell_name}%'))
    
    return cursor.fetchone()

def extract_weapon_stats(content, weapon_name):
    """Extract weapon statistics from RAG content"""
    stats = {}
    
    # Look for damage pattern
    damage_patterns = [
        rf'{re.escape(weapon_name)}.*?Damage[:\s]+([0-9]+[MDLS][0-9]*)',
        rf'Damage[:\s]+([0-9]+[MDLS][0-9]*)',
    ]
    for pattern in damage_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            stats['damage'] = match.group(1)
            break
    
    # Look for concealability
    conceal_patterns = [
        rf'{re.escape(weapon_name)}.*?Conceal(?:ability)?[:\s]+([0-9]+)',
        rf'Conceal(?:ability)?[:\s]+([0-9]+)',
    ]
    for pattern in conceal_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            stats['conceal'] = int(match.group(1))
            break
    
    # Look for ammo capacity
    ammo_patterns = [
        rf'{re.escape(weapon_name)}.*?Ammo[:\s]+([0-9]+\([cm]\))',
        rf'Ammo[:\s]+([0-9]+\([cm]\))',
    ]
    for pattern in ammo_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            stats['ammo_capacity'] = match.group(1)
            break
    
    return stats

def extract_armor_stats(content, armor_name):
    """Extract armor statistics from RAG content"""
    stats = {}
    
    # Look for ballistic/impact ratings
    rating_patterns = [
        rf'{re.escape(armor_name)}.*?Rating[:\s]+([0-9]+)/([0-9]+)',
        rf'Ballistic[:\s]+([0-9]+).*?Impact[:\s]+([0-9]+)',
    ]
    for pattern in rating_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            stats['ballistic_rating'] = int(match.group(1))
            stats['impact_rating'] = int(match.group(2))
            break
    
    # Look for concealability
    conceal_patterns = [
        rf'{re.escape(armor_name)}.*?Conceal(?:ability)?[:\s]+([0-9]+)',
        rf'Conceal(?:ability)?[:\s]+([0-9]+)',
    ]
    for pattern in conceal_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            stats['conceal'] = int(match.group(1))
            break
    
    return stats

def extract_cyberware_stats(content, cyber_name):
    """Extract cyberware statistics from RAG content"""
    stats = {}
    
    # Look for essence cost
    essence_patterns = [
        rf'{re.escape(cyber_name)}.*?Essence[:\s]+([\d.]+)',
        rf'Essence[:\s]+([\d.]+)',
    ]
    for pattern in essence_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            stats['essence_cost'] = float(match.group(1))
            break
    
    # Look for cost in nuyen
    cost_patterns = [
        rf'{re.escape(cyber_name)}.*?Cost[:\s]+([0-9,]+)¥',
        rf'Cost[:\s]+([0-9,]+)¥',
    ]
    for pattern in cost_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            stats['cost'] = int(match.group(1).replace(',', ''))
            break
    
    return stats

def enrich_weapons(conn):
    """Enrich weapon data from gear tables"""
    cursor = conn.cursor()
    
    # Get all weapons missing data
    cursor.execute("""
        SELECT id, gear_name, damage, conceal, ammo_capacity
        FROM character_gear
        WHERE gear_type = 'weapon'
        AND (damage IS NULL OR conceal IS NULL OR ammo_capacity IS NULL)
    """)
    
    weapons = cursor.fetchall()
    print(f"\nEnriching {len(weapons)} weapons...")
    
    for weapon in weapons:
        print(f"  Looking up: {weapon['gear_name']}")
        
        # Search gear tables
        gear_data = search_gear(cursor, weapon['gear_name'])
        
        if gear_data:
            # Update weapon with found stats
            updates = []
            values = []
            
            if gear_data.get('damage') and not weapon['damage']:
                updates.append("damage = %s")
                values.append(gear_data['damage'])
                print(f"    Found damage: {gear_data['damage']}")
            
            if gear_data.get('conceal') and not weapon['conceal']:
                updates.append("conceal = %s")
                values.append(gear_data['conceal'])
                print(f"    Found conceal: {gear_data['conceal']}")
            
            if gear_data.get('ammo') and not weapon['ammo_capacity']:
                updates.append("ammo_capacity = %s")
                values.append(gear_data['ammo'])
                print(f"    Found ammo: {gear_data['ammo']}")
            
            if updates:
                values.append(weapon['id'])
                cursor.execute(f"""
                    UPDATE character_gear
                    SET {', '.join(updates)}
                    WHERE id = %s
                """, values)
        else:
            print(f"    Not found in gear tables")
    
    conn.commit()
    print("  ✓ Weapons enriched")

def enrich_armor(conn):
    """Enrich armor data from gear tables"""
    cursor = conn.cursor()
    
    # Get all armor missing data
    cursor.execute("""
        SELECT id, gear_name, ballistic_rating, impact_rating, conceal
        FROM character_gear
        WHERE gear_type = 'armor'
        AND (ballistic_rating IS NULL OR impact_rating IS NULL OR conceal IS NULL)
    """)
    
    armor_items = cursor.fetchall()
    print(f"\nEnriching {len(armor_items)} armor items...")
    
    for armor in armor_items:
        print(f"  Looking up: {armor['gear_name']}")
        
        # Search gear tables
        gear_data = search_gear(cursor, armor['gear_name'])
        
        if gear_data:
            # Update armor with found stats
            updates = []
            values = []
            
            if gear_data.get('ballistic') and not armor['ballistic_rating']:
                updates.append("ballistic_rating = %s")
                values.append(gear_data['ballistic'])
                print(f"    Found ballistic: {gear_data['ballistic']}")
            
            if gear_data.get('impact') and not armor['impact_rating']:
                updates.append("impact_rating = %s")
                values.append(gear_data['impact'])
                print(f"    Found impact: {gear_data['impact']}")
            
            if gear_data.get('conceal') and not armor['conceal']:
                updates.append("conceal = %s")
                values.append(gear_data['conceal'])
                print(f"    Found conceal: {gear_data['conceal']}")
            
            if updates:
                values.append(armor['id'])
                cursor.execute(f"""
                    UPDATE character_gear
                    SET {', '.join(updates)}
                    WHERE id = %s
                """, values)
        else:
            print(f"    Not found in gear tables")
    
    conn.commit()
    print("  ✓ Armor enriched")

def enrich_cyberware(conn):
    """Enrich cyberware data from gear tables"""
    cursor = conn.cursor()
    
    # Get all cyberware
    cursor.execute("""
        SELECT id, source, essence_cost, modifier_data
        FROM character_modifiers
        WHERE source_type = 'cyberware'
    """)
    
    cyberware_items = cursor.fetchall()
    print(f"\nEnriching {len(cyberware_items)} cyberware items...")
    
    for cyber in cyberware_items:
        print(f"  Looking up: {cyber['source']}")
        
        # Search gear tables
        gear_data = search_gear(cursor, cyber['source'])
        
        if gear_data:
            # Update cyberware with found stats
            modifier_data = cyber['modifier_data'] or {}
            updated = False
            
            if gear_data.get('cost'):
                modifier_data['cost'] = gear_data['cost']
                print(f"    Found cost: {gear_data['cost']}¥")
                updated = True
            
            if gear_data.get('essence'):
                modifier_data['essence_cost'] = gear_data['essence']
                print(f"    Found essence: {gear_data['essence']}")
                updated = True
            
            if updated and modifier_data != cyber['modifier_data']:
                cursor.execute("""
                    UPDATE character_modifiers
                    SET modifier_data = %s
                    WHERE id = %s
                """, (psycopg.types.json.Jsonb(modifier_data), cyber['id']))
        else:
            print(f"    Not found in gear tables")
    
    conn.commit()
    print("  ✓ Cyberware enriched")

def main():
    """Main enrichment process"""
    print("=" * 70)
    print("ENRICHING CHARACTER DATA FROM RAG DATABASE")
    print("=" * 70)
    
    # Connect to database
    conn = psycopg.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB'),
        row_factory=dict_row
    )
    
    try:
        enrich_weapons(conn)
        enrich_armor(conn)
        enrich_cyberware(conn)
        
        print("\n" + "=" * 70)
        print("✓ Enrichment complete!")
        print("=" * 70)
        
    finally:
        conn.close()

if __name__ == "__main__":
    main()
