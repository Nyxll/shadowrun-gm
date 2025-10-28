#!/usr/bin/env python3
"""
Enrich character data from database tables (qualities, gear, spells, etc.)
Then export enriched data back to v1 markdown files
"""
import os
import json
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row

load_dotenv()

def enrich_edges_flaws(conn):
    """Enrich edges and flaws with data from qualities table"""
    cursor = conn.cursor()
    
    print("\n" + "="*70)
    print("ENRICHING EDGES AND FLAWS")
    print("="*70)
    
    # Get all edges/flaws
    cursor.execute("""
        SELECT ef.id, ef.character_id, ef.name, ef.type, ef.description,
               c.name as character_name
        FROM character_edges_flaws ef
        JOIN characters c ON c.id = ef.character_id
        ORDER BY c.name, ef.type, ef.name
    """)
    
    edges_flaws = cursor.fetchall()
    enriched_count = 0
    
    for ef in edges_flaws:
        # Search qualities table
        cursor.execute("""
            SELECT name, quality_type, cost, game_effects, description, game_notes
            FROM qualities
            WHERE LOWER(name) = LOWER(%s)
            OR LOWER(name) LIKE LOWER(%s)
            LIMIT 1
        """, (ef['name'], f"%{ef['name']}%"))
        
        quality = cursor.fetchone()
        
        if quality:
            print(f"\n{ef['character_name']} - {ef['type'].upper()}: {ef['name']}")
            
            # Build enriched description
            enriched_desc = ef['description'] or ''
            
            if quality['description'] and quality['description'] not in (enriched_desc or ''):
                if enriched_desc and enriched_desc != 'N/A':
                    enriched_desc += f"\n\n{quality['description']}"
                else:
                    enriched_desc = quality['description']
                print(f"  + Added description from qualities table")
            
            if quality['game_notes']:
                if enriched_desc and enriched_desc != 'N/A':
                    enriched_desc += f"\n\nGame Notes: {quality['game_notes']}"
                else:
                    enriched_desc = f"Game Notes: {quality['game_notes']}"
                print(f"  + Added game notes")
            
            if quality['game_effects']:
                effects_str = json.dumps(quality['game_effects'], indent=2)
                if enriched_desc and enriched_desc != 'N/A':
                    enriched_desc += f"\n\nGame Effects: {effects_str}"
                else:
                    enriched_desc = f"Game Effects: {effects_str}"
                print(f"  + Added game effects")
            
            # Update database
            cursor.execute("""
                UPDATE character_edges_flaws
                SET description = %s
                WHERE id = %s
            """, (enriched_desc, ef['id']))
            
            enriched_count += 1
        else:
            print(f"\n{ef['character_name']} - {ef['type'].upper()}: {ef['name']} - Not found in qualities table")
    
    conn.commit()
    print(f"\n✓ Enriched {enriched_count} edges/flaws")

def enrich_gear(conn):
    """Enrich gear (weapons/armor) with data from gear tables"""
    cursor = conn.cursor()
    
    print("\n" + "="*70)
    print("ENRICHING GEAR (WEAPONS & ARMOR)")
    print("="*70)
    
    # Get all gear
    cursor.execute("""
        SELECT g.id, g.character_id, g.gear_name, g.gear_type,
               g.damage, g.conceal, g.ammo_capacity,
               g.ballistic_rating, g.impact_rating,
               c.name as character_name
        FROM character_gear g
        JOIN characters c ON c.id = g.character_id
        ORDER BY c.name, g.gear_type, g.gear_name
    """)
    
    gear_items = cursor.fetchall()
    enriched_count = 0
    
    for item in gear_items:
        # Search gear table
        cursor.execute("""
            SELECT name, category, subcategory, base_stats, description, game_notes, cost
            FROM gear
            WHERE LOWER(name) = LOWER(%s)
            OR LOWER(name) LIKE LOWER(%s)
            LIMIT 1
        """, (item['gear_name'], f"%{item['gear_name']}%"))
        
        gear_data = cursor.fetchone()
        
        if gear_data:
            print(f"\n{item['character_name']} - {item['gear_type'].upper()}: {item['gear_name']}")
            
            updates = []
            values = []
            
            # Extract stats from base_stats JSONB
            if gear_data['base_stats']:
                stats = gear_data['base_stats']
                
                if item['gear_type'] == 'weapon':
                    if stats.get('damage') and not item['damage']:
                        updates.append("damage = %s")
                        values.append(stats['damage'])
                        print(f"  + damage: {stats['damage']}")
                    
                    if stats.get('conceal') and not item['conceal']:
                        updates.append("conceal = %s")
                        values.append(str(stats['conceal']))
                        print(f"  + conceal: {stats['conceal']}")
                    
                    if stats.get('ammo') and not item['ammo_capacity']:
                        updates.append("ammo_capacity = %s")
                        values.append(stats['ammo'])
                        print(f"  + ammo: {stats['ammo']}")
                
                elif item['gear_type'] == 'armor':
                    if stats.get('ballistic') and not item['ballistic_rating']:
                        updates.append("ballistic_rating = %s")
                        values.append(stats['ballistic'])
                        print(f"  + ballistic: {stats['ballistic']}")
                    
                    if stats.get('impact') and not item['impact_rating']:
                        updates.append("impact_rating = %s")
                        values.append(stats['impact'])
                        print(f"  + impact: {stats['impact']}")
                    
                    if stats.get('conceal') and not item['conceal']:
                        updates.append("conceal = %s")
                        values.append(str(stats['conceal']))
                        print(f"  + conceal: {stats['conceal']}")
            
            if updates:
                values.append(item['id'])
                cursor.execute(f"""
                    UPDATE character_gear
                    SET {', '.join(updates)}
                    WHERE id = %s
                """, values)
                enriched_count += 1
    
    conn.commit()
    print(f"\n✓ Enriched {enriched_count} gear items")

