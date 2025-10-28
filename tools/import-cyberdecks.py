#!/usr/bin/env python3
"""Import cyberdeck data from character_gear notes into character_cyberdecks table"""
import os
import re
import json
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=os.getenv('POSTGRES_PORT'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    dbname=os.getenv('POSTGRES_DB'),
    cursor_factory=RealDictCursor
)

cur = conn.cursor()

# Apply migration
print("Applying migration...")
with open('migrations/013_add_cyberdecks_table.sql', 'r') as f:
    cur.execute(f.read())
conn.commit()
print("✓ Migration applied\n")

# Get all cyberdeck gear items
cur.execute("""
    SELECT 
        cg.id,
        cg.character_id,
        cg.gear_name,
        cg.notes,
        c.street_name
    FROM character_gear cg
    JOIN characters c ON c.id = cg.character_id
    WHERE LOWER(cg.gear_name) LIKE '%cyberdeck%'
      AND cg.gear_name NOT LIKE '%Parts%'
    ORDER BY c.street_name, cg.gear_name
""")

cyberdecks = cur.fetchall()

print(f"Found {len(cyberdecks)} cyberdeck(s) to import\n")

for deck_gear in cyberdecks:
    print(f"Processing: {deck_gear['gear_name']} ({deck_gear['street_name']})")
    
    notes = deck_gear['notes'] or ''
    
    # Extract deck name from gear_name (remove quotes)
    deck_name = deck_gear['gear_name'].replace('"', '')
    
    # Parse stats from notes
    mpcp = None
    hardening = None
    memory = None
    storage = None
    io_speed = None
    response_increase = None
    persona_programs = {}
    utilities = {}
    ai_companions = []
    
    # Extract MPCP
    mpcp_match = re.search(r'MPCP:\s*(\d+)', notes)
    if mpcp_match:
        mpcp = int(mpcp_match.group(1))
    
    # Extract Hardening
    hardening_match = re.search(r'Hardening:\s*(\d+)', notes)
    if hardening_match:
        hardening = int(hardening_match.group(1))
    
    # Extract Memory
    memory_match = re.search(r'Memory:\s*(\d+)\s*MP', notes)
    if memory_match:
        memory = int(memory_match.group(1))
    
    # Extract Storage
    storage_match = re.search(r'Storage:\s*(\d+)\s*MP', notes)
    if storage_match:
        storage = int(storage_match.group(1))
    
    # Extract I/O Speed
    io_match = re.search(r'I/O Speed:\s*(\d+)', notes)
    if io_match:
        io_speed = int(io_match.group(1))
    
    # Extract Response Increase
    response_match = re.search(r'Response Increase:\s*\+?(\d+)', notes)
    if response_match:
        response_increase = int(response_match.group(1))
    
    # Extract Persona Programs (Bod, Evasion, Masking, Sensor)
    persona_match = re.search(r'Persona Programs:\s*(.+?)(?:\n|$)', notes)
    if persona_match:
        persona_text = persona_match.group(1)
        
        # Parse individual programs
        bod_match = re.search(r'Bod\s+(\d+)', persona_text)
        if bod_match:
            persona_programs['bod'] = int(bod_match.group(1))
        
        evasion_match = re.search(r'Evasion\s+(\d+)', persona_text)
        if evasion_match:
            persona_programs['evasion'] = int(evasion_match.group(1))
        
        masking_match = re.search(r'Masking\s+(\d+)(?:\s*\(effective\s+(\d+)\))?', persona_text)
        if masking_match:
            persona_programs['masking'] = int(masking_match.group(1))
            if masking_match.group(2):
                persona_programs['masking_effective'] = int(masking_match.group(2))
        
        sensor_match = re.search(r'Sensor\s+(\d+)', persona_text)
        if sensor_match:
            persona_programs['sensor'] = int(sensor_match.group(1))
    
    # Extract Utilities
    utilities_match = re.search(r'Utilities:\s*(.+?)(?:\n|$)', notes)
    if utilities_match:
        util_text = utilities_match.group(1)
        
        # Parse utility descriptions
        # Example: "Masking Boost 4 dice (persistent), Utility Creation 5 dice"
        masking_boost_match = re.search(r'Masking Boost\s+(\d+)\s+dice', util_text)
        if masking_boost_match:
            utilities['masking_boost'] = {
                'dice': int(masking_boost_match.group(1)),
                'persistent': 'persistent' in util_text.lower()
            }
        
        util_creation_match = re.search(r'Utility Creation\s+(\d+)\s+dice', util_text)
        if util_creation_match:
            utilities['utility_creation'] = {
                'dice': int(util_creation_match.group(1))
            }
        
        sandbox_match = re.search(r'Virtual sandbox Rating\s+(\d+)', util_text)
        if sandbox_match:
            utilities['virtual_sandbox'] = {
                'rating': int(sandbox_match.group(1))
            }
    
    # Extract AI Companions
    ai_match = re.search(r'AI Companions:\s*(.+?)(?:\n|$)', notes)
    if ai_match:
        ai_text = ai_match.group(1)
        ai_companions.append(ai_text.strip())
    
    # Also check for ARESIA AI in persona programs
    if 'ARESIA' in notes:
        if 'ARESIA' not in str(ai_companions):
            ai_companions.append('ARESIA AI (excels at decryption/IC countermeasures)')
    
    print(f"  MPCP: {mpcp}, Hardening: {hardening}, Memory: {memory} MP")
    print(f"  Persona: {persona_programs}")
    print(f"  Utilities: {utilities}")
    if ai_companions:
        print(f"  AI Companions: {ai_companions}")
    
    # Insert into character_cyberdecks
    cur.execute("""
        INSERT INTO character_cyberdecks (
            character_id, deck_name, mpcp, hardening, memory, storage,
            io_speed, response_increase, persona_programs, utilities, ai_companions, notes
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        deck_gear['character_id'],
        deck_name,
        mpcp,
        hardening,
        memory,
        storage,
        io_speed,
        response_increase,
        json.dumps(persona_programs),
        json.dumps(utilities),
        json.dumps(ai_companions),
        notes
    ))
    
    print(f"  ✓ Imported\n")

conn.commit()

# Verify
cur.execute("""
    SELECT 
        c.street_name,
        cd.deck_name,
        cd.mpcp,
        cd.hardening,
        cd.memory
    FROM character_cyberdecks cd
    JOIN characters c ON c.id = cd.character_id
    ORDER BY c.street_name, cd.deck_name
""")

print("Verification:")
for row in cur.fetchall():
    print(f"  {row['street_name']}: {row['deck_name']} (MPCP {row['mpcp']}, {row['memory']} MP)")

conn.close()
print("\n✓ Import complete")
