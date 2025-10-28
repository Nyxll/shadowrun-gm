#!/usr/bin/env python3
"""
Export enriched character data to v1 markdown files
"""
import os
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row

load_dotenv()

def export_character(cursor, character_name):
    """Export a single character to v1 markdown format"""
    
    # Get character basic info
    cursor.execute("""
        SELECT * FROM characters WHERE name = %s
    """, (character_name,))
    char = cursor.fetchone()
    
    if not char:
        print(f"Character '{character_name}' not found")
        return None
    
    md = []
    md.append(f"# {char['name']}")
    if char.get('real_name'):
        md.append(f"**Real Name:** {char['real_name']}")
    md.append("")
    
    # Basic Info
    md.append("## Basic Information")
    md.append(f"- **Metatype:** {char.get('metatype') or 'Unknown'}")
    md.append(f"- **Archetype:** {char.get('archetype') or 'Unknown'}")
    if char.get('age'):
        md.append(f"- **Age:** {char['age']}")
    if char.get('sex'):
        md.append(f"- **Sex:** {char['sex']}")
    if char.get('height'):
        md.append(f"- **Height:** {char['height']}")
    if char.get('weight'):
        md.append(f"- **Weight:** {char['weight']}")
    md.append("")
    
    # Attributes
    md.append("## Attributes")
    attrs = ['body', 'quickness', 'strength', 'charisma', 'intelligence', 'willpower', 'essence', 'magic', 'reaction']
    for attr in attrs:
        val = char.get(attr)
        if val is not None:
            md.append(f"- **{attr.title()}:** {val}")
    md.append("")
    
    # Derived Stats
    md.append("## Derived Statistics")
    if char.get('initiative'):
        md.append(f"- **Initiative:** {char['initiative']}")
    if char.get('combat_pool'):
        md.append(f"- **Combat Pool:** {char['combat_pool']}")
    if char.get('karma_pool'):
        md.append(f"- **Karma Pool:** {char['karma_pool']}")
    md.append("")
    
    # Condition Monitor
    if char.get('physical_damage') or char.get('stun_damage'):
        md.append("## Condition Monitor")
        if char.get('physical_damage'):
            md.append(f"- **Physical:** {char['physical_damage']}")
        if char.get('stun_damage'):
            md.append(f"- **Stun:** {char['stun_damage']}")
        md.append("")
    
    # Skills
    cursor.execute("""
        SELECT skill_name, current_rating, specialization
        FROM character_skills
        WHERE character_id = %s
        ORDER BY skill_name
    """, (char['id'],))
    skills = cursor.fetchall()
    
    if skills:
        md.append("## Skills")
        for skill in skills:
            spec = f" ({skill['specialization']})" if skill['specialization'] else ""
            md.append(f"- **{skill['skill_name']}:** {skill['current_rating']}{spec}")
        md.append("")
    
    # Edges
    cursor.execute("""
        SELECT name, description
        FROM character_edges_flaws
        WHERE character_id = %s AND type = 'edge'
        ORDER BY name
    """, (char['id'],))
    edges = cursor.fetchall()
    
    if edges:
        md.append("## Edges")
        for edge in edges:
            md.append(f"- **{edge['name']}:** {edge['description'] or 'N/A'}")
        md.append("")
    
    # Flaws
    cursor.execute("""
        SELECT name, description
        FROM character_edges_flaws
        WHERE character_id = %s AND type = 'flaw'
        ORDER BY name
    """, (char['id'],))
    flaws = cursor.fetchall()
    
    if flaws:
        md.append("## Flaws")
        for flaw in flaws:
            md.append(f"- **{flaw['name']}:** {flaw['description'] or 'N/A'}")
        md.append("")
    
    # Cyberware
    cursor.execute("""
        SELECT source, essence_cost, modifier_data
        FROM character_modifiers
        WHERE character_id = %s AND source_type = 'cyberware'
        ORDER BY source
    """, (char['id'],))
    cyberware = cursor.fetchall()
    
    if cyberware:
        md.append("## Cyberware")
        for cyber in cyberware:
            essence = f" (Essence: {cyber['essence_cost']})" if cyber['essence_cost'] else ""
            md.append(f"- **{cyber['source']}**{essence}")
            if cyber['modifier_data']:
                data = cyber['modifier_data']
                if data.get('description'):
                    md.append(f"  - {data['description']}")
                if data.get('cost'):
                    md.append(f"  - Cost: {data['cost']}¥")
        md.append("")
    
    # Bioware
    cursor.execute("""
        SELECT source, essence_cost, modifier_data
        FROM character_modifiers
        WHERE character_id = %s AND source_type = 'bioware'
        ORDER BY source
    """, (char['id'],))
    bioware = cursor.fetchall()
    
    if bioware:
        md.append("## Bioware")
        for bio in bioware:
            essence = f" (Essence: {bio['essence_cost']})" if bio['essence_cost'] else ""
            md.append(f"- **{bio['source']}**{essence}")
            if bio['modifier_data'] and bio['modifier_data'].get('description'):
                md.append(f"  - {bio['modifier_data']['description']}")
        md.append("")
    
    # Weapons
    cursor.execute("""
        SELECT gear_name, damage, conceal, ammo_capacity, notes
        FROM character_gear
        WHERE character_id = %s AND gear_type = 'weapon'
        ORDER BY gear_name
    """, (char['id'],))
    weapons = cursor.fetchall()
    
    if weapons:
        md.append("## Weapons")
        for weapon in weapons:
            parts = [f"**{weapon['gear_name']}**"]
            if weapon['damage']:
                parts.append(f"Damage: {weapon['damage']}")
            if weapon['conceal']:
                parts.append(f"Conceal: {weapon['conceal']}")
            if weapon['ammo_capacity']:
                parts.append(f"Ammo: {weapon['ammo_capacity']}")
            md.append(f"- {', '.join(parts)}")
            if weapon['notes']:
                md.append(f"  - {weapon['notes']}")
        md.append("")
    
    # Armor
    cursor.execute("""
        SELECT gear_name, ballistic_rating, impact_rating, conceal, notes
        FROM character_gear
        WHERE character_id = %s AND gear_type = 'armor'
        ORDER BY gear_name
    """, (char['id'],))
    armor = cursor.fetchall()
    
    if armor:
        md.append("## Armor")
        for item in armor:
            parts = [f"**{item['gear_name']}**"]
            if item['ballistic_rating'] or item['impact_rating']:
                b = item['ballistic_rating'] or 0
                i = item['impact_rating'] or 0
                parts.append(f"Rating: {b}/{i}")
            if item['conceal']:
                parts.append(f"Conceal: {item['conceal']}")
            md.append(f"- {', '.join(parts)}")
            if item['notes']:
                md.append(f"  - {item['notes']}")
        md.append("")
    
    # Contacts
    cursor.execute("""
        SELECT *
        FROM character_contacts
        WHERE character_id = %s
        ORDER BY name
    """, (char['id'],))
    contacts = cursor.fetchall()
    
    if contacts:
        md.append("## Contacts")
        for contact in contacts:
            parts = [f"**{contact['name']}**"]
            if contact.get('contact_role'):
                parts.append(contact['contact_role'])
            if contact.get('loyalty') or contact.get('connection'):
                l = contact.get('loyalty') or 0
                c = contact.get('connection') or 0
                parts.append(f"(Loyalty: {l}, Connection: {c})")
            md.append(f"- {', '.join(parts)}")
            if contact.get('notes'):
                md.append(f"  - {contact['notes']}")
        md.append("")
    
    # Vehicles
    cursor.execute("""
        SELECT *
        FROM character_vehicles
        WHERE character_id = %s
        ORDER BY id
    """, (char['id'],))
    vehicles = cursor.fetchall()
    
    if vehicles:
        md.append("## Vehicles")
        for vehicle in vehicles:
            v_name = vehicle.get('name') or vehicle.get('vehicle_name') or 'Unknown Vehicle'
            md.append(f"- **{v_name}** ({vehicle.get('vehicle_type') or 'Vehicle'})")
            stats = []
            if vehicle.get('handling'):
                stats.append(f"Handling: {vehicle['handling']}")
            if vehicle.get('speed'):
                stats.append(f"Speed: {vehicle['speed']}")
            if vehicle.get('body'):
                stats.append(f"Body: {vehicle['body']}")
            if vehicle.get('armor'):
                stats.append(f"Armor: {vehicle['armor']}")
            if stats:
                md.append(f"  - {', '.join(stats)}")
            if vehicle.get('notes'):
                md.append(f"  - {vehicle['notes']}")
        md.append("")
    
    # Background
    if char.get('background'):
        md.append("## Background")
        md.append(char['background'])
        md.append("")
    
    return '\n'.join(md)

def main():
    """Export all characters to v1 markdown files"""
    print("="*70)
    print("EXPORTING ENRICHED CHARACTERS TO V1 MARKDOWN")
    print("="*70)
    
    conn = psycopg.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB'),
        row_factory=dict_row
    )
    
    cursor = conn.cursor()
    
    # Get all character names
    cursor.execute("SELECT name FROM characters ORDER BY name")
    characters = cursor.fetchall()
    
    # Create v1 directory if it doesn't exist
    v1_dir = "characters/v1"
    os.makedirs(v1_dir, exist_ok=True)
    
    for char in characters:
        char_name = char['name']
        print(f"\nExporting {char_name}...")
        
        markdown = export_character(cursor, char_name)
        
        if markdown:
            filename = f"{v1_dir}/{char_name}.md"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(markdown)
            print(f"  ✓ Saved to {filename}")
    
    conn.close()
    
    print("\n" + "="*70)
    print("✓ EXPORT COMPLETE!")
    print("="*70)
    print(f"\nEnriched character sheets saved to {v1_dir}/")

if __name__ == "__main__":
    main()
