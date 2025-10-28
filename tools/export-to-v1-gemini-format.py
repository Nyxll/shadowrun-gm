#!/usr/bin/env python3
"""
Export enriched character data to v1 markdown files following GEMINI-CHARACTER-SHEET-PROMPT.md format
"""
import os
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row

load_dotenv()

def export_character(cursor, character_name):
    """Export a single character to GEMINI markdown format"""
    
    # Get character basic info
    cursor.execute("""
        SELECT * FROM characters WHERE name = %s
    """, (character_name,))
    char = cursor.fetchone()
    
    if not char:
        print(f"Character '{character_name}' not found")
        return None
    
    md = []
    
    # Title with street name
    street_name = char.get('street_name') or char['name']
    real_name = char.get('real_name') or char['name']
    md.append(f"# {real_name} ({street_name})")
    md.append("")
    
    # Basic Information
    md.append("## Basic Information")
    md.append(f"- **Name**: {real_name} ")
    md.append(f"- **Street Name**: {street_name} ")
    md.append(f"- **Metatype**: {char.get('metatype') or 'Human'} ")
    md.append(f"- **Archetype**: {char.get('archetype') or 'Unknown'} ")
    md.append(f"- **Sex**: {char.get('sex') or 'N/A'} ")
    md.append(f"- **Age**: {char.get('age') or 'N/A'}")
    md.append(f"- **Height**: {char.get('height') or 'N/A'} ")
    md.append(f"- **Weight**: {char.get('weight') or 'N/A'} ")
    md.append(f"- **Hair**: {char.get('hair') or 'N/A'} ")
    md.append(f"- **Eyes**: {char.get('eyes') or 'N/A'} ")
    md.append(f"- **Skin**: {char.get('skin') or 'N/A'}")
    md.append("")
    md.append("---")
    md.append("")
    
    # Attributes
    md.append("## Attributes")
    md.append("### Base Form")
    # Use current_ values which include augmentations
    attrs = {
        'Body': char.get('current_body'),
        'Quickness': char.get('current_quickness'),
        'Strength': char.get('current_strength'),
        'Charisma': char.get('current_charisma'),
        'Intelligence': char.get('current_intelligence'),
        'Willpower': char.get('current_willpower'),
        'Essence': char.get('current_essence'),
        'Magic': char.get('current_magic'),
        'Reaction': char.get('current_reaction')
    }
    for attr_name, val in attrs.items():
        if val is not None:
            md.append(f"- **{attr_name}**: {val} ")
        else:
            md.append(f"- **{attr_name}**: N/A")
    md.append("")
    
    # Animal Form (always include for consistency)
    md.append("### Animal Form (Shapeshifters Only)")
    md.append("- **Form**: N/A")
    md.append("- **Body**: N/A")
    md.append("- **Quickness**: N/A")
    md.append("- **Strength**: N/A")
    md.append("- **Charisma**: N/A")
    md.append("- **Intelligence**: N/A")
    md.append("- **Willpower**: N/A")
    md.append("- **Essence**: N/A")
    md.append("- **Magic**: N/A")
    md.append("- **Reaction**: N/A")
    md.append("- **Special Abilities**: N/A")
    md.append("")
    md.append("---")
    md.append("")
    
    # Derived Stats
    md.append("## Derived Stats")
    md.append(f"- **Initiative**: {char.get('initiative') or 'N/A'} ")
    md.append(f"- **Combat Pool**: {char.get('combat_pool') or 'N/A'} ")
    md.append(f"- **Karma Pool**: {char.get('karma_pool') or 'N/A'} ")
    md.append(f"- **Total Karma Earned**: {char.get('karma_total') or 'N/A'} ")
    md.append(f"- **Total Karma Available**: {char.get('karma_available') or 'N/A'} ")
    
    # Format nuyen with ¥ symbol if present
    nuyen = char.get('nuyen')
    if nuyen is not None:
        md.append(f"- **Nuyen**: {nuyen}¥ ")
    else:
        md.append(f"- **Nuyen**: N/A ")
    
    # Format lifestyle with cost and months if available
    lifestyle = char.get('lifestyle')
    lifestyle_cost = char.get('lifestyle_cost')
    lifestyle_months = char.get('lifestyle_months_prepaid')
    if lifestyle:
        if lifestyle_cost and lifestyle_months:
            md.append(f"- **Lifestyle**: {lifestyle} ({lifestyle_cost}¥/month, {lifestyle_months} month prepaid) ")
        else:
            md.append(f"- **Lifestyle**: {lifestyle} ")
    else:
        md.append(f"- **Lifestyle**: N/A ")
    
    md.append(f"- **Essence Hole**: {char.get('essence_hole') or 'N/A'}")
    md.append("")
    md.append("---")
    md.append("")
    
    # Edges and Flaws
    md.append("## Edges and Flaws (if using Shadowrun Companion)")
    
    # Edges
    cursor.execute("""
        SELECT name, description
        FROM character_edges_flaws
        WHERE character_id = %s AND type = 'edge'
        ORDER BY name
    """, (char['id'],))
    edges = cursor.fetchall()
    
    md.append("### Edges")
    if edges:
        for edge in edges:
            desc = edge['description'] if edge['description'] and edge['description'] != 'N/A' else 'N/A'
            md.append(f"- **{edge['name']}**: {desc} ")
    else:
        md.append("- **None**")
    md.append("")
    
    # Flaws
    cursor.execute("""
        SELECT name, description
        FROM character_edges_flaws
        WHERE character_id = %s AND type = 'flaw'
        ORDER BY name
    """, (char['id'],))
    flaws = cursor.fetchall()
    
    md.append("### Flaws")
    if flaws:
        for flaw in flaws:
            desc = flaw['description'] if flaw['description'] and flaw['description'] != 'N/A' else 'N/A'
            md.append(f"- **{flaw['name']}**: {desc} ")
    else:
        md.append("- **None**")
    md.append("")
    md.append("---")
    md.append("")
    
    # Decker Stats
    md.append("## Decker Stats (if applicable)")
    md.append("- **Body Index**: N/A")
    md.append("- **Task Pool**: N/A")
    md.append("- **Hacking Pool**: N/A")
    md.append("- **Matrix Initiative**: N/A")
    md.append("")
    md.append("---")
    md.append("")
    
    # Mage Stats
    md.append("## Mage Stats (if applicable)")
    md.append("- **Magic Pool**: N/A")
    md.append("- **Spell Pool**: N/A")
    md.append("- **Initiate Level**: None")
    md.append("- **Metamagics**: None")
    md.append("- **Magical Group/Lodge**: None")
    md.append("- **Tradition**: N/A")
    md.append("")
    md.append("---")
    md.append("")
    
    # Adept Powers
    md.append("## Adept Powers (if applicable)")
    md.append("- **None**")
    md.append("")
    md.append("---")
    md.append("")
    
    # Rigger Stats
    md.append("## Rigger Stats (if applicable)")
    md.append("- **Rigged Reaction**: N/A")
    md.append("- **Rigged Initiative**: N/A")
    md.append("- **Vehicle Control Rig**: N/A")
    md.append("")
    md.append("---")
    md.append("")
    
    # Skills
    md.append("## Skills")
    cursor.execute("""
        SELECT skill_name, current_rating, specialization, skill_type
        FROM character_skills
        WHERE character_id = %s
        ORDER BY skill_type, skill_name
    """, (char['id'],))
    skills = cursor.fetchall()
    
    # Group skills by type
    active_skills = [s for s in skills if s.get('skill_type') == 'active' or not s.get('skill_type')]
    knowledge_skills = [s for s in skills if s.get('skill_type') == 'knowledge']
    language_skills = [s for s in skills if s.get('skill_type') == 'language']
    
    md.append("### Active Skills")
    if active_skills:
        for skill in active_skills:
            spec = f" {skill['specialization']}" if skill.get('specialization') else ""
            md.append(f"- **{skill['skill_name']}**: {skill['current_rating']}{spec} ")
    else:
        md.append("- **None**")
    md.append("")
    
    md.append("### Knowledge Skills")
    if knowledge_skills:
        for skill in knowledge_skills:
            md.append(f"- **{skill['skill_name']}**: {skill['current_rating']} ")
    else:
        md.append("- **None**")
    md.append("")
    
    md.append("### Language Skills")
    if language_skills:
        for skill in language_skills:
            md.append(f"- **{skill['skill_name']}**: {skill['current_rating']} ")
    else:
        md.append("- **None**")
    md.append("")
    md.append("---")
    md.append("")
    
    # Cyberware/Bioware
    md.append("## Cyberware/Bioware")
    
    # Cyberware
    cursor.execute("""
        SELECT source, essence_cost, modifier_data
        FROM character_modifiers
        WHERE character_id = %s AND source_type = 'cyberware'
        ORDER BY source
    """, (char['id'],))
    cyberware = cursor.fetchall()
    
    md.append("### Cyberware")
    if cyberware:
        for cyber in cyberware:
            essence = f" ({cyber['essence_cost']} Essence)" if cyber['essence_cost'] else ""
            md.append(f"- **{cyber['source']}**{essence} ")
            if cyber['modifier_data']:
                data = cyber['modifier_data']
                if data.get('description'):
                    md.append(f"  - {data['description']} ")
                if data.get('stats'):
                    for key, val in data['stats'].items():
                        md.append(f"  - {key}: {val} ")
            md.append("")
    else:
        md.append("- **None**")
        md.append("")
    
    # Bioware
    cursor.execute("""
        SELECT source, essence_cost, modifier_data
        FROM character_modifiers
        WHERE character_id = %s AND source_type = 'bioware'
        ORDER BY source
    """, (char['id'],))
    bioware = cursor.fetchall()
    
    md.append("### Bioware")
    if bioware:
        for bio in bioware:
            essence = f" ({bio['essence_cost']} Body Index)" if bio['essence_cost'] else ""
            md.append(f"- **{bio['source']}**{essence} ")
            if bio['modifier_data'] and bio['modifier_data'].get('description'):
                md.append(f"  - {bio['modifier_data']['description']} ")
            md.append("")
    else:
        md.append("- **None**")
        md.append("")
    
    md.append("---")
    md.append("")
    
    # Gear
    md.append("## Gear")
    
    # Weapons
    cursor.execute("""
        SELECT gear_name, damage, conceal, ammo_capacity, notes
        FROM character_gear
        WHERE character_id = %s AND gear_type = 'weapon'
        ORDER BY gear_name
    """, (char['id'],))
    weapons = cursor.fetchall()
    
    md.append("### Weapons")
    if weapons:
        for weapon in weapons:
            md.append(f"- **{weapon['gear_name']}**")
            md.append(f"  - Type: Weapon ")
            if weapon['damage']:
                md.append(f"  - Damage: {weapon['damage']} ")
            if weapon['conceal']:
                md.append(f"  - Concealability: {weapon['conceal']} ")
            if weapon['ammo_capacity']:
                md.append(f"  - Ammo: {weapon['ammo_capacity']} ")
            if weapon['notes']:
                md.append(f"  - Modifications: {weapon['notes']} ")
            md.append("")
    else:
        md.append("- **None**")
        md.append("")
    
    # Armor
    cursor.execute("""
        SELECT gear_name, ballistic_rating, impact_rating, conceal, notes
        FROM character_gear
        WHERE character_id = %s AND gear_type = 'armor'
        ORDER BY gear_name
    """, (char['id'],))
    armor = cursor.fetchall()
    
    md.append("### Armor")
    if armor:
        for item in armor:
            md.append(f"- **{item['gear_name']}**")
            if item['ballistic_rating'] or item['impact_rating']:
                b = item['ballistic_rating'] or 0
                i = item['impact_rating'] or 0
                md.append(f"  - Rating: {b}/{i} (Ballistic/Impact) ")
            if item['conceal']:
                md.append(f"  - Concealability: {item['conceal']}")
            md.append("")
    else:
        md.append("- **None**")
        md.append("")
    
    md.append("### Equipment")
    md.append("- **None**")
    md.append("")
    
    md.append("### Cyberdecks (for Deckers)")
    md.append("- **None**")
    md.append("")
    
    md.append("### Magical Items (for Mages)")
    md.append("- **None**")
    md.append("")
    
    # Vehicles
    cursor.execute("""
        SELECT *
        FROM character_vehicles
        WHERE character_id = %s
        ORDER BY id
    """, (char['id'],))
    vehicles = cursor.fetchall()
    
    md.append("### Vehicles")
    if vehicles:
        for vehicle in vehicles:
            v_name = vehicle.get('name') or vehicle.get('vehicle_name') or 'Unknown Vehicle'
            md.append(f"- **{v_name}**")
            if vehicle.get('vehicle_type'):
                md.append(f"  - Type: {vehicle['vehicle_type']} ")
            if vehicle.get('handling'):
                md.append(f"  - Handling: {vehicle['handling']} ")
            if vehicle.get('speed'):
                md.append(f"  - Speed: {vehicle['speed']} ")
            if vehicle.get('body'):
                md.append(f"  - Body: {vehicle['body']} ")
            if vehicle.get('armor'):
                md.append(f"  - Armor: {vehicle['armor']} ")
            md.append(f"  - Signature: N/A")
            md.append(f"  - Pilot: N/A")
            md.append(f"  - Modifications: N/A")
            md.append("")
    else:
        md.append("- **None**")
        md.append("")
    
    md.append("---")
    md.append("")
    
    # Magic
    md.append("## Magic (if applicable)")
    md.append("### Spells")
    md.append("- **None**")
    md.append("")
    md.append("### Spell Locks/Quickened Spells")
    md.append("- **None**")
    md.append("")
    md.append("### Spell Formulas (Unlearned)")
    md.append("- **None**")
    md.append("")
    md.append("### Bound Spirits")
    md.append("- **None**")
    md.append("")
    md.append("### Totems/Traditions")
    md.append("- **Totem**: N/A")
    md.append("- **Advantages**: N/A")
    md.append("- **Disadvantages**: N/A")
    md.append("")
    md.append("### Power Sites (if applicable)")
    md.append("- **None**")
    md.append("")
    md.append("---")
    md.append("")
    
    # Contacts
    cursor.execute("""
        SELECT *
        FROM character_contacts
        WHERE character_id = %s
        ORDER BY name
    """, (char['id'],))
    contacts = cursor.fetchall()
    
    md.append("## Contacts")
    if contacts:
        for contact in contacts:
            role = contact.get('contact_role') or 'Contact'
            level = contact.get('loyalty') or contact.get('connection') or 1
            md.append(f"- **{contact['name']}** - {role} ")
            md.append(f"  - Level: {level} ")
            if contact.get('notes'):
                md.append(f"  - Notes: {contact['notes']}")
            else:
                md.append(f"  - Notes: N/A")
    else:
        md.append("- **None**")
    md.append("")
    md.append("---")
    md.append("")
    
    # Background
    md.append("## Background")
    background = char.get('background')
    if background:
        # Remove "- **Concept**:" prefix if it exists in the background field
        if background.startswith('- **Concept**:'):
            background = background.replace('- **Concept**:', '').strip()
        md.append(f"- **Concept**: {background}")
    else:
        md.append("- **Concept**: N/A")
    md.append("")
    md.append("---")
    md.append("")
    
    # Notes
    md.append("## Notes")
    notes = char.get('notes')
    if notes and notes.strip() and notes != '-':
        md.append(notes)
    else:
        md.append("- N/A")
    
    return '\n'.join(md)

def main():
    """Export all characters to v1 markdown files in GEMINI format"""
    print("="*70)
    print("EXPORTING ENRICHED CHARACTERS TO V1 (GEMINI FORMAT)")
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
            # Get street name for filename to match original files
            cursor.execute("SELECT street_name FROM characters WHERE name = %s", (char_name,))
            result = cursor.fetchone()
            street_name = result['street_name'] if result and result['street_name'] else char_name
            
            filename = f"{v1_dir}/{street_name}.md"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(markdown)
            print(f"  ✓ Saved to {filename}")
    
    conn.close()
    
    print("\n" + "="*70)
    print("✓ EXPORT COMPLETE!")
    print("="*70)
    print(f"\nEnriched character sheets saved to {v1_dir}/")
    print("Format: GEMINI-CHARACTER-SHEET-PROMPT.md compliant")

if __name__ == "__main__":
    main()