def enrich_cyberware_bioware(conn):
    """Enrich cyberware/bioware with data from gear tables"""
    cursor = conn.cursor()
    
    print("\n" + "="*70)
    print("ENRICHING CYBERWARE & BIOWARE")
    print("="*70)
    
    # Get all cyberware/bioware
    cursor.execute("""
        SELECT m.id, m.character_id, m.source, m.source_type,
               m.essence_cost, m.modifier_data,
               c.name as character_name
        FROM character_modifiers m
        JOIN characters c ON c.id = m.character_id
        WHERE m.source_type IN ('cyberware', 'bioware')
        ORDER BY c.name, m.source_type, m.source
    """)
    
    modifiers = cursor.fetchall()
    enriched_count = 0
    
    for mod in modifiers:
        # Search gear table for cyberware/bioware
        cursor.execute("""
            SELECT name, category, subcategory, base_stats, description, game_notes, cost
            FROM gear
            WHERE (category = 'cyberware' OR category = 'bioware')
            AND (LOWER(name) = LOWER(%s) OR LOWER(name) LIKE LOWER(%s))
            LIMIT 1
        """, (mod['source'], f"%{mod['source']}%"))
        
        gear_data = cursor.fetchone()
        
        if gear_data:
            print(f"\n{mod['character_name']} - {mod['source_type'].upper()}: {mod['source']}")
            
            modifier_data = mod['modifier_data'] or {}
            updated = False
            
            if gear_data['cost'] and 'cost' not in modifier_data:
                modifier_data['cost'] = gear_data['cost']
                print(f"  + cost: {gear_data['cost']}¥")
                updated = True
            
            if gear_data['description'] and 'description' not in modifier_data:
                modifier_data['description'] = gear_data['description']
                print(f"  + description added")
                updated = True
            
            if gear_data['base_stats']:
                if 'stats' not in modifier_data:
                    modifier_data['stats'] = gear_data['base_stats']
                    print(f"  + stats added")
                    updated = True
            
            if updated:
                cursor.execute("""
                    UPDATE character_modifiers
                    SET modifier_data = %s
                    WHERE id = %s
                """, (psycopg.types.json.Jsonb(modifier_data), mod['id']))
                enriched_count += 1
    
    conn.commit()
    print(f"\n✓ Enriched {enriched_count} cyberware/bioware items")

def main():
    """Main enrichment process"""
    print("="*70)
    print("ENRICHING CHARACTER DATA FROM DATABASE TABLES")
    print("="*70)
    
    conn = psycopg.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB'),
        row_factory=dict_row
    )
    
    try:
        enrich_edges_flaws(conn)
        enrich_gear(conn)
        enrich_cyberware_bioware(conn)
        
        print("\n" + "="*70)
        print("✓ ENRICHMENT COMPLETE!")
        print("="*70)
        print("\nNext step: Run export script to create v1 markdown files")
        
    finally:
        conn.close()

if __name__ == "__main__":
    main()
