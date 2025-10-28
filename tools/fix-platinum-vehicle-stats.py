#!/usr/bin/env python3
"""Fix Platinum's vehicle stats by parsing notes into proper columns"""
import os
import re
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

# Get character ID
cur.execute("""
    SELECT id FROM characters WHERE street_name = 'Platinum'
""")
char = cur.fetchone()

if not char:
    print("Platinum not found!")
    conn.close()
    exit(1)

char_id = char['id']

# Get vehicles
cur.execute("""
    SELECT id, vehicle_name, notes 
    FROM character_vehicles 
    WHERE character_id = %s
""", (char_id,))

vehicles = cur.fetchall()

for vehicle in vehicles:
    notes = vehicle['notes'] or ''
    print(f"\nProcessing: {vehicle['vehicle_name']}")
    print(f"Notes: {notes}")
    
    # Parse stats from notes
    handling = None
    speed = None
    body = None
    armor = None
    signature = None
    pilot = None
    modifications = None
    
    # Extract Handling (e.g., "Handling: 3/8")
    handling_match = re.search(r'Handling:\s*(\d+/\d+)', notes)
    if handling_match:
        handling = handling_match.group(1)
    
    # Extract Speed (e.g., "Speed: 210")
    speed_match = re.search(r'Speed:\s*(\d+)', notes)
    if speed_match:
        speed = int(speed_match.group(1))
    
    # Extract Body (e.g., "Body: 8")
    body_match = re.search(r'Body:\s*(\d+)', notes)
    if body_match:
        body = int(body_match.group(1))
    
    # Extract Armor (e.g., "Armor: 2")
    armor_match = re.search(r'Armor:\s*(\d+)', notes)
    if armor_match:
        armor = int(armor_match.group(1))
    
    # Extract Signature (e.g., "Signature: N/A" or "Signature: 2")
    signature_match = re.search(r'Signature:\s*(.+?)(?:\n|$)', notes)
    if signature_match:
        sig_value = signature_match.group(1).strip()
        signature = None if sig_value.upper() == 'N/A' else sig_value
    
    # Extract Pilot (e.g., "Pilot: N/A" or "Pilot: 3")
    pilot_match = re.search(r'Pilot:\s*(.+?)(?:\n|$)', notes)
    if pilot_match:
        pilot_value = pilot_match.group(1).strip()
        pilot = None if pilot_value.upper() == 'N/A' else pilot_value
    
    # Extract Modifications (e.g., "Modifications: N/A" or "Modifications: Smartlink")
    mods_match = re.search(r'Modifications:\s*(.+?)(?:\n|$)', notes)
    if mods_match:
        mods_value = mods_match.group(1).strip()
        modifications = None if mods_value.upper() == 'N/A' else mods_value
    
    print(f"  Parsed - Handling: {handling}, Speed: {speed}, Body: {body}, Armor: {armor}")
    print(f"           Signature: {signature}, Pilot: {pilot}, Modifications: {modifications}")
    
    # Update vehicle with parsed stats
    cur.execute("""
        UPDATE character_vehicles
        SET handling = %s,
            speed = %s,
            body = %s,
            armor = %s,
            signature = %s,
            pilot = %s,
            modifications = %s
        WHERE id = %s
    """, (handling, speed, body, armor, signature, pilot, modifications, vehicle['id']))
    
    print(f"  ✓ Updated {vehicle['vehicle_name']}")

conn.commit()
print(f"\n✓ Updated {len(vehicles)} vehicle(s)")

# Verify
cur.execute("""
    SELECT vehicle_name, handling, speed, body, armor
    FROM character_vehicles 
    WHERE character_id = %s
""", (char_id,))

print("\nVerification:")
for v in cur.fetchall():
    print(f"  {v['vehicle_name']}: Handling={v['handling']}, Speed={v['speed']}, Body={v['body']}, Armor={v['armor']}")

conn.close()
